# RAG Evaluation & Drift Monitor

A system that continuously scores an existing RAG pipeline's retrieval quality and flags silent degradation before users notice.

## The Problem It Solves

Everyone builds RAG. Almost nobody builds the thing that tells you when it's silently getting worse. This project fills that gap — teams ship RAG pipelines with no visibility into whether retrieval quality is degrading over time due to stale documents or embedding drift.

## Architecture

```
Labeled Eval Set → Run Eval Queries → Score (Precision@k, Faithfulness, Relevance)
       → Compare vs Baseline → Flag Drift → Log to Score History
```

The monitor runs alongside the live RAG pipeline, not inside it. It never touches live queries — it's an observer that runs on a schedule and watches for degradation trends.

**Key design point:** Drift is only visible as a trend, never from a single run. The monitor stores scores over time and compares against a fixed baseline — one bad score means nothing, a consistent downward trend is the signal.

## Project Structure

```
src/
  run_eval.py       # runs eval questions through RAG, captures outputs
  score_eval.py     # scores each run: precision@k, faithfulness, answer relevance
  drift_monitor.py  # compares to baseline, flags drops, logs history
data/
  eval_set.json     # 10 labeled eval pairs (question, ground truth, source section)
```

## Setup

```bash
git clone https://github.com/[your-username]/project-2-rag-drift-monitor
cd project-2-rag-drift-monitor
pip install -r requirements.txt
cp .env.example .env
# add your GROQ_API_KEY to .env
```

## Usage

**Step 1 — Run eval queries through RAG:**
```bash
python src/run_eval.py
# outputs: eval_results.json
```

**Step 2 — Score the results:**
```bash
python src/score_eval.py
# outputs: eval_scores.json
```

**Step 3 — Check for drift:**
```bash
python src/drift_monitor.py
# first run: saves baseline
# subsequent runs: compares vs baseline, flags any metric drop > 0.2
# outputs: baseline_scores.json, score_history.json
```

## Stack

- Python 3.11
- ChromaDB (vector store)
- sentence-transformers / all-MiniLM-L6-v2 (embeddings)
- Groq / llama-3.3-70b-versatile (LLM)
- LangChain (prompt + chain)

## Development

```bash
pytest tests/
```

## Baseline Scores (first run)

| Metric | Score |
|---|---|
| precision@k | 0.62 |
| faithfulness | 0.86 |
| answer_relevance | 0.78 |