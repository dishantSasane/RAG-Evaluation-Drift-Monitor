# RAG Evaluation & Drift Monitor

An out-of-band monitoring system that continuously evaluates a RAG pipeline for silent quality degradation — before users notice.

> Built on a banking knowledge base: HDFC Bank Fixed Deposit & Recurring Deposit Terms and Conditions.

---

## The problem

Production RAG pipelines degrade silently. Swap an embedding model, rebuild a vector index, or update your document corpus — retrieval quality drops, hallucinations increase, and no error is raised. Users just start getting worse answers.

This system catches that by running a fixed evaluation dataset against the pipeline on every cycle, tracking metric history, and alerting when sustained decline is detected.

---

## What this adds over standalone RAGAS

| | RAGAS alone | This system |
|---|---|---|
| Score a single run | ✅ | ✅ |
| Track scores over time | ❌ | ✅ |
| Detect drift across runs | ❌ | ✅ |
| Out-of-band (no latency impact) | ❌ | ✅ |
| Historical score persistence | ❌ | ✅ |

---

## Sample output

```
=== RAG Evaluation Report ===
Run ID     : eval_20240315_001
Timestamp  : 2024-03-15 14:32:07

Metric              Score    Baseline   Delta    Status
─────────────────────────────────────────────────────
Answer Relevance    1.00     1.00       +0.00    ✅ STABLE
Precision@K         0.77     0.85       -0.08    ⚠️  DRIFT DETECTED
Faithfulness        0.60     0.71       -0.11    🔴 ALERT

Drift detected on 2 metrics. Possible causes:
  - Embedding model update
  - Document corpus change
  - Vector index rebuild

Scores written to score_history.json
```

---

## Architecture

```
data/eval_set.json
        │
        ▼
  Evaluation Runner (main.py)
        │
  ┌─────┼──────┐
  ▼     ▼      ▼
Retrieval  Generation  Scoring
(ChromaDB) (LLM)       (LLM-as-Judge)
        │
        ▼
  Drift Detection
        │
        ▼
  score_history.json
```

Runs entirely outside the production request path — never touches user latency.

---

## Evaluation metrics

| Metric | What it measures | Low score means |
|---|---|---|
| `precision_at_k` | Fraction of retrieved chunks that are relevant | Retrieval degradation |
| `faithfulness` | Generated claims grounded in retrieved context | Hallucination / poor grounding |
| `answer_relevance` | Answer directly addresses the query | Prompt or generation issues |

**Baseline:**
```json
{
  "precision_at_k": 0.773,
  "faithfulness": 0.600,
  "answer_relevance": 1.000
}
```

---

## Stack

| Component | Technology |
|---|---|
| Language | Python 3.11 |
| Vector Database | ChromaDB |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| LLM | poolside/laguna-xs-2.1 via OpenRouter |
| HTTP Client | requests |

---

## Setup

```bash
conda create -n rag-monitor python=3.11 -y
conda activate rag-monitor
pip install -r requirements.txt
cp .env.example .env
# Add API_KEY=your_openrouter_key to .env
```

Run:
```bash
python main.py
```

---

## Repository structure

```
├── data/
│   ├── banking.pdf
│   └── eval_set.json
├── src/
│   ├── extractor.py
│   ├── vector_store.py
│   ├── rag_engine.py
│   └── evaluator.py
├── config.py
├── main.py
└── requirements.txt
```

---

## Roadmap

- [ ] Grafana / Prometheus metrics export
- [ ] Slack / email alerts on drift threshold breach
- [ ] Precision@K visualization over time
- [ ] Multi-document benchmark support
- [ ] Scheduled evaluation via cron

---

## License

MIT
