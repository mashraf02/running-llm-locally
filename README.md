# Running an LLM Locally: Setup, Python Integration & Temperature Testing

This repository contains the complete implementation, experimental evaluation, and analysis for running a Large Language Model (LLM) locally using **Ollama** and **Python**. The project explores local model deployment, automated prompt evaluation via the Ollama REST API, temperature benchmarking, and result aggregation.

---

## 📋 Table of Contents
- [Overview](#overview)
- [System Environment & Hardware](#system-environment--hardware)
- [Project Architecture & Directory Structure](#project-architecture--directory-structure)
- [Part 1: Local Model Setup & Verification](#part-1-local-model-setup--verification)
- [Part 2: Python Automation & Pipeline](#part-2-python-automation--pipeline)
- [Part 3: Experimental Tasks & Results](#part-3-experimental-tasks--results)
  - [Task 1: Capability Summary](#task-1-capability-summary)
  - [Task 2: Text Summarization & Temperature Testing](#task-2-text-summarization--temperature-testing)
  - [Task 3: Sentiment Classification](#task-3-sentiment-classification)
  - [Task 4: Professional Email Generation](#task-4-professional-email-generation)
- [Performance & Statistical Summary](#performance--statistical-summary)
- [Getting Started](#getting-started)
- [Report](#report)

---

## 🔍 Overview

Running LLMs locally offers privacy, complete offline autonomy, zero API usage costs, and full control over prompt pipelines. In this project:
- **Model**: Google Gemma 4 (2B quantized variant `gemma4:e2b`, disk footprint: ~4.6 GB, memory footprint: ~970 MB).
- **Inference Engine**: [Ollama](https://ollama.ai) (`v0.40.2`) running locally on CPU via `llamacpp`.
- **Python Integration**: Modular script reading prompts, inputs, and configurations entirely from disk to ensure repeatable experiments, outputting raw results and aggregated summaries to CSV.
- **Testing Scope**: Evaluated across 4 distinct tasks and 3 temperature settings (`0.0`, `0.3`, `1.0`).

---

## 💻 System Environment & Hardware

The experiments were executed on a CPU-bound machine with the following specifications:

| Component | Specification |
| :--- | :--- |
| **Operating System** | Windows (MINGW64 / Git Bash environment) |
| **Processor (CPU)** | Intel Core i3 (CPU-only inference, 100% load during generation) |
| **RAM** | 12 GB |
| **GPU** | Integrated Graphics (113 MB; no dedicated discrete GPU required) |
| **Storage** | 1.03 TB HDD/SSD |
| **Ollama Version** | `0.40.2` |
| **Ollama Runner** | `llamacpp` (context window: 4096 tokens) |
| **API Interface** | Local REST API: `POST http://localhost:11434/api/chat` |

---

## 📁 Project Architecture & Directory Structure

```
Running-LLM-Locally/
├── README.md                              # Project documentation
├── Running_an_LLM_Locally_Report.pdf      # Detailed formal academic report
├── config.json                            # Experiment parameters and model settings
├── run_llm.py                             # Main orchestration script (calls Ollama API)
├── analyze_results.py                     # Results analysis & statistical aggregation script
├── system/
│   └── default.txt                        # System instruction prompt
├── inputs/
│   ├── passage.txt                        # Source renewable-energy passage for summarization
│   └── review.txt                         # Customer review text for sentiment classification
├── prompts/
│   ├── capabilities.txt                   # Prompt template for capability summary
│   ├── summarize.txt                      # Prompt template with {input} placeholder
│   ├── sentiment.txt                      # Prompt template with {input} placeholder
│   └── email.txt                          # Prompt template for supervisor meeting request
├── outputs/
│   ├── results.csv                        # Per-call recorded results (9 runs total)
│   ├── task_summary.csv                   # Aggregated statistics per task
│   └── temperature_summary.csv            # Aggregated statistics per temperature setting
└── screenshots/                           # Verification evidence captures
    ├── Screenshot_2026-10-11_101932.png   # Ollama version check
    ├── Screenshot_2026-10-11_102023.png   # Local model listing (ollama list)
    ├── Screenshot_2026-10-11_102640.png   # Interactive test session (ollama run)
    ├── Screenshot_2026-10-11_last.png     # Loaded model & CPU utilization (ollama ps)
    └── Screenshot_2026-10-11_132403.png   # Offline inference verification
```

---

## ⚙️ Part 1: Local Model Setup & Verification

1. **Ollama Installation**: Verified with `ollama --version` (`v0.40.2`).
2. **Model Download**: Model `gemma4:e2b` pulled locally (`ollama pull gemma4:e2b`), verified via `ollama list` (ID: `b37049369adf`, 4.6 GB).
3. **Interactive Inference**: Verified local reasoning using `ollama run gemma4:e2b` with a test query on databases.
4. **Process Monitoring**: Verified via `ollama ps`:
   - Processor: `100% CPU`
   - Runner: `llamacpp`
   - Memory Loaded: `970 MB`
   - Context: `4096`
5. **Offline Capability**: Verified by running generation while disconnected from the internet (system tray showing disconnected globe indicator).

---

## 🐍 Part 2: Python Automation & Pipeline

### Configuration (`config.json`)
```json
{
  "model": "gemma4:e2b",
  "temperatures": [0.0, 0.3, 1.0],
  "runs_per_setting": 2,
  "default_temperature": 0.0,
  "max_tokens": 1024
}
```
> **Note on `max_tokens`**: The standard assignment baseline was 512 tokens. During initial runs, multi-step chain-of-thought responses risked premature truncation before final outputs. To ensure complete, well-formed answers without output truncation, `max_tokens` was configured to `1024` (documented in Section 5 of the report).

### Workflow Implementation (`run_llm.py` & `analyze_results.py`)
- **Decoupled Inputs**: Prompts and inputs are kept strictly in external `.txt` files; changing prompts requires zero code modifications.
- **REST Integration**: Issues synchronous non-streaming HTTP POST requests to `http://localhost:11434/api/chat`.
- **Pre-Flight Health Check**: Queries `/api/tags` to ensure Ollama daemon is active before initiating runs.
- **Data Recording**: Tracks task name, temperature, run iteration, elapsed time (`time.perf_counter()`), token/word count (`len(answer.split())`), and full verbatim responses.
- **Statistical Aggregation**: `analyze_results.py` computes mean response times, fastest/slowest runs, and word count distributions.

---

## 📊 Part 3: Experimental Tasks & Results

A total of 9 model executions were logged across four evaluation tasks:

### Task 1: Capability Summary
- **Prompt**: List 3–5 capabilities and 3–5 limitations in exact bullet format, under 150 words.
- **Result**: Complied 100% with format rules (4 capability bullets, 4 limitation bullets, 78 words recorded, 64.41s response time).

### Task 2: Text Summarization & Temperature Testing
- **Task Requirements**: Summarize the renewable energy passage into exactly 3 bullet points, 1 sentence each, $\le$ 25 words per bullet.
- **Testing Grid**: Tested at temperatures `0.0`, `0.3`, and `1.0` (2 runs each).

| Temperature | Run | Time (s) | Word Count | Format Compliant? | Key Observations |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **0.0** | Run 1 | 81.72s | 52 | ✅ Yes (3 bullets, 1 sentence each, $\le$ 25 words) | Identical first bullet with Run 2; covers 5 core ideas fully. |
| **0.0** | Run 2 | 63.68s | 47 | ✅ Yes (3 bullets, 1 sentence each, $\le$ 25 words) | Identical first bullet; covers emissions targets specifically. |
| **0.3** | Run 1 | 54.77s | 42 | ✅ Yes (3 bullets, 1 sentence each, $\le$ 25 words) | Shortest summary; mentions storage and financing constraints. |
| **0.3** | Run 2 | 65.06s | 52 | ✅ Yes (3 bullets, 1 sentence each, $\le$ 25 words) | Slightly varied phrasing; mentions grid stability. |
| **1.0** | Run 1 | 62.61s | 48 | ✅ Yes (3 bullets, 1 sentence each, $\le$ 25 words) | Replaces "worldwide" with "globally"; fully compliant. |
| **1.0** | Run 2 | 54.19s | 51 | ✅ Yes (3 bullets, 1 sentence each, $\le$ 25 words) | Varied wording; introduces "increased new capacity". |

#### Temperature Analysis Takeaways
- **Recommended Temperature for Summarization**: **`0.0`**. Low randomness ensures high fidelity to source facts, minimizes semantic hallucination, and preserves precision across repeated queries.
- **Constraint Compliance**: All 6 runs strictly satisfied the 3-bullet, 1-sentence, $\le$ 25-word constraint regardless of temperature.

### Task 3: Sentiment Classification
- **Input**: Customer review praising audio and battery life, but noting poor cushion comfort, app drops, and delayed customer support.
- **Output**:
  - `Label: Mixed`
  - `Explanation: The reviewer praises the excellent sound quality and long battery life, but also notes issues with uncomfortable ear cushions and frequent app disconnections. Additionally, the slow response time from customer support contributes to the mixed sentiment.`
- **Result**: Exactly 2 sentences, correct label, accurate reasoning. Fastest execution of all tests (**14.65s**).

### Task 4: Professional Email Generation
- **Prompt**: Formal meeting request for 30 minutes next week, mentioning completion of data collection, analysis underway, offering two time slots, signed as "Student Name", under 150 words.
- **Result**: Complied with all requirements (109 words, offered Tuesday 10:00 AM & Thursday 2:00 PM, polite tone, signed appropriately; 72.42s).

---

## 📈 Performance & Statistical Summary

### Aggregated Performance by Task (`outputs/task_summary.csv`)
| Task | Calls | Avg Time (s) | Fastest (s) | Slowest (s) | Avg Words |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **capabilities** | 1 | 64.41 | 64.41 | 64.41 | 78.00 |
| **email** | 1 | 72.42 | 72.42 | 72.42 | 109.00 |
| **sentiment** | 1 | 14.65 | 14.65 | 14.65 | 39.00 |
| **summarize** | 6 | 63.67 | 54.19 | 81.72 | 48.67 |
| **Overall / Total** | **9** | **59.28** | **14.65** | **81.72** | — |

### Summarization Performance by Temperature (`outputs/temperature_summary.csv`)
| Temperature | Runs | Average Time (s) | Average Words |
| :---: | :---: | :---: | :---: |
| **0.0** | 2 | 72.70 s | 49.50 |
| **0.3** | 2 | 59.92 s | 47.00 |
| **1.0** | 2 | 58.40 s | 49.50 |

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- [Ollama](https://ollama.ai) installed and running

### 2. Pull the Model
```bash
ollama pull gemma4:e2b
```

### 3. Clone Repository & Install Dependencies
```bash
git clone https://github.com/mashraf02/running-llm-locally.git
cd running-llm-locally

# Install required Python packages (requests)
pip install requests
```

### 4. Run the Pipeline
Ensure Ollama service is active (`ollama serve` or background daemon), then execute:
```bash
# Run all model evaluations (saves outputs/results.csv)
python run_llm.py

# Analyze outputs and generate summary tables
python analyze_results.py
```

---

## 📄 Academic Report
The comprehensive academic report documenting full experimental methodology, reasoning traces, and evaluations is available in the repository root:
- [Running_an_LLM_Locally_Report.pdf](Running_an_LLM_Locally_Report.pdf)
