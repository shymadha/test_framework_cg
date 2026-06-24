"""Artifact Loader Module"""

from pathlib import Path

from framework.agentic_ai.state.orchestrator_state import OrchestratorState


def artifact_loader(state: OrchestratorState) -> OrchestratorState:
    """
    ARTIFACT_READY state.
    Resolves and validates artifacts required for RCA.
    Typically selects the latest framework.log unless a specific
    timestamp/scope is already provided.
    """
    # Transition state
    state["status"] = "ARTIFACT_READY"

    # Base logs directory (adjust if needed)
    logs_base = Path("logs")

    if not logs_base.exists():
        raise FileNotFoundError("Logs directory does not exist")


    execution_dir: Path | None = None

    if state.get("timestamp"):
        candidate = logs_base / state["timestamp"]
        if not candidate.exists():
            raise FileNotFoundError(
                f"Execution folder not found for timestamp: {state['timestamp']}"
            )
        execution_dir = candidate
    else:
        # Pick latest execution folder (lexicographically sortable timestamps)
        execution_dirs = [d for d in logs_base.iterdir() if d.is_dir()]
        if not execution_dirs:
            raise FileNotFoundError("No execution runs found")

        execution_dir = sorted(execution_dirs, key=lambda d: d.name)[-1]
        state["timestamp"] = execution_dir.name

    framework_log = execution_dir / "framework.log"

    if not framework_log.exists():
        raise FileNotFoundError(f"framework.log not found in {execution_dir}")

    state["artifact_path"] = str(framework_log)

    return state
