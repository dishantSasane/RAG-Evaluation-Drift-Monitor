# RAG Evaluation & Drift Monitor

An enterprise-grade, out-of-band observer system that continuously evaluates an existing Retrieval-Augmented Generation (RAG) pipeline, measuring retrieval quality and grounding accuracy while detecting silent performance degradation before it reaches end users.

> Built around a banking knowledge-base RAG pipeline using the corporate policy document:
> **HDFC Bank Fixed Deposit & Recurring Deposit Terms and Conditions** (`data/Practice.pdf`)

---

# Overview

Most RAG systems focus on generating answers.

Very few monitor whether those answers remain reliable over time.

As embeddings change, documents evolve, indexes are rebuilt, or retrieval parameters are modified, answer quality can slowly degrade without obvious failures. Since users only see incorrect answers after deployment, identifying these regressions becomes difficult.

This project serves as an **independent evaluation layer** that continuously measures the health of a RAG system using a fixed golden evaluation dataset.

Instead of serving users directly, it periodically executes evaluation queries, scores the pipeline using multiple quality metrics, records historical performance, and detects statistically significant declines that may indicate retrieval drift or grounding failures.

---

# Problem Statement

Production RAG systems commonly experience issues such as:

- Retrieval quality degrading after vector database updates
- Embedding model replacements changing nearest-neighbor behavior
- Knowledge base modifications introducing retrieval inconsistencies
- Hallucinations increasing despite unchanged prompts
- Lack of historical visibility into pipeline quality

Without continuous evaluation, these failures remain hidden until users begin reporting incorrect responses.

This repository addresses that problem by introducing an automated monitoring workflow that operates independently of the live inference pipeline.

---

# System Architecture

The evaluation pipeline runs **outside** the production request path.

It never increases user latency and never interferes with inference.

```text
                 data/eval_set.json
                         │
                         ▼
                 Evaluation Runner
                    (main.py)
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
  Vector Retrieval   Response Generation   Quality Evaluation
(vector_store.py)     (rag_engine.py)      (evaluator.py)
        │                │                │
        └────────────────┼────────────────┘
                         ▼
               Statistical Drift Detection
                         │
                         ▼
               score_history.json
```

---

# Repository Structure

```text
rag-evaluation-drift-monitor/
│
├── data/
│   ├── banking.pdf
│   └── eval_set.json
│
├── src/
│   ├── extractor.py
│   ├── vector_store.py
│   ├── rag_engine.py
│   └── evaluator.py
│
├── config.py
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

# How It Works

The evaluation workflow executes the following sequence:

1. Load the fixed evaluation dataset.
2. Retrieve relevant document chunks from ChromaDB.
3. Generate answers using the LLM.
4. Score each response using an LLM-as-a-Judge.
5. Aggregate evaluation metrics.
6. Append scores to historical records.
7. Compare current performance against previous runs.
8. Raise drift alerts when sustained degradation is detected.

---

# Features

- Independent evaluation pipeline
- Automatic ChromaDB initialization
- Golden evaluation dataset
- LLM-as-a-Judge scoring
- Historical performance tracking
- Statistical drift detection
- Persistent score history
- Modular architecture
- Framework-independent API communication
- Production-oriented repository structure

---

# Installation

## 1. Create Environment

```bash
conda create -n rag-monitor python=3.11 -y
conda activate rag-monitor
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 3. Configure Environment Variables

```bash
cp .env.example .env
```

Add your API key:

```text
API_KEY=your_api_key_here
```

---

# Running the Project

Execute the complete evaluation pipeline:

```bash
python main.py
```

---

# Runtime Workflow

During execution the system performs the following operations:

### Vector Store Initialization

`vector_store.py` checks whether the ChromaDB collection already exists.

If the collection is empty:

- PDF is parsed
- Text is chunked
- Embeddings are generated
- Database is populated

If the collection already exists, initialization is skipped.

---

### Evaluation Execution

Each evaluation question is processed sequentially.

For every question:

- retrieve context
- generate answer
- evaluate quality
- record scores

A small delay is inserted between requests to reduce API rate-limit issues.

---

### Metric Aggregation

After all evaluation samples complete, the system computes average scores for every metric.

These metrics are then written to the historical score log.

---

### Drift Detection

Instead of reacting to a single low score, the monitor compares current performance with historical averages.

A sustained decline across multiple evaluation runs indicates possible retrieval drift or grounding degradation.

---

# Evaluation Metrics

| Metric | Description | Failure Indicates |
|---------|-------------|-------------------|
| **precision_at_k** | Measures how many retrieved chunks are actually relevant to the query. | Retrieval quality degradation |
| **faithfulness** | Measures whether generated claims are supported by retrieved context. | Hallucination or poor grounding |
| **answer_relevance** | Measures how directly the generated answer addresses the user query. | Prompt or generation issues |

---

# Baseline Performance

Current reference scores:

```json
{
  "precision_at_k": 0.7730158730111,
  "faithfulness": 0.6000000000000,
  "answer_relevance": 1.0000000000000
}
```

### Interpretation

- **Answer Relevance = 1.00**

  Generated answers consistently address the evaluation questions.

- **Precision@K ≈ 0.77**

  Most retrieved chunks contain relevant information, though retrieval still has room for improvement.

- **Faithfulness = 0.60**

  Responses occasionally introduce unsupported information beyond the retrieved context, indicating opportunities to improve grounding.

---

# Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11 |
| Environment | Anaconda |
| Vector Database | ChromaDB |
| Embedding Model | sentence-transformers (all-MiniLM-L6-v2) |
| LLM | poolside/laguna-xs-2.1:free |
| API Provider | OpenRouter |
| HTTP Client | requests |

---

# Future Improvements

Potential extensions include:

- Grafana dashboard integration
- Prometheus metrics export
- Email or Slack drift notifications
- CI/CD evaluation pipeline
- Multiple benchmark datasets
- Precision@K visualization
- Recall and MRR metrics
- Scheduled execution with cron jobs
- Multi-document evaluation support

---

# License

This project is licensed under the MIT License.

See the `LICENSE` file for more information.
