
import csv
import json
import sys
import time
from pathlib import Path

import requests


# Find the project folder, regardless of the terminal's location.
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / "outputs" / "results.csv"
OLLAMA_URL = "http://localhost:11434/api/chat"


def read_text_file(path):
    """Read a UTF-8 text file or report a useful error."""
    if not path.is_file():
        raise FileNotFoundError(f"Missing file: {path}")

    return path.read_text(encoding="utf-8").strip()


def call_model(model, system_prompt, prompt, temperature, max_tokens):
    """Send one request to the locally running Ollama model."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }

    start = time.perf_counter()

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=600,
    )
    response.raise_for_status()

    data = response.json()
    answer = data["message"]["content"].strip()
    elapsed = time.perf_counter() - start

    return answer, elapsed


def main():
    # Load all settings from config.json.
    config_path = BASE_DIR / "config.json"
    config = json.loads(read_text_file(config_path))

    model = config["model"]
    temperatures = config["temperatures"]
    runs_per_setting = config["runs_per_setting"]
    default_temperature = config["default_temperature"]
    max_tokens = config["max_tokens"]

    # Load the system instructions from a file.
    system_prompt = read_text_file(
        BASE_DIR / "system" / "default.txt"
    )

    # Load the four prompts from files.
    prompts = {
        "capabilities": read_text_file(
            BASE_DIR / "prompts" / "capabilities.txt"
        ),
        "summarize": read_text_file(
            BASE_DIR / "prompts" / "summarize.txt"
        ),
        "sentiment": read_text_file(
            BASE_DIR / "prompts" / "sentiment.txt"
        ),
        "email": read_text_file(
            BASE_DIR / "prompts" / "email.txt"
        ),
    }

    # Load input texts.
    passage = read_text_file(
        BASE_DIR / "inputs" / "passage.txt"
    )
    review = read_text_file(
        BASE_DIR / "inputs" / "review.txt"
    )

    # Insert each input into its corresponding prompt.
    prompts["summarize"] = prompts["summarize"].replace(
        "{input}", passage
    )
    prompts["sentiment"] = prompts["sentiment"].replace(
        "{input}", review
    )

    # Check Ollama before starting the experiments.
    try:
        requests.get(
            "http://localhost:11434/api/tags",
            timeout=5,
        ).raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(
            "Ollama is not running or cannot be reached. "
            "Start Ollama and try again."
        ) from exc

    # Prepare the CSV output.
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    columns = [
        "task",
        "temperature",
        "run_number",
        "response_time_seconds",
        "word_count",
        "response",
    ]

    results = []

    # Run summarization twice at each configured temperature.
    for temperature in temperatures:
        for run_number in range(1, runs_per_setting + 1):
            answer, elapsed = call_model(
                model,
                system_prompt,
                prompts["summarize"],
                temperature,
                max_tokens,
            )

            results.append({
                "task": "summarize",
                "temperature": temperature,
                "run_number": run_number,
                "response_time_seconds": round(elapsed, 3),
                "word_count": len(answer.split()),
                "response": answer,
            })

            print(
                f"\n=== Summarization | "
                f"Temperature {temperature} | "
                f"Run {run_number} ==="
            )
            print(answer)

    # Run each remaining task once at the default temperature.
    for task in ["capabilities", "sentiment", "email"]:
        answer, elapsed = call_model(
            model,
            system_prompt,
            prompts[task],
            default_temperature,
            max_tokens,
        )

        results.append({
            "task": task,
            "temperature": default_temperature,
            "run_number": 1,
            "response_time_seconds": round(elapsed, 3),
            "word_count": len(answer.split()),
            "response": answer,
        })

        print(f"\n=== {task.title()} ===")
        print(answer)

    # Save every model call, including the full response.
    with OUTPUT_FILE.open(
        "w", newline="", encoding="utf-8-sig"
    ) as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nCompleted {len(results)} model calls.")
    print(f"Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"ERROR: config.json contains invalid JSON: {exc}",
              file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as exc:
        print(f"ERROR: Ollama request failed: {exc}",
              file=sys.stderr)
        sys.exit(1)
    except (RuntimeError, KeyError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)