MODELS = [
    "starcoder2:instruct",
    "deepseek-coder:6.7b-instruct",
    "qwen2.5-coder:7b",
]

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_TIMEOUT = 180          # seconds to wait for LLM response

DOCKER_MEMORY_LIMIT = "512m"  # container memory cap
DOCKER_CPU_LIMIT = "1"        # CPUs available to container
EXECUTION_TIMEOUT = 30        # seconds before killing container

RESULTS_DIR = "results"
DETAILED_CSV = "results/evaluation_detailed.csv"
SUMMARY_CSV  = "results/evaluation_summary.csv"

# Docker images used for sandboxed execution
DOCKER_IMAGES = {
    "python": "python:3.11-slim",
    "java":   "eclipse-temurin:17-jdk-alpine",
}
