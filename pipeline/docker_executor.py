"""
Execute generated code inside an isolated Docker container and collect:
  - execution_success : bool
  - pass_at_1         : bool
  - peak_memory_mb    : float  (measured inside the container)
  - stdout / stderr   : str

Two test-case styles are supported in both languages
---------------------------------------------------
1. **Function-call style** (most tasks)
     input    : list of argument values
     expected : single return value
   The harness calls the function with those args and compares the result.

2. **Eval / class-based style** (LRU Cache, Thread-Safe Counter, …)
     input    : single-element list whose only element is a string of
                semicolon-separated statements; the *last* segment is
                the expression whose value is compared to `expected`.
   Detection: input is a 1-element list of strings containing ';' or 'new '.

Java harness note
-----------------
The task format was updated to use Python-native values for `input`/`expected`
(no more Java literal strings).  `_py_to_java_arg` and `_java_comparison_info`
convert Python values → Java expressions at harness-build time.
"""

import os
import re
import subprocess
import tempfile
import threading
import time
import uuid

import config


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_task(task: dict, code: str) -> dict:
    lang = task["language"]
    if lang == "python":
        return _run_python(task, code)
    elif lang == "java":
        return _run_java(task, code)
    else:
        return _error_result(f"Unsupported language: {lang}")


# ---------------------------------------------------------------------------
# Language runners
# ---------------------------------------------------------------------------

def _run_python(task: dict, code: str) -> dict:
    harness = _build_python_harness(task, code)
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "solution.py"), "w") as fh:
            fh.write(harness)
        container_name = f"eval_{uuid.uuid4().hex[:10]}"
        cmd = [
            "docker", "run", "--rm",
            "--name", container_name,
            "--memory", config.DOCKER_MEMORY_LIMIT,
            "--memory-swap", config.DOCKER_MEMORY_LIMIT,
            "--cpus", config.DOCKER_CPU_LIMIT,
            "--network", "none",
            "-v", f"{tmpdir}:/code:ro",
            config.DOCKER_IMAGES["python"],
            "python", "/code/solution.py",
        ]
        return _execute_container(cmd, container_name, config.EXECUTION_TIMEOUT)


def _run_java(task: dict, code: str) -> dict:
    clean_code = _strip_java_class_wrapper(code)
    harness = _build_java_harness(task, clean_code)
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "Solution.java"), "w") as fh:
            fh.write(harness)
        container_name = f"eval_{uuid.uuid4().hex[:10]}"
        sh_cmd = "cd /code && javac Solution.java 2>&1 && java -cp /code Solution"
        cmd = [
            "docker", "run", "--rm",
            "--name", container_name,
            "--memory", config.DOCKER_MEMORY_LIMIT,
            "--memory-swap", config.DOCKER_MEMORY_LIMIT,
            "--cpus", config.DOCKER_CPU_LIMIT,
            "--network", "none",
            "-v", f"{tmpdir}:/code",
            config.DOCKER_IMAGES["java"],
            "sh", "-c", sh_cmd,
        ]
        return _execute_container(cmd, container_name, config.EXECUTION_TIMEOUT)


# ---------------------------------------------------------------------------
# Container execution
# ---------------------------------------------------------------------------

def _execute_container(cmd: list, container_name: str, timeout: int) -> dict:
    memory_samples: list[float] = []
    stop_event = threading.Event()
    threading.Thread(
        target=_poll_memory,
        args=(container_name, memory_samples, stop_event),
        daemon=True,
    ).start()

    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            stop_event.set()
            return {
                "execution_success": False, "pass_at_1": False,
                "peak_memory_mb": _best_memory(stdout, memory_samples),
                "stdout": stdout, "stderr": stderr,
                "error": f"Execution timed out after {timeout}s",
            }
        finally:
            stop_event.set()

        exec_ok, pass1 = _parse_results(stdout, proc.returncode)
        return {
            "execution_success": exec_ok,
            "pass_at_1": pass1,
            "peak_memory_mb": _best_memory(stdout, memory_samples),
            "stdout": stdout, "stderr": stderr, "error": None,
        }
    except FileNotFoundError:
        stop_event.set()
        return _error_result("Docker not found — is Docker installed and running?")
    except Exception as exc:
        stop_event.set()
        return _error_result(str(exc))


def _poll_memory(container_name: str, samples: list, stop: threading.Event) -> None:
    time.sleep(0.05)
    while not stop.is_set():
        try:
            r = subprocess.run(
                ["docker", "stats", "--no-stream", "--format", "{{.MemUsage}}", container_name],
                capture_output=True, text=True, timeout=2,
            )
            raw = r.stdout.strip()
            if raw:
                mem = _parse_mem_usage(raw)
                if mem > 0:
                    samples.append(mem)
        except Exception:
            pass
        stop.wait(0.15)


def _parse_mem_usage(raw: str) -> float:
    part = raw.split("/")[0].strip()
    m = re.match(r"([\d.]+)\s*([KMGkmg]i?[Bb]?)", part)
    if not m:
        return 0.0
    value, unit = float(m.group(1)), m.group(2).upper()
    if unit.startswith("K"):
        return value / 1024
    elif unit.startswith("M"):
        return value
    elif unit.startswith("G"):
        return value * 1024
    return 0.0


def _best_memory(stdout: str, docker_samples: list) -> float:
    m = re.search(r"PEAK_MEMORY_MB:\s*([\d.]+)", stdout)
    if m:
        return round(float(m.group(1)), 2)
    return round(max(docker_samples, default=0.0), 2)


def _parse_results(stdout: str, returncode: int) -> tuple[bool, bool]:
    if returncode != 0 and "RESULTS:" not in stdout:
        return False, False
    test_lines = [ln for ln in stdout.splitlines() if re.match(r"TEST_\d+:", ln)]
    if not test_lines:
        ok = returncode == 0
        return ok, ok
    exec_ok  = returncode == 0 and not any("ERROR" in ln for ln in test_lines)
    all_pass = all("PASS" in ln for ln in test_lines)
    return exec_ok, all_pass


# ---------------------------------------------------------------------------
# Python harness builder
# ---------------------------------------------------------------------------

def _build_python_harness(task: dict, code: str) -> str:
    fn   = task["function_name"]
    tcs  = task["test_cases"]

    # Guard: if code lacks the function/class definition, add a stub header
    if f"def {fn}" not in code and f"class {fn}" not in code:
        code = f"def {fn}(*_args):\n" + _indent(code, 4)

    lines = [
        "import sys, resource as _res",
        "_passed = 0",
        f"_total  = {len(tcs)}",
    ]

    for i, tc in enumerate(tcs):
        if _is_eval_test(tc):
            lines.append(_py_eval_test_block(i, tc))
        else:
            lines.append(_py_func_test_block(i, fn, tc))

    lines.append('print("RESULTS: " + str(_passed) + "/" + str(_total))')
    lines.append(
        'print("PEAK_MEMORY_MB: " + '
        'str(round(_res.getrusage(_res.RUSAGE_SELF).ru_maxrss / 1024, 2)))'
    )
    return code + "\n\n# --- TEST HARNESS ---\n" + "\n".join(lines)


def _py_func_test_block(idx: int, fn: str, tc: dict) -> str:
    inp_repr = ", ".join(repr(a) for a in tc["input"])
    exp_repr = repr(tc["expected"])
    return f"""
try:
    _result   = {fn}({inp_repr})
    _expected = {exp_repr}
    if _result == _expected:
        print("TEST_{idx}: PASS")
        _passed += 1
    else:
        print("TEST_{idx}: FAIL (expected=" + repr(_expected) + ", got=" + repr(_result) + ")")
except Exception as _e:
    print("TEST_{idx}: ERROR (" + type(_e).__name__ + ": " + str(_e) + ")")
"""


def _py_eval_test_block(idx: int, tc: dict) -> str:
    """
    For class/eval-style tests: the input is a single string of
    semicolon-separated statements; the last segment is the return expression.
    """
    ops = tc["input"][0]
    exp_repr = repr(tc["expected"])
    # Split on last ';' to separate setup from final expression
    if ";" in ops:
        setup, expr = ops.rsplit(";", 1)
        setup = setup.strip()
        expr  = expr.strip()
    else:
        setup = ""
        expr  = ops.strip()

    setup_line = f'    exec({repr(setup)})' if setup else "    pass"
    return f"""
try:
{setup_line}
    _result   = eval({repr(expr)})
    _expected = {exp_repr}
    if _result == _expected:
        print("TEST_{idx}: PASS")
        _passed += 1
    else:
        print("TEST_{idx}: FAIL (expected=" + repr(_expected) + ", got=" + repr(_result) + ")")
except Exception as _e:
    print("TEST_{idx}: ERROR (" + type(_e).__name__ + ": " + str(_e) + ")")
"""


# ---------------------------------------------------------------------------
# Java harness builder
# ---------------------------------------------------------------------------

def _build_java_harness(task: dict, code: str) -> str:
    fn  = task["function_name"]
    tcs = task["test_cases"]

    test_blocks = [
        _java_eval_test_block(i, tc) if _is_eval_test(tc)
        else _java_func_test_block(i, fn, tc)
        for i, tc in enumerate(tcs)
    ]
    tests_joined = "\n".join(test_blocks)
    n = len(tcs)

    return f"""\
import java.util.*;
import java.util.stream.*;

public class Solution {{

    // ---- Generated code ----
{_indent(code, 4)}

    // ---- Test harness ----
    public static void main(String[] args) {{
        int _passed = 0;
        int _total  = {n};

{_indent(tests_joined, 8)}

        System.out.println("RESULTS: " + _passed + "/" + _total);
        Runtime rt = Runtime.getRuntime();
        long usedBytes = rt.totalMemory() - rt.freeMemory();
        System.out.printf("PEAK_MEMORY_MB: %.2f%n", usedBytes / (1024.0 * 1024.0));
    }}
}}
"""


def _java_func_test_block(idx: int, fn: str, tc: dict) -> str:
    """Standard function-call test block; converts Python values to Java."""
    inputs   = tc["input"]
    expected = tc["expected"]

    java_args = ", ".join(_py_to_java_arg(v) for v in inputs)
    call      = f"{fn}({java_args})"

    (ret_type, comparison,
     result_str, expected_str, expected_decl) = _java_comparison_info(expected)

    return f"""\
// Test {idx}
try {{
    {ret_type} _result = {call};
    {expected_decl}
    if ({comparison}) {{
        System.out.println("TEST_{idx}: PASS");
        _passed++;
    }} else {{
        System.out.println("TEST_{idx}: FAIL (expected=" + {expected_str} + ", got=" + {result_str} + ")");
    }}
}} catch (Exception _e) {{
    System.out.println("TEST_{idx}: ERROR: " + _e.getMessage());
}}"""


def _java_eval_test_block(idx: int, tc: dict) -> str:
    """
    For class/eval-style Java tests.
    input[0] is a Java code string; the last semicolon-delimited segment
    is the expression whose value is compared to expected.
    """
    ops      = tc["input"][0]
    expected = tc["expected"]

    if ";" in ops:
        setup, expr = ops.rsplit(";", 1)
        setup = setup.strip()
        expr  = expr.strip()
    else:
        setup = ""
        expr  = ops.strip()

    (ret_type, comparison,
     result_str, expected_str, expected_decl) = _java_comparison_info(expected)

    setup_stmt = f"{setup};" if setup and not setup.rstrip().endswith(";") else setup

    return f"""\
// Test {idx}
try {{
    {setup_stmt}
    {ret_type} _result = {expr};
    {expected_decl}
    if ({comparison}) {{
        System.out.println("TEST_{idx}: PASS");
        _passed++;
    }} else {{
        System.out.println("TEST_{idx}: FAIL (expected=" + {expected_str} + ", got=" + {result_str} + ")");
    }}
}} catch (Exception _e) {{
    System.out.println("TEST_{idx}: ERROR: " + _e.getMessage());
}}"""


# ---------------------------------------------------------------------------
# Python → Java value conversion
# ---------------------------------------------------------------------------

def _py_to_java_arg(val) -> str:
    """Convert a Python argument value to a Java expression."""
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, int):
        return str(val)
    if isinstance(val, float):
        return f"{val}f"
    if isinstance(val, str):
        escaped = val.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    if isinstance(val, list):
        if not val:
            return "new int[]{}"
        if all(isinstance(x, int) and not isinstance(x, bool) for x in val):
            inner = ", ".join(str(x) for x in val)
            return f"new int[]{{{inner}}}"
        if all(isinstance(x, str) for x in val):
            inner = ", ".join(f'"{x}"' for x in val)
            return f"new String[]{{{inner}}}"
        # Mixed / nested — fall back
        return "null"
    return "null"


def _java_comparison_info(expected) -> tuple[str, str, str, str, str]:
    """
    Given the Python expected value, return:
      (return_type, comparison_expr, result_to_str, expected_to_str, expected_decl)

    expected_decl is the Java statement(s) that declare+initialise `_expected`.
    """
    if isinstance(expected, bool):
        ev = "true" if expected else "false"
        return (
            "boolean",
            "_result == _expected",
            "String.valueOf(_result)",
            "String.valueOf(_expected)",
            f"boolean _expected = {ev};",
        )
    if isinstance(expected, int):
        return (
            "long",
            "_result == _expected",
            "String.valueOf(_result)",
            "String.valueOf(_expected)",
            f"long _expected = {expected}L;",
        )
    if isinstance(expected, float):
        return (
            "double",
            "Math.abs(_result - _expected) < 1e-9",
            "String.valueOf(_result)",
            "String.valueOf(_expected)",
            f"double _expected = {expected};",
        )
    if isinstance(expected, str):
        escaped = expected.replace("\\", "\\\\").replace('"', '\\"')
        return (
            "String",
            "_result != null && _result.equals(_expected)",
            "_result",
            "_expected",
            f'String _expected = "{escaped}";',
        )
    if isinstance(expected, list):
        if not expected:
            return (
                "int[]",
                "Arrays.equals(_result, _expected)",
                "Arrays.toString(_result)",
                "Arrays.toString(_expected)",
                "int[] _expected = new int[]{};",
            )
        if all(isinstance(x, int) and not isinstance(x, bool) for x in expected):
            inner = ", ".join(str(x) for x in expected)
            return (
                "int[]",
                "Arrays.equals(_result, _expected)",
                "Arrays.toString(_result)",
                "Arrays.toString(_expected)",
                f"int[] _expected = new int[]{{{inner}}};",
            )
        if all(isinstance(x, str) for x in expected):
            inner = ", ".join(f'"{x}"' for x in expected)
            return (
                "java.util.List",
                "_result != null && _result.equals(_expected)",
                "_result.toString()",
                "_expected.toString()",
                f"java.util.List _expected = java.util.Arrays.asList({inner});",
            )
    if isinstance(expected, dict):
        entries = "\n        ".join(
            f'_expected.put("{k}", {v});' for k, v in expected.items()
        )
        return (
            "java.util.Map",
            "_result != null && _result.equals(_expected)",
            "_result.toString()",
            "_expected.toString()",
            f"java.util.Map<String,Integer> _expected = new java.util.HashMap<>();\n        {entries}",
        )
    # Fallback
    return (
        "Object",
        "String.valueOf(_result).equals(String.valueOf(_expected))",
        "String.valueOf(_result)",
        f'"{expected}"',
        f'Object _expected = "{expected}";',
    )


# ---------------------------------------------------------------------------
# Eval-test detection
# ---------------------------------------------------------------------------

def _is_eval_test(tc: dict) -> bool:
    """
    Returns True when the test case encodes a sequence of operations as a
    single string rather than a plain list of function arguments.
    This is used for class-based tasks (LRU Cache, Thread-Safe Counter).
    """
    inp = tc.get("input", [])
    return (
        len(inp) == 1
        and isinstance(inp[0], str)
        and (";" in inp[0] or "new " in inp[0])
    )


# ---------------------------------------------------------------------------
# Java code normalisation
# ---------------------------------------------------------------------------

def _strip_java_class_wrapper(code: str) -> str:
    """
    Remove an outer `class … { … }` wrapper that models sometimes emit,
    keeping only the method(s) inside. Also drops any generated main().
    """
    if not re.search(r'\b(?:public\s+)?(?:abstract\s+)?class\s+\w+', code):
        return code
    match = re.search(r'\bclass\s+\w+[^{]*\{', code)
    if not match:
        return code
    start_idx = match.end() - 1
    depth = 0
    body_end = len(code)
    for i in range(start_idx, len(code)):
        if code[i] == '{':
            depth += 1
        elif code[i] == '}':
            depth -= 1
            if depth == 0:
                body_end = i
                break
    body = code[start_idx + 1 : body_end].strip()
    # Remove model-generated main() so it doesn't conflict with ours
    body = re.sub(
        r'public\s+static\s+void\s+main\s*\([^)]*\)\s*\{[^}]*\}',
        '', body, flags=re.DOTALL,
    ).strip()
    return body if body else code


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _indent(text: str, spaces: int) -> str:
    pad = " " * spaces
    return "\n".join(pad + line if line.strip() else line for line in text.splitlines())


def _error_result(msg: str) -> dict:
    return {
        "execution_success": False,
        "pass_at_1": False,
        "peak_memory_mb": 0.0,
        "stdout": "",
        "stderr": "",
        "error": msg,
    }
