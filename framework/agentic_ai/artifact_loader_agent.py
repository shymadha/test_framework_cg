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
from agents.orchestrator_state import OrchestratorState


def artifact_loader(state: OrchestratorState) -> OrchestratorState:
    """
    ARTIFACT_READY state.
    Resolves and validates artifacts required for RCA.
    Typically selects the latest framework.log unless a specific
    timestamp/scope is already provided.
    """

    # Transition state
    state["status"] = "ARTIFACT_READY"

    artifact_type = state.get("artifact_type")

    if artifact_type != "framework_log":
        raise RuntimeError("artifact_loader called without framework_log requirement")

    # Base logs directory (adjust if needed)
    logs_base = Path("logs")

    if not logs_base.exists():
        raise FileNotFoundError("Logs directory does not exist")

    # -------------------------------------------------
    # Resolve execution scope
    # -------------------------------------------------
    # 1. Explicit timestamp (from report/rca request)
    # 2. Otherwise, latest execution directory
    # -------------------------------------------------

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

    # -------------------------------------------------
    # Resolve framework.log
    # -------------------------------------------------
    framework_log = execution_dir / "framework.log"

    if not framework_log.exists():
        raise FileNotFoundError(f"framework.log not found in {execution_dir}")

    # -------------------------------------------------
    # Update orchestrator state
    # -------------------------------------------------
    state["artifact_path"] = str(framework_log)

    return state
