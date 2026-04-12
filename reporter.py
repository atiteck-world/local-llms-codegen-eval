"""
Save evaluation results to CSV files.

Two files are produced:
  evaluation_detailed.csv  — one row per (model × task), includes category + difficulty
  evaluation_summary.csv   — aggregated metrics per (model × language × difficulty)
"""

import csv
import os

import config


# ---------------------------------------------------------------------------
# Column definitions
# ---------------------------------------------------------------------------

DETAILED_FIELDS = [
    "model",
    "language",
    "category",
    "difficulty",
    "task_id",
    "task_title",
    "generation_time_s",
    "execution_success",
    "pass_at_1",
    "peak_memory_mb",
    "error",
]

SUMMARY_FIELDS = [
    "model",
    "language",
    "difficulty",
    "total_tasks",
    "execution_success_rate",
    "pass_at_1_rate",
    "avg_generation_time_s",
    "avg_peak_memory_mb",
]


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def save_detailed(rows: list[dict], path: str = config.DETAILED_CSV) -> None:
    """Write the per-task rows to a CSV file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=DETAILED_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  [reporter] Detailed results → {path}")


def save_summary(rows: list[dict], path: str = config.SUMMARY_CSV) -> None:
    """Aggregate per-task rows and write summary CSV."""
    summary = _aggregate(rows)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(summary)
    print(f"  [reporter] Summary results  → {path}")


def print_summary_table(rows: list[dict]) -> None:
    """Print a formatted summary table to stdout, grouped by difficulty."""
    summary = _aggregate(rows)
    header = (
        f"{'Model':<30} {'Lang':<8} {'Difficulty':<10} {'Tasks':>6} "
        f"{'Exec%':>7} {'Pass@1%':>8} "
        f"{'AvgGen(s)':>10} {'AvgMem(MB)':>11}"
    )
    sep = "=" * len(header)
    print("\n" + sep)
    print(header)
    print(sep)
    prev_model = None
    for r in summary:
        if prev_model and prev_model != r["model"]:
            print("-" * len(header))
        print(
            f"{r['model']:<30} {r['language']:<8} {r['difficulty']:<10} {r['total_tasks']:>6} "
            f"{r['execution_success_rate']:>7.1f} {r['pass_at_1_rate']:>8.1f} "
            f"{r['avg_generation_time_s']:>10.2f} {r['avg_peak_memory_mb']:>11.2f}"
        )
        prev_model = r["model"]
    print(sep)


# ---------------------------------------------------------------------------
# Internal
# ---------------------------------------------------------------------------

def _aggregate(rows: list[dict]) -> list[dict]:
    """Group by (model, language, difficulty) and compute aggregate metrics."""
    groups: dict[tuple, list] = {}
    for r in rows:
        key = (r["model"], r["language"], r.get("difficulty", "unknown"))
        groups.setdefault(key, []).append(r)

    summary = []
    for (model, language, difficulty), group in sorted(groups.items()):
        total    = len(group)
        exec_ok  = sum(1 for r in group if str(r["execution_success"]).lower() == "true")
        pass_ok  = sum(1 for r in group if str(r["pass_at_1"]).lower() == "true")
        gen_times = [float(r["generation_time_s"]) for r in group if r["generation_time_s"] not in ("", None)]
        mem_vals  = [float(r["peak_memory_mb"])    for r in group if r["peak_memory_mb"]    not in ("", None)]

        summary.append({
            "model":                    model,
            "language":                 language,
            "difficulty":               difficulty,
            "total_tasks":              total,
            "execution_success_rate":   round(exec_ok / total * 100, 2) if total else 0,
            "pass_at_1_rate":           round(pass_ok / total * 100,  2) if total else 0,
            "avg_generation_time_s":    round(sum(gen_times) / len(gen_times), 3) if gen_times else 0,
            "avg_peak_memory_mb":       round(sum(mem_vals)  / len(mem_vals),  2) if mem_vals  else 0,
        })
    return summary
