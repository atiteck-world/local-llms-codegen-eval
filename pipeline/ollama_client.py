"""
Ollama HTTP API wrapper for code generation.

Two prompt strategies are supported:

1. Instruction-tuned models (deepseek-coder:*-instruct, qwen2.5-coder:*)
   A natural-language instruction prompt is sent.  The model is expected
   to return a complete function definition, optionally inside a markdown
   code fence.

2. Completion / base models (starcoder2:*)
   starcoder2 is a fill-in-the-middle base model that does NOT follow
   natural-language instructions well.  We instead provide the function
   signature as a code prefix and let the model complete just the body.
   After generation the prefix is prepended so the full function is
   available for extraction.
"""

import time
import requests

import config

# Base completion models: contain one of these tags BUT are NOT instruct-tuned.
# Instruct variants (e.g. starcoder2:instruct) follow instructions and should
# use the standard instruction-style prompt instead.
_COMPLETION_MODEL_TAGS = ("starcoder",)
_INSTRUCT_SUFFIXES     = ("instruct", "chat", "it")


def _is_completion_model(model: str) -> bool:
    m = model.lower()
    is_base_tag  = any(tag in m for tag in _COMPLETION_MODEL_TAGS)
    is_instruct  = any(sfx in m for sfx in _INSTRUCT_SUFFIXES)
    return is_base_tag and not is_instruct


def generate(model: str, prompt: str, prefix: str = "") -> dict:
    """
    Send *prompt* to *model* via the Ollama REST API.

    Parameters
    ----------
    model  : Ollama model tag
    prompt : Text prompt to send
    prefix : If set, this string is prepended to the raw model output before
             returning (used for completion-style prompts where the function
             signature is part of the prompt rather than the response).

    Returns
    -------
    dict:
        text            : str   — full text (prefix + model output)
        generation_time : float — wall-clock seconds
        error           : str | None
    """
    url = f"{config.OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 512,
        },
    }

    t0 = time.perf_counter()
    try:
        resp = requests.post(url, json=payload, timeout=config.OLLAMA_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        generation_time = time.perf_counter() - t0
        raw = data.get("response", "")
        return {
            "text": prefix + raw,
            "generation_time": round(generation_time, 3),
            "error": None,
        }
    except requests.exceptions.Timeout:
        return {
            "text": prefix,
            "generation_time": config.OLLAMA_TIMEOUT,
            "error": "Ollama request timed out",
        }
    except Exception as exc:
        return {
            "text": prefix,
            "generation_time": round(time.perf_counter() - t0, 3),
            "error": str(exc),
        }


def build_prompt(task: dict, model: str = "") -> tuple[str, str]:
    """
    Build the prompt and the response-prefix for a task.

    Returns
    -------
    (prompt, prefix)
        prompt : string sent to the model
        prefix : string to prepend to the model's raw output
                 (empty string for instruction models)
    """
    lang = task["language"]

    if _is_completion_model(model):
        return _completion_prompt(task, lang)
    else:
        return _instruction_prompt(task, lang), ""


# ---------------------------------------------------------------------------
# Instruction-style prompt (deepseek-coder, qwen2.5-coder, …)
# ---------------------------------------------------------------------------

def _instruction_prompt(task: dict, lang: str) -> str:
    description = task["description"]
    if lang == "python":
        return (
            f"{description}\n\n"
            "Respond with ONLY the Python function definition. "
            "No explanations, no main block, no test code, no markdown.\n"
        )
    elif lang == "java":
        return (
            f"{description}\n\n"
            "Respond with ONLY the Java static method (no class wrapper, "
            "no main method, no explanations, no markdown).\n"
        )
    return task["description"]


# ---------------------------------------------------------------------------
# Completion-style prompt (starcoder2, …)
# ---------------------------------------------------------------------------

def _completion_prompt(task: dict, lang: str) -> tuple[str, str]:
    """
    Return (prompt, prefix) for a FIM / completion base model.
    The function signature is included in the prompt so the model
    only needs to produce the body.
    """
    if lang == "python":
        fn      = task["function_name"]
        # Short docstring summarising the task (first line of description)
        summary = task["description"].splitlines()[0].strip().lstrip("Write a Python function:")
        prefix  = f'def {fn}({_py_args_hint(task)}):\n    """{"".join(summary.split()[:12])}"""\n    '
        prompt  = f"# Python\n{prefix}"
        return prompt, prefix

    elif lang == "java":
        rt      = task.get("return_type", "Object")
        mn      = task["method_name"]
        sig     = _java_sig_hint(task)
        prefix  = f"public static {rt} {mn}({sig}) {{\n    "
        prompt  = f"// Java\n{prefix}"
        return prompt, prefix

    return task["description"], ""


def _py_args_hint(task: dict) -> str:
    """
    Build a minimal Python argument list from the first test case's input.
    Falls back to '*args' if not derivable.
    """
    tc = task["test_cases"][0] if task["test_cases"] else None
    if tc is None:
        return "*args"
    n = len(tc["input"])
    if n == 0:
        return ""
    if n == 1:
        return "s" if isinstance(tc["input"][0], str) else "n" if isinstance(tc["input"][0], int) else "x"
    return ", ".join(f"arg{i}" for i in range(n))


def _java_sig_hint(task: dict) -> str:
    """
    Build a minimal Java parameter list from the first test case's inputs.
    Falls back to empty string.
    """
    tc = task["test_cases"][0] if task["test_cases"] else None
    if tc is None:
        return ""
    params = []
    for j, inp in enumerate(tc["inputs"]):
        inp = inp.strip()
        if inp.startswith('"'):
            params.append(f"String p{j}")
        elif inp.startswith("new int"):
            params.append(f"int[] p{j}")
        elif inp.startswith("'"):
            params.append(f"char p{j}")
        elif inp in ("true", "false"):
            params.append(f"boolean p{j}")
        else:
            try:
                int(inp)
                params.append(f"int p{j}")
            except ValueError:
                params.append(f"Object p{j}")
    return ", ".join(params)
