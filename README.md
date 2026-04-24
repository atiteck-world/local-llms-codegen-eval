# Benchmarking Local Large Language Models for Code Generation: An Automated Evaluation Pipeline
### A Comparative Study of Small-Scale Code Models Using Sandboxed Execution

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python" />
  <img src="https://img.shields.io/badge/Java-17-orange?style=flat-square&logo=openjdk" />
  <img src="https://img.shields.io/badge/Docker-sandboxed-2496ED?style=flat-square&logo=docker" />
  <img src="https://img.shields.io/badge/Ollama-local%20inference-black?style=flat-square" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" />
</p>

---

## Overview

This repository contains the full evaluation pipeline developed for the master's thesis:

> **"Benchmarking Local Large Language Models for Code Generation: An Automated Evaluation Pipeline"**

The pipeline benchmarks three state-of-the-art, locally-hosted code generation models on a custom dataset of **40 programming tasks** (20 Python + 20 Java), spanning five task categories and three difficulty levels. Generated code is executed in isolated Docker sandboxes to collect objective, reproducible metrics.

---

## Models Under Evaluation

| Model | Parameters | Type | Provider |
|---|---|---|---|
| `starcoder2:instruct` | ~7B | Instruction-tuned | BigCode |
| `deepseek-coder:6.7b-instruct` | 6.7B | Instruction-tuned | DeepSeek |
| `qwen2.5-coder:7b` | 7B | Instruction-tuned | Alibaba |

All models are served locally via [Ollama](https://ollama.com) — no API keys or internet access required during evaluation.

---

## Dataset

A custom benchmark of **40 tasks** covering a practical range of programming competency:

| | Easy | Medium | Hard | Total |
|---|---|---|---|---|
| **Python** | 7 | 8 | 5 | 20 |
| **Java** | 7 | 8 | 5 | 20 |
| **Total** | 14 | 16 | 10 | **40** |

### Task Categories

| Category | Description | Example Tasks |
|---|---|---|
| `string_manipulation` | Text processing and pattern operations | Reverse String, Run-Length Encoding, Is Anagram |
| `algorithms` | Classic algorithmic problems | Binary Search, Bubble Sort, LCS, Two Sum |
| `data_structures` | Stack, cache, and recursive structures | Balanced Parentheses, Flatten List, LRU Cache |
| `concurrency` | Thread-safe programming primitives | Thread-Safe Counter |
| `self_invoking` | Functions that call sibling functions | GCD + LCM of List |

Each task includes a natural-language description (the LLM prompt), 4–5 test cases with expected outputs, and supports two execution modes: **function-call** (standard tasks) and **eval/class-based** (OOP tasks such as LRU Cache).

---

## Metrics

| Metric | Description |
|---|---|
| **Execution Success Rate** | % of tasks where generated code ran without uncaught exceptions |
| **Pass@1** | % of tasks where the first generated solution passed all test cases |
| **Generation Time (s)** | Wall-clock seconds for the model to respond via the Ollama API |
| **Peak Memory (MB)** | Max RSS memory during execution, measured inside the container |

Results are broken down by **model × language × difficulty level**.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Evaluation Pipeline                  │
│                                                         │
│  dataset/tasks.py                                       │
│       │  40 tasks (Python + Java)                       │
│       ▼                                                 │
│  ollama_client.py  ──►  Ollama API (localhost:11434)    │
│       │  generated code + generation_time               │
│       ▼                                                 │
│  code_extractor.py                                      │
│       │  strips markdown fences / prose                 │
│       ▼                                                 │
│  docker_executor.py                                     │
│       │  ┌──────────────────────────────┐               │
│       │  │  Docker sandbox              │               │
│       │  │  --network none              │               │
│       │  │  --memory 512m               │               │
│       │  │                              │               │
│       │  │  python:3.11-slim  (Python)  │               │
│       │  │  eclipse-temurin:17 (Java)   │               │
│       │  └──────────────────────────────┘               │
│       │  execution_success, pass@1, peak_memory         │
│       ▼                                                 │
│  reporter.py  ──►  results/evaluation_detailed.csv      │
│                    results/evaluation_summary.csv       │
└─────────────────────────────────────────────────────────┘
```

### Key Design Decisions

| Decision | Rationale |
|---|---|
| Local inference via Ollama | No data leaves the machine; fully reproducible |
| `--network none` containers | Prevents outbound calls during code execution |
| In-container memory measurement | `resource.getrusage` (Python) / `Runtime.getRuntime()` (Java) — more accurate than polling `docker stats` for short-lived containers |
| Model-aware prompting | Instruction-tuned models receive a natural-language prompt; base completion models receive a code-prefix prompt |
| Java class-wrapper stripping | Models often wrap their output in `class Solution {}` — the harness automatically unwraps it to avoid duplicate-class compilation errors |

---

## Project Structure

```
lllms-codegen-eval/
│
├── main.py                     # Entry point — orchestrates the full pipeline
├── config.py                   # Models, timeouts, Docker limits, output paths
├── requirements.txt
│
├── dataset/
│   └── tasks.py                # 40 benchmark tasks with test cases
│
├── pipeline/
│   ├── ollama_client.py        # Ollama REST API wrapper + prompt builder
│   ├── code_extractor.py       # Extract code block from raw LLM output
│   └── docker_executor.py      # Sandbox execution + test harness generation
│
└── results/                    # Generated output (git-ignored)
    ├── evaluation_detailed.csv
    └── evaluation_summary.csv
```

---

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | ≥ 3.11 | Pipeline runtime |
| Docker | ≥ 24 | Sandboxed execution |
| Ollama | ≥ 0.3 | Local LLM inference server |

---

## Setup & Usage

### 1. Clone and install dependencies

```bash
git clone https://github.com/atiteck-world/local-llms-codegen-eval.git
cd local-llms-codegen-eval
pip install -r requirements.txt
```

### 2. Start Ollama and pull models

```bash
ollama serve

# In a separate terminal:
ollama pull starcoder2:instruct
ollama pull deepseek-coder:6.7b-instruct
ollama pull qwen2.5-coder:7b
```

### 3. Pull Docker execution images

```bash
docker pull python:3.11-slim
docker pull eclipse-temurin:17-jdk-alpine
```

### 4. Run the evaluation

```bash
# Full benchmark — all 3 models × 40 tasks (≈ 15–20 min)
python main.py

# Quick smoke-test — 5 tasks per language
python main.py --limit 5 --skip-docker-pull

# Single model or language
python main.py --models deepseek-coder:6.7b-instruct --languages python

# Custom output directory
python main.py --output-dir my_results/
```

### CLI Reference

| Flag | Default | Description |
|---|---|---|
| `--models` | all 3 | Space-separated Ollama model tags |
| `--languages` | `python java` | Languages to benchmark |
| `--limit N` | — | Max tasks per language (for quick tests) |
| `--skip-docker-pull` | off | Skip `docker pull` at startup |
| `--output-dir PATH` | `results/` | Directory for CSV output |

---

## Output

### `evaluation_detailed.csv` — one row per (model × task)

| Column | Description |
|---|---|
| `model` | Ollama model tag |
| `language` | `python` or `java` |
| `category` | Task category |
| `difficulty` | `easy` / `medium` / `hard` |
| `task_id` | e.g. `py_001`, `java_012` |
| `task_title` | Human-readable task name |
| `generation_time_s` | LLM response time in seconds |
| `execution_success` | `True` if code ran without runtime errors |
| `pass_at_1` | `True` if all test cases passed on first attempt |
| `peak_memory_mb` | Peak memory during execution (MB) |
| `error` | Infrastructure error message, if any |

### `evaluation_summary.csv` — aggregated per (model × language × difficulty)

| Column | Description |
|---|---|
| `execution_success_rate` | % tasks that executed without errors |
| `pass_at_1_rate` | % tasks that passed all tests on first try |
| `avg_generation_time_s` | Mean generation time |
| `avg_peak_memory_mb` | Mean peak execution memory |

---

## Results

> Full data: [results/evaluation_detailed.csv](results/evaluation_detailed.csv) · [results/evaluation_summary.csv](results/evaluation_summary.csv)

### Overall Performance (40 tasks — 20 Python + 20 Java)

| Model | Exec. Success | Pass@1 | Avg. Gen. Time | Python Mem |
|---|---|---|---|---|
| `qwen2.5-coder:7b` | **90.0%** | **85.0%** | **11.41 s** | ~11.86 MB |
| `deepseek-coder:6.7b-instruct` | **90.0%** | **85.0%** | 17.28 s | ~11.82 MB |
| `starcoder2:instruct` | **90.0%** | **85.0%** | 55.50 s | ~11.78 MB |

All three models achieve the same overall correctness (85% pass@1). The decisive differentiator is **generation speed**: `qwen2.5-coder:7b` is **4.9× faster** than `starcoder2:instruct` with identical accuracy.

---

### By Language

| Model | Python Exec% | Python Pass@1% | Java Exec% | Java Pass@1% |
|---|---|---|---|---|
| `qwen2.5-coder:7b` | **100%** | **95%** | 80% | 75% |
| `deepseek-coder:6.7b-instruct` | 95% | **90%** | **85%** | **80%** |
| `starcoder2:instruct` | **100%** | **95%** | 80% | 75% |

All models perform substantially better in Python than Java. `deepseek-coder:6.7b-instruct` leads in Java correctness; `qwen2.5-coder:7b` and `starcoder2:instruct` are tied on Python.

---

### By Difficulty Level (all models combined, 120 total runs)

| Difficulty | Tasks | Passes | Pass@1 Rate |
|---|---|---|---|
| Easy | 42 | 42 | **100.0%** |
| Medium | 48 | 41 | **85.4%** |
| Hard | 30 | 19 | **63.3%** |

Easy tasks pose no challenge to any model. Performance degrades predictably with difficulty, dropping 22 percentage points from medium to hard.

---

### Generation Speed

| Model | Avg. Time / Task | Total (40 tasks) | vs. Fastest |
|---|---|---|---|
| `qwen2.5-coder:7b` | **11.41 s** | 456 s | 1× (baseline) |
| `deepseek-coder:6.7b-instruct` | 17.28 s | 691 s | 1.5× slower |
| `starcoder2:instruct` | 55.50 s | 2220 s | 4.9× slower |

`starcoder2:instruct` consistently generates much longer responses (reflecting more verbose reasoning), which explains the speed gap despite similar final accuracy.

---

### Failure Analysis

**Tasks that fail for all three models:**

| Task | Language | Category | Difficulty | Root Cause |
|---|---|---|---|---|
| Two Sum | Python | algorithms | medium | Wrong index ordering in edge cases |
| Two Sum | Java | algorithms | medium | Wrong index ordering in edge cases |
| Flatten List | Java | data_structures | hard | Recursive generics compilation error |
| LRU Cache | Java | data_structures | hard | Complex OOP / LinkedHashMap usage |
| Thread-Safe Counter | Java | concurrency | hard | AtomicInteger import / class structure |

**Tasks where only 2 of 3 models succeed:**

| Task | Language | Who fails |
|---|---|---|
| Word Frequency | Java | `qwen2.5-coder:7b` |
| GCD and LCM of List | Java | `starcoder2:instruct` |
| GCD and LCM of List | Python | `deepseek-coder:6.7b-instruct` |

**Key observations:**
- The **Two Sum** failure across all models in both languages suggests a systematic weakness in handling the edge case `[0, 4, 3, 0], target=0` where duplicate values and index ordering matter
- All Java **hard data-structure and concurrency tasks** fail universally — models generate syntactically plausible but semantically incorrect class hierarchies
- Java **easy and medium tasks** succeed at near-perfect rates, showing that the difficulty gap is specific to OOP complexity, not Java syntax in general

---

## Reproducibility

- Model temperature is fixed at **0.2** across all runs
- Docker containers are fully isolated (`--network none`, `--memory 512m`, `--cpus 1`)
- All test cases and expected outputs are deterministic and versioned in `dataset/tasks.py`
- The pipeline can be re-run at any time to reproduce results

---

## License

This project is released under the [MIT License](LICENSE).

---

## Citation

If you use this pipeline or dataset in your research, please cite:

```bibtex
@mastersthesis{atiim2026lllmcodegen,
  title  = {Benchmarking Local Large Language Models for Code Generation: An Automated Evaluation Pipeline},
  author = {Atiim Bismark Azumah},
  school = {Schmalkalden University of Applied Sciences},
  year   = {2026},
}
```
