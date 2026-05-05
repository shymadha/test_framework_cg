import sys
import os

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser

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
from agentic_ai.orchestrator_state import OrchestratorState


def analysis_agent(state: OrchestratorState) -> OrchestratorState:
    """
    ANALYZING state.

    Performs first-level RCA using framework.log.
    LLM analyzes the log lines and stores RCA as a normal dict in analysis_output.

    This agent does NOT control orchestration flow.
    """

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

    # fallback
    if not log_lines:
        state["analysis_output"] = {
            "root_cause": "Log file is empty. RCA cannot be performed.",
            "evidence": [],
            "confidence": 0.0,
            "summary": "No log content found.",
            "recommended_fix": "Verify that the correct artifact/log file was provided.",
        }
        return state

    llm = ChatOpenAI(
        model="openai.gpt-5.1",
        base_url="https://openai.generative.engine.capgemini.com/v1",
        api_key=api_key,
        default_headers={
            "x-api-key": api_key
        },
    )

    parser = JsonOutputParser()

    system_prompt = """
        You are an expert SRE and log analysis assistant.

        Analyze application/framework logs to identify the most likely root cause.

        Guidelines:
        - Focus only on evidence present in logs: errors, exceptions, stack traces, failed assertions, missing files, 
        timeouts, dependency issues, connection failures, permission/configuration errors, and resource exhaustion.
        - Do not invent details.
        - If inconclusive, state that clearly.
        - Evidence must include the most relevant snippets or observations.
        - Confidence must be between 0 and 1.
        - Recommended fix must be actionable.

        Return ONLY valid JSON, with no markdown or extra text.

        Use this exact structure:
        {
            "root_cause": "string",
            "evidence": ["string"],
            "confidence": 0.0,
            "summary": "string",
            "recommended_fix": "string"
        }
    """

    human_prompt = f"""
        Analyze the following log content and produce a structured RCA.

        Logs:
        {log_lines}
    """

    chain = llm | parser

    try:
        analysis_output = chain.invoke(
            [
                SystemMessage(content=system_prompt),
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
