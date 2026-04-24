"""
LLM Code-Generation Evaluation Pipeline
========================================

Evaluates starcoder2:7b, deepseek-coder:6.7b, and qwen2.5-coder:7b on 40
programming tasks (20 Python + 20 Java) using Ollama + Docker sandboxes.

Metrics collected per task:
  - generation_time_s    : wall-clock seconds for LLM to produce code
  - execution_success    : code ran without uncaught exceptions (bool)
  - pass_at_1            : all test cases passed on first try (bool)
  - peak_memory_mb       : peak RSS during execution (MB)

Usage
-----
    pip install -r requirements.txt
    python main.py [--models m1 m2 ...] [--languages python java] [--limit N]

Prerequisites
-------------
  - Ollama running locally (ollama serve)
  - Docker daemon running
  - Models pulled: ollama pull starcoder2:7b  etc.
"""

import argparse
import os
import subprocess
import sys
import time

from tqdm import tqdm

import config
import reporter
from dataset.tasks import ALL_TASKS
from pipeline import code_extractor, ollama_client, docker_executor


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="LLM code-generation evaluator")
    p.add_argument(
        "--models", nargs="+",
        default=config.MODELS,
        metavar="MODEL",
        help="Ollama model tags to evaluate (default: all configured models)",
    )
    p.add_argument(
        "--languages", nargs="+",
        default=["python", "java"],
        choices=["python", "java"],
        help="Languages to include (default: python java)",
    )
    p.add_argument(
        "--limit", type=int, default=None,
        metavar="N",
        help="Limit to first N tasks per language (useful for quick smoke-tests)",
    )
    p.add_argument(
        "--skip-docker-pull", action="store_true",
        help="Skip pulling Docker images at startup",
    )
    p.add_argument(
        "--output-dir", default=config.RESULTS_DIR,
        help=f"Directory for CSV output (default: {config.RESULTS_DIR})",
    )
    return p.parse_args()


# ---------------------------------------------------------------------------
# Setup helpers
# ---------------------------------------------------------------------------

def check_ollama(models: list[str]) -> None:
    print("[setup] Checking Ollama availability …")
    import requests
    try:
        r = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=5)
        r.raise_for_status()
        available = {m["name"] for m in r.json().get("models", [])}
        missing = [m for m in models if m not in available]
        if missing:
            print(f"  WARNING: These models are not pulled yet: {missing}")
            print("  Run: ollama pull <model>  for each one.")
    except Exception as exc:
        print(f"  WARNING: Cannot reach Ollama at {config.OLLAMA_BASE_URL}: {exc}")
        print("  Make sure `ollama serve` is running.")


def pull_docker_images(languages: list[str]) -> None:
    print("[setup] Pulling Docker images …")
    for lang in languages:
        image = config.DOCKER_IMAGES.get(lang)
        if not image:
            continue
        print(f"  docker pull {image}")
        subprocess.run(["docker", "pull", image], check=False)


def select_tasks(languages: list[str], limit: int | None) -> list[dict]:
    tasks = [t for t in ALL_TASKS if t["language"] in languages]
    if limit:
        # apply limit per language
        selected = []
        for lang in languages:
            lang_tasks = [t for t in tasks if t["language"] == lang]
            selected.extend(lang_tasks[:limit])
        return selected
    return tasks


# ---------------------------------------------------------------------------
# Core evaluation loop
# ---------------------------------------------------------------------------

def evaluate(models: list[str], tasks: list[dict], output_dir: str) -> list[dict]:
    all_rows: list[dict] = []
    total_runs = len(models) * len(tasks)

    print(f"\n[eval] Starting evaluation: {len(models)} model(s) × {len(tasks)} task(s) = {total_runs} runs\n")

    with tqdm(total=total_runs, unit="run", ncols=90) as pbar:
        for model in models:
            pbar.set_description(f"{model}")

            for task in tasks:
                row = _run_single(model, task)
                all_rows.append(row)

                status = "PASS" if row["pass_at_1"] else ("EXEC" if row["execution_success"] else "FAIL")
                pbar.set_postfix(
                    task=task["id"],
                    status=status,
                    gen=f"{row['generation_time_s']:.1f}s",
                )
                pbar.update(1)

    # Persist results
    os.makedirs(output_dir, exist_ok=True)
    detailed_path = os.path.join(output_dir, "evaluation_detailed.csv")
    summary_path  = os.path.join(output_dir, "evaluation_summary.csv")

    print()
    reporter.save_detailed(all_rows, detailed_path)
    reporter.save_summary(all_rows,  summary_path)
    reporter.print_summary_table(all_rows)

    return all_rows


def _run_single(model: str, task: dict) -> dict:
    """Run one (model, task) pair and return a result row."""
    row = {
        "model":             model,
        "language":          task["language"],
        "category":          task.get("category", ""),
        "difficulty":        task.get("difficulty", ""),
        "task_id":           task["id"],
        "task_title":        task["title"],
        "generation_time_s": 0.0,
        "execution_success": False,
        "pass_at_1":         False,
        "peak_memory_mb":    0.0,
        "error":             None,
    }

    # ── 1. Generate code via Ollama ──────────────────────────────────────
    prompt = ollama_client.build_prompt(task)
    gen_result = ollama_client.generate(model, prompt)

    row["generation_time_s"] = gen_result["generation_time"]

    if gen_result["error"]:
        row["error"] = f"Generation error: {gen_result['error']}"
        return row

    raw_response = gen_result["text"]
    if not raw_response.strip():
        row["error"] = "Empty response from model"
        return row

    # ── 2. Extract code from response ────────────────────────────────────
    code = code_extractor.extract_code(raw_response, task["language"])

    # ── 3. Execute in Docker sandbox ─────────────────────────────────────
    exec_result = docker_executor.run_task(task, code)

    row["execution_success"] = exec_result["execution_success"]
    row["pass_at_1"]         = exec_result["pass_at_1"]
    row["peak_memory_mb"]    = exec_result["peak_memory_mb"]

    if exec_result["error"]:
        row["error"] = exec_result["error"]

    return row


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    # Override output paths if custom dir given
    config.RESULTS_DIR  = args.output_dir
    config.DETAILED_CSV = os.path.join(args.output_dir, "evaluation_detailed.csv")
    config.SUMMARY_CSV  = os.path.join(args.output_dir, "evaluation_summary.csv")

    print("=" * 60)
    print("  LLM Code-Generation Evaluation Pipeline")
    print("=" * 60)
    print(f"  Models    : {args.models}")
    print(f"  Languages : {args.languages}")
    print(f"  Output    : {args.output_dir}/")
    print("=" * 60)

    # ── Pre-flight checks ────────────────────────────────────────────────
    check_ollama(args.models)

    if not args.skip_docker_pull:
        pull_docker_images(args.languages)

    # ── Task selection ───────────────────────────────────────────────────
    tasks = select_tasks(args.languages, args.limit)
    print(f"\n[info] Running {len(tasks)} tasks across {len(args.languages)} language(s).")

    if not tasks:
        print("No tasks selected. Exiting.")
        sys.exit(0)

    # ── Main loop ────────────────────────────────────────────────────────
    t0 = time.perf_counter()
    evaluate(args.models, tasks, args.output_dir)
    elapsed = time.perf_counter() - t0

    print(f"\n[done] Total wall-clock time: {elapsed / 60:.1f} min")


if __name__ == "__main__":
    main()
