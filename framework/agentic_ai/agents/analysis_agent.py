import sys
import os

from framework.agentic_ai.llm.gen_engine_llm import GenEngineLLM
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from framework.agentic_ai.prompts.agent_prompts import rca_agent_prompt

from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("api_key")

# Add project root BEFORE any framework imports
current = Path(__file__).resolve()

for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break
from pathlib import Path
from framework.agentic_ai.state.orchestrator_state import OrchestratorState

llm = GenEngineLLM().get_llm_model()

def analysis_agent(state: OrchestratorState) -> OrchestratorState:
    """
    ANALYZING state.

    Performs first-level RCA using framework.log.
    Retrieves relevant context from ChromaDB (device manual) using the log
    content as a query, then passes both log + context to the LLM for RCA.

    This agent does NOT control orchestration flow.
    """
    from framework.agentic_ai.vector_store.retrieval_memory import RetrievalPipeline

    state["status"] = "ANALYZING"

    artifact_path = state.get("artifact_path")
    if not artifact_path:
        raise RuntimeError("analysis_agent called without resolved artifact_path")

    log_file = Path(artifact_path)

    if not log_file.exists():
        raise FileNotFoundError(f"Artifact not found: {log_file}")

    # Read log file
    with log_file.open("r", encoding="utf-8", errors="ignore") as f:
        log_lines = f.readlines()

    # Fallback
    if not log_lines:
        state["analysis_output"] = {
            "root_cause": "Log file is empty. RCA cannot be performed.",
            "evidence": [],
            "confidence": 0.0,
            "summary": "No log content found.",
            "recommended_fix": "Verify that the correct artifact/log file was provided.",
        }
        return state

    log_text = "".join(log_lines)

    # Memory: retrieve relevant context from ChromaDB
    retrieval_context = ""
    try:
        retriever = RetrievalPipeline(
            chroma_dir="./chroma_db",
            collection_name="pdf_store",
            top_k=5,
        )
        query_msg = llm.invoke(
            [
                HumanMessage(
                    content=f"""You are a log analysis assistant. Read the log and extract: (1) what failed, 
                        (2) the incorrect device slave address used. Reply in 2-3 sentences,
                        be concise.":\n{log_text}
                    """
                )
            ]
        )
        query = query_msg.content.strip()
        results = retriever.similarity_search(query)
        retrieval_context = "\n\n".join(r["content"] for r in results)
    except Exception as e:
        # Non-fatal: RCA still proceeds with log only
        print(f"[analysis_agent] RAG retrieval failed, proceeding without context: {e}")

    context_block = (
        f"\n\nRelevant context retrieved from the device manual:\n{retrieval_context}"
        if retrieval_context
        else ""
    )

    human_prompt = f"""
        Analyze the following log content and produce a structured RCA.
        If relevant context from the device manual is provided, use it to identify
        misconfigurations, incorrect addresses, or other discrepancies.

        Logs:
        {log_text}
        {context_block}
    """

    parser = JsonOutputParser()
    chain  = llm | parser

    try:
        analysis_output = chain.invoke(
            [
                SystemMessage(content=rca_agent_prompt),
                HumanMessage(content=human_prompt),
            ]
        )
    except Exception as e:
        analysis_output = {
            "root_cause": "LLM log analysis failed.",
            "evidence": [],
            "confidence": 0.0,
            "summary": f"Failed to parse LLM output: {str(e)}",
            "recommended_fix": "Check LLM response formatting, API configuration, and log input size.",
        }

    state["analysis_output"] = {
        "root_cause": analysis_output.get("root_cause", "Unknown"),
        "evidence": analysis_output.get("evidence", []),
        "confidence": analysis_output.get("confidence", 0.0),
        "summary": analysis_output.get("summary", ""),
        "recommended_fix": analysis_output.get("recommended_fix", ""),
    }

    return state


if __name__ == "__main__":

    state = {
        "artifact_path": "/Users/ishant162/Generative_AI/cg_test_frwk/test_framework_cg/data/log/framework.log",
        "retry_count": 0,
        "status": "INIT",
    }
    state = analysis_agent(state)
    print(state['analysis_output'])