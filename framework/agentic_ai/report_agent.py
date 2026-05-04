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
from datetime import datetime
import json
from agentic_ai.orchestrator_state import OrchestratorState

def _resolve_latest_execution() -> str:
    reports_dir = Path("reports")

    if not reports_dir.exists():
        raise RuntimeError("No reports directory found; cannot resolve latest execution")

    reports = sorted(
        reports_dir.glob("report_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not reports:
        raise RuntimeError("No existing reports found; cannot resolve latest execution")

    # Extract timestamp from filename: report_<timestamp>.json
    latest = reports[0].stem.replace("report_", "")
    return latest


def report_agent(state: OrchestratorState) -> OrchestratorState:
    """
    REPORTING state.
    Generates a final report for the resolved execution scope.
    Always runs as the terminal convergence node.
    """

    state["status"] = "REPORTING"

    # -------------------------------------------------
    # Resolve report scope
    # -------------------------------------------------
    timestamp = state.get("timestamp")

    if not timestamp:
        # Default to latest execution if not already resolved
        timestamp = _resolve_latest_execution()
        state["timestamp"] = timestamp

    # -------------------------------------------------
    # Assemble report content
    # -------------------------------------------------
    report_data = {
        "execution_timestamp": timestamp,
        "test_name": state.get("test_name"),
        "test_domain": state.get("test_domain"),
        "platform": state.get("platform"),
        "execution_method": state.get("execution_method"),
        "execution_status": state.get("execution_status"),
        "execution_output": state.get("execution_output"),
        "analysis_output": state.get("analysis_output"),
        "generated_at": datetime.utcnow().isoformat(),
    }

    # -------------------------------------------------
    # Persist report artifact
    # -------------------------------------------------
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    report_path = reports_dir / f"report_{timestamp}.json"

    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    state["report_path"] = str(report_path)
    state["status"] = "COMPLETED"

    return state
