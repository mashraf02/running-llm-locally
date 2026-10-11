
import csv
import statistics
from collections import defaultdict
from pathlib import Path

# Find the project folder automatically.
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "outputs" / "results.csv"
OUTPUT_DIR = BASE_DIR / "outputs"


def read_results():
    """Read results.csv and convert numeric values."""
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"File not found: {INPUT_FILE}\n"
            "Run run_llm.py first."
        )

    with INPUT_FILE.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    if not rows:
        raise ValueError("results.csv contains no data.")

    # Convert text values into numbers for calculations.
    for row in rows:
        row["temperature"] = float(row["temperature"])
        row["response_time_seconds"] = float(
            row["response_time_seconds"]
        )
        row["word_count"] = int(row["word_count"])

    return rows


def average(values):
    """Calculate the average of a list of numbers."""
    return statistics.mean(values)


def save_csv(filename, fieldnames, rows):
    """Save summary data to a CSV file."""
    output_file = OUTPUT_DIR / filename

    with output_file.open(
        "w", encoding="utf-8", newline=""
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return output_file


def main():
    rows = read_results()

    # Overall performance.
    times = [r["response_time_seconds"] for r in rows]

    print("\n=== Overall Results ===")
    print(f"Total model calls: {len(rows)}")
    print(f"Average response time: {average(times):.2f} seconds")
    print(f"Fastest call: {min(times):.2f} seconds")
    print(f"Slowest call: {max(times):.2f} seconds")

    # Group results by task.
    task_groups = defaultdict(list)

    for row in rows:
        task_groups[row["task"]].append(row)

    task_summary = []

    print("\n=== Performance by Task ===")
    print(f"{'Task':<16}{'Calls':>8}{'Avg Time':>14}{'Avg Words':>13}")

    for task, group in sorted(task_groups.items()):
        task_times = [r["response_time_seconds"] for r in group]
        word_counts = [r["word_count"] for r in group]

        result = {
            "task": task,
            "calls": len(group),
            "average_time_seconds": round(average(task_times), 2),
            "fastest_seconds": round(min(task_times), 2),
            "slowest_seconds": round(max(task_times), 2),
            "average_word_count": round(average(word_counts), 2),
        }

        task_summary.append(result)

        print(
            f"{task:<16}{len(group):>8}"
            f"{average(task_times):>14.2f}"
            f"{average(word_counts):>13.2f}"
        )

    save_csv(
        "task_summary.csv",
        [
            "task",
            "calls",
            "average_time_seconds",
            "fastest_seconds",
            "slowest_seconds",
            "average_word_count",
        ],
        task_summary,
    )

    # Compare summarization results by temperature.
    temperature_groups = defaultdict(list)

    for row in rows:
        if row["task"] == "summarize":
            temperature_groups[row["temperature"]].append(row)

    temperature_summary = []

    print("\n=== Summarization by Temperature ===")
    print(
        f"{'Temperature':<15}{'Runs':>8}"
        f"{'Avg Time':>14}{'Avg Words':>13}"
    )

    for temperature, group in sorted(temperature_groups.items()):
        task_times = [r["response_time_seconds"] for r in group]
        word_counts = [r["word_count"] for r in group]

        result = {
            "temperature": temperature,
            "runs": len(group),
            "average_time_seconds": round(average(task_times), 2),
            "average_word_count": round(average(word_counts), 2),
        }

        temperature_summary.append(result)

        print(
            f"{temperature:<15.1f}{len(group):>8}"
            f"{average(task_times):>14.2f}"
            f"{average(word_counts):>13.2f}"
        )

    save_csv(
        "temperature_summary.csv",
        [
            "temperature",
            "runs",
            "average_time_seconds",
            "average_word_count",
        ],
        temperature_summary,
    )

    print("\nReports saved in the outputs folder:")
    print("- task_summary.csv")
    print("- temperature_summary.csv")


if __name__ == "__main__":
    main()