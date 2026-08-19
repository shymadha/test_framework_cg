# Aster FW — Architecture

## System Diagram
```
+----------------------+
|        UI Layer      |
|  - Agentic UI        |  framework/ui/ui_agentic_ai.py
|  - Manual UI         |  framework/ui/ui.py
+----------+-----------+
           |
           v
+----------+-----------+
|   Orchestration      |
|  - LangGraph agents  |
|  - Executor/Analysis |
|  - Reporting         |
+----------+-----------+
           |
           v
+----------+-----------+
|   Test Engine        |
|  framework/core/     |
|  - TestEngine        |
|  - Test discovery    |
+----------+-----------+
           |
           v
+----------+-----------+
|   Device/IO Layer    |
|  - SSH (Paramiko)    |
|  - Serial            |
+----------+-----------+
           |
           v
+----------+-----------+
|  Storage & Reports   |
|  - logs/<ts>/        |
|  - reports/*.md      |
|  - chroma_db         |
+----------------------+
```

## Layers
- UI layer (Gradio-based Agentic UI and Manual UI) for user interaction.
- Orchestration layer (LangGraph/LangChain) for agent flows, execution, analysis, and reporting.
- Core test engine manages discovery (framework/tests/<domain>, classes ending with Test) and runs selected tests.
- Device/IO integrates with hardware via SSH and Serial.
- Storage handles logs, reports, and optional vector store.

## Key Patterns
- Layered architecture within a monolith.
- Convention-based test discovery (module path + class name suffix).
- Environment-driven configuration via .env loaded at import time (Jira integration requires presence even if unused).
- Relative path reliance for logs/reports/DB; enforced via running from aster_fw CWD.

## ADRs
(Add architectural decision records here as decisions are made)
