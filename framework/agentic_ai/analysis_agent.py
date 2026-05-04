import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add project root BEFORE any framework imports
current = Path(__file__).resolve()

for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break
from pathlib import Path
from typing import Dict, List
from agents.orchestrator_state import OrchestratorState


def analysis_agent(state: OrchestratorState) -> OrchestratorState:
    """
    ANALYZING state.
    Performs first-level RCA using framework.log.
    This agent does NOT control orchestration flow.
    """

    state["status"] = "ANALYZING"

    artifact_path = state.get("artifact_path")
    if not artifact_path:
        raise RuntimeError("analysis_agent called without resolved artifact_path")

    log_file = Path(artifact_path)

    if not log_file.exists():
        raise FileNotFoundError(f"Artifact not found: {log_file}")

    # -------------------------------------------------
    # Read and analyze log file
    # -------------------------------------------------
    with log_file.open("r", encoding="utf-8", errors="ignore") as f:
        log_lines = f.readlines()

    error_lines = _extract_error_lines(log_lines)
    root_cause, confidence = _infer_root_cause(error_lines)

    # -------------------------------------------------
    # Prepare structured RCA output
    # -------------------------------------------------
    state["analysis_output"] = {
        "root_cause": root_cause,
        "evidence": error_lines[:5],  # keep first N lines as evidence
        "confidence": confidence,
    }

    return state
	
def _extract_error_lines(log_lines: List[str]) -> List[str]:
    """
    Extracts lines indicating failure or errors.
    """
    keywords = ["error", "exception", "failed", "timeout", "fatal"]

    return [
        line.strip()
        for line in log_lines
        if any(keyword in line.lower() for keyword in keywords)
    ]


def _infer_root_cause(error_lines: List[str]) -> tuple[str, float]:
    """
    Simple heuristic-based RCA inference.
    Can later be replaced or augmented with ML / LLM.
    """

    if not error_lines:
        return "Unknown failure (no explicit error found)", 0.3

    joined_text = " ".join(error_lines).lower()

    if "timeout" in joined_text:
        return "Service timeout during execution", 0.85
    if "connection refused" in joined_text or "ssh" in joined_text:
        return "SSH connectivity issue", 0.85
    if "cpu" in joined_text and "threshold" in joined_text:
        return "CPU usage exceeded configured threshold", 0.9
    if "permission denied" in joined_text:
        return "Permission issue during execution", 0.9

    return "Unhandled execution error", 0.6