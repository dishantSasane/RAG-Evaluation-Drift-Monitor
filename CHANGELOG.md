# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [1.0.0] - 2026-07-06

### Added
- Labeled eval set (10 question/answer pairs across 9 paper sections)
- Eval runner: runs eval questions through ChromaDB + Groq RAG pipeline
- Scoring: precision@k (string match), faithfulness and answer relevance (LLM-as-judge via Groq)
- Drift monitor: baseline storage, run-over-run comparison, drift flagging at 0.2 threshold
- Score history logging with timestamps