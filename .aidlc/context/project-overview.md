# Aster FW — Project Overview

## What It Does
Agentic AI test execution and analysis framework for hardware-focused validation. Provides an Agentic UI (LLM-driven) and a Manual Test Runner UI, orchestrates tests against a user-defined testbed (typically a BeagleBone over SSH), captures logs and generates markdown reports, and optionally enriches root-cause analysis with a local vector store.

## Tech Stack
- Language: Python 3
- LLM/Agent: LangGraph, LangChain (+ OpenAI-compatible endpoint)
- UI: Gradio (agentic UI), Flask (supporting), CLI entrypoints
- Data/Vector: ChromaDB (optional)
- Tests: pytest (security tests under tests/security)
- Integrations: Jira (optional; values loaded from .env at import time)
- Utilities: Paramiko (SSH), serial, NumPy, scikit-learn, HDBSCAN, Drain3, ruff

## Project Scope
- In scope: Agentic UI (framework/ui/ui_agentic_ai.py), Manual Test Runner UI (framework/ui/ui.py), test discovery and execution via framework.core.test_engine.TestEngine, log and report generation under logs/ and reports/, optional vector store ingestion and retrieval, Jira integration (if configured), BeagleBone-based test execution via SSH per userinput/testbed.json.
- Out of scope: Mock hardware execution (real hardware required for test execution), cloud-hosted persistence/services beyond optional Jira, non-Python clients, multi-repo microservice orchestration.
