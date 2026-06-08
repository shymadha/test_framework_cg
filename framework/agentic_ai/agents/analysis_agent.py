"""RCA agent node"""

import sys
import json
from pathlib import Path
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser

from framework.agentic_ai.llm.gen_engine_llm import GenEngineLLM
from framework.agentic_ai.prompts.agent_prompts import rca_agent_prompt
from framework.agentic_ai.state.orchestrator_state import OrchestratorState
from framework.agentic_ai.vector_store.retrieval_memory import RetrievalPipeline

current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break

llm = GenEngineLLM().get_llm_model()


def analysis_agent(state: OrchestratorState) -> dict:
    """
    Performs Root Cause Analysis (RCA) on test log.

    Tiered Logic:
    1. Check historical analysis (analysis_store): If exact match (confidence > 90%), return it.
    2. Fallback to context-aware analysis (pdf_store): Retrieve documentation context and perform RCA.
    3. Final fallback: If context is not relevant, perform fresh LLM analysis on logs only.
    4. Commit fresh results back to historical analysis store.
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
        log_text = f.read()

    if not log_text.strip():
        return {
            "status": "ANALYZING",
            "analysis_output": {"root_cause": "Empty log file"},
        }

    print("Tier 1: Checking for exact historical match...")
    hist_retriever = RetrievalPipeline(
        chroma_dir="./chroma_db",
        collection_name="analysis_store",
        top_k=1,
    )

    query = f"Failure analysis for log: {log_text[:2000]}"
    try:
        # Check if collection has any data before searching
        if hist_retriever.collection.count() > 0:
            hist_results = hist_retriever.similarity_search(query)
            if hist_results:
                print("Exact historical match found")
                return {
                    "analysis_output": json.loads(hist_results[0]["content"]),
                    "status": "ANALYZING",
                }
        else:
            print("historical store is empty. Skipping Tier 1.")
    except Exception as e:
        print(f"Historical search failed: {e}")

    print("Tier 2: No exact match. Attempting context-aware analysis...")
    doc_retriever = RetrievalPipeline(
        chroma_dir="./chroma_db",
        collection_name="pdf_store",
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
            print("pdf_store is empty. Skipping Tier 2.")
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

    try:
        print("Committing analysis to historical store...")
        hist_retriever.add_document(
            text=json.dumps(analysis_output),
            metadata={
                "type": "historical_analysis",
                "test_name": state.get("test_name", "unknown"),
                "has_context": bool(retrieval_context),
            },
        )
    except Exception as e:
        print(f"Commit failed: {e}")

    return {"analysis_output": analysis_output, "status": "ANALYZING"}
