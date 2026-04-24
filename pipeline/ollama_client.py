import time
import requests

import config


def generate(model: str, prompt: str) -> dict:
    """
    Send *prompt* to *model* via the Ollama REST API.

    Returns
    -------
    dict:
        text            : str   — model output
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
        return {
            "text": data.get("response", ""),
            "generation_time": round(time.perf_counter() - t0, 3),
            "error": None,
        }
    except requests.exceptions.Timeout:
        return {
            "text": "",
            "generation_time": config.OLLAMA_TIMEOUT,
            "error": "Ollama request timed out",
        }
    except Exception as exc:
        return {
            "text": "",
            "generation_time": round(time.perf_counter() - t0, 3),
            "error": str(exc),
        }


def build_prompt(task: dict) -> str:
    description = task["description"]
    lang = task["language"]

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
    return description
