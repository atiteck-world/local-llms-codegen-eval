"""
Extract the raw code block from an LLM response.

LLMs frequently wrap code in markdown fences (```python ... ``` or ``` ... ```).
This module strips the surrounding prose and returns only the code.
"""

import re


def extract_code(response: str, language: str) -> str:
    """
    Try several extraction strategies in priority order and return the
    first non-empty result.  Falls back to the full response if nothing
    matches.
    """
    # 1. Fenced block with explicit language tag  (```python / ```java)
    pattern_lang = rf"```{language}\s*\n(.*?)```"
    match = re.search(pattern_lang, response, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # 2. Any fenced block
    pattern_any = r"```(?:\w+)?\s*\n(.*?)```"
    match = re.search(pattern_any, response, re.DOTALL)
    if match:
        return match.group(1).strip()

    # 3. Single backtick inline block (rarely used for multi-line, but present)
    pattern_inline = r"`([^`]+)`"
    matches = re.findall(pattern_inline, response, re.DOTALL)
    if matches:
        longest = max(matches, key=len)
        if "\n" in longest:   # multi-line → treat as code
            return longest.strip()

    # 4. Heuristic: strip lines that look like prose (no code characters)
    lines = response.splitlines()
    code_lines = [
        ln for ln in lines
        if ln.strip() and not _looks_like_prose(ln)
    ]
    if code_lines and len(code_lines) > 2:
        return "\n".join(code_lines).strip()

    # 5. Return raw response as last resort
    return response.strip()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_PROSE_PATTERN = re.compile(
    r"^(here|this|the following|sure|of course|below|note|explanation|output|"
    r"example|solution|implementation|certainly|please|as requested|"
    r"i (will|can|would|have)|let me|feel free)",
    re.IGNORECASE,
)


def _looks_like_prose(line: str) -> bool:
    """Rough heuristic: lines that start with common prose phrases."""
    stripped = line.strip()
    if not stripped:
        return True
    if _PROSE_PATTERN.match(stripped):
        return True
    # Lines with no colons / brackets / operators are likely prose
    code_chars = set("{}[]()=<>:;,+-*/\\\"'@#")
    if not any(c in stripped for c in code_chars):
        word_count = len(stripped.split())
        return word_count > 5   # long prose sentences
    return False
