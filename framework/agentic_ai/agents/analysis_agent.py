"""RCA agent node"""

import json
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser

from framework.agentic_ai.llm.gen_engine_llm import GenEngineLLM
from framework.agentic_ai.prompts.agent_prompts import rca_agent_prompt
from framework.agentic_ai.security.validators import (
    RCAPoisoningError,
    sanitize_log_text,
    validate_rca_output,
)
from framework.agentic_ai.state.orchestrator_state import OrchestratorState
from framework.agentic_ai.vector_store.retrieval_memory import \
    RetrievalPipeline

# Minimum confidence score required to accept a Tier 1 historical match
TIER1_CONFIDENCE_THRESHOLD = 0.90


def analysis_agent(state: OrchestratorState) -> dict:
    """
    Performs Root Cause Analysis (RCA) on test log.

    Tiered Logic:
    1. Check historical analysis (historical_store): If exact match AND
       confidence > TIER1_CONFIDENCE_THRESHOLD, return it.
    2. Fallback to context-aware analysis (doc_store): Retrieve documentation
       context and perform RCA.
    3. Final fallback: Fresh LLM analysis on logs only.
    4. Validate RCA output for poisoning before committing or returning.
    5. Commit fresh results back to historical analysis store.
    """

    print("\n RCA agent started")

    if state.get("execution_status") != "FAILED":
        print("Execution passed → Skipping RCA")
        return {
            "analysis_output": {
                "root_cause": "No failure",
                "confidence": 1.0,
                "summary": "Test passed successfully",
                "evidence": [],
                "recommended_fix": "No action needed",
            },
            "status": "ANALYZING",
        }

    artifact_path = state.get("artifact_path")
    if not artifact_path:
        raise RuntimeError("artifact_path missing in state")

    log_file = Path(artifact_path)
    if not log_file.is_absolute():
        log_file = Path.cwd() / log_file

    if not log_file.exists():
        raise FileNotFoundError(f"Log file not found: {log_file}")

    with log_file.open("r", encoding="utf-8", errors="ignore") as f:
        raw_log_text = f.read()

    # --- Security: sanitize log content before any LLM use ---
    log_text = sanitize_log_text(raw_log_text)

    if not log_text.strip():
        return {
            "status": "ANALYZING",
            "analysis_output": {"root_cause": "Empty log file"},
        }

    print("Tier 1: Checking for exact historical match...")
    hist_retriever = RetrievalPipeline(
        chroma_dir="./chroma_db",
        collection_name="historical_store",
        top_k=1,
    )

    query = f"Failure analysis for log: {log_text[:2000]}"
    try:
        if hist_retriever.collection.count() > 0:
            hist_results = hist_retriever.similarity_search(query)
            if hist_results:
                candidate = hist_results[0]
                meta = candidate.get("metadata", {})
                # Only accept if test_name matches AND confidence exceeds threshold
                hist_confidence = float(meta.get("confidence", 0.0))
                if (
                    meta.get("test_name") == state.get("execution_output", {}).get("test")
                    and hist_confidence >= TIER1_CONFIDENCE_THRESHOLD
                ):
                    print(f"Exact historical match found (confidence={hist_confidence})")
                    cached = json.loads(candidate["content"])
                    # --- Security: validate cached RCA before returning it ---
                    try:
                        cached = validate_rca_output(cached)
                    except RCAPoisoningError as exc:
                        print(f"[SECURITY] Cached RCA poisoned, discarding: {exc}")
                        # Fall through to fresh analysis
                    else:
                        return {"analysis_output": cached, "status": "ANALYZING"}
                else:
                    print(
                        f"Historical match confidence {hist_confidence:.2f} "
                        f"below threshold {TIER1_CONFIDENCE_THRESHOLD} → continuing"
                    )
        else:
            print("historical store is empty. Skipping Tier 1.")
    except Exception as e:
        print(f"Historical search failed: {e}")

    print("Tier 2: No exact match. Attempting context-aware analysis...")
    doc_retriever = RetrievalPipeline(
        chroma_dir="./chroma_db",
        collection_name="doc_store",
        top_k=2,
    )

    retrieval_context = ""
    try:
        if doc_retriever.collection.count() > 0:
            doc_results = doc_retriever.similarity_search(log_text[:2000])
            relevant_docs = [r for r in doc_results]
            if relevant_docs:
                print(f"Found {len(relevant_docs)} relevant documentation snippets.")
                retrieval_context = "\n\n".join(r["content"] for r in relevant_docs)
        else:
            print("doc_store is empty. Skipping Tier 2.")
    except Exception as e:
        print(f"Documentation retrieval failed: {e}")

    if retrieval_context:
        print("Performing context-aware RCA...")
        context_block = f"\n\nRelevant Documentation Context:\n{retrieval_context}"
    else:
        print("No relevant context found. Performing fresh LLM analysis...")
        context_block = ""

    human_prompt = f"""
        Analyze the following log content and produce a structured RCA.
        If relevant context from the device manual is provided, use it to identify
        misconfigurations, incorrect addresses, or other discrepancies.

        Logs:
        {log_text}

        Context:
        {context_block}
    """

    parser = JsonOutputParser()
    llm = GenEngineLLM().get_llm_model()
    chain = llm | parser

    try:
        analysis_output = chain.invoke(
            [
                SystemMessage(content=rca_agent_prompt),
                HumanMessage(content=human_prompt),
            ]
        )
    except Exception as e:
        print(f"LLM RCA failed: {e}")
        analysis_output = {"root_cause": "LLM analysis failed", "summary": str(e)}

    # --- Security: validate LLM RCA output before storing or returning ---
    try:
        analysis_output = validate_rca_output(analysis_output)
    except RCAPoisoningError as exc:
        print(f"[SECURITY] RCA output failed validation: {exc}")
        analysis_output = {
            "root_cause": "RCA output rejected by security validator",
            "evidence": [],
            "confidence": 0.0,
            "summary": str(exc),
            "recommended_fix": "Review logs manually",
        }

    try:
        print("Committing analysis to historical store...")
        hist_retriever.add_document(
            text=json.dumps(analysis_output),
            metadata={
                "type": "historical_analysis",
                "test_name": state.get("test_name", "unknown"),
                "has_context": bool(retrieval_context),
                "confidence": analysis_output.get("confidence", 0.0),
            },
        )
    except Exception as e:
        print(f"Commit failed: {e}")

    return {"analysis_output": analysis_output, "status": "ANALYZING"}
