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
from framework.agentic_ai.state.orchestrator_state import OrchestratorState

from pathlib import Path

def artifact_loader(state):

    state["status"] = "ARTIFACT_READY"

    logs_base = Path("logs")

    if not logs_base.exists():
        raise FileNotFoundError("logs directory not found")

    # ✅ Get all timestamp folders
    execution_dirs = [d for d in logs_base.iterdir() if d.is_dir()]
    
    if not execution_dirs:
        raise FileNotFoundError("No execution folders found in logs/")

    # ✅ Pick latest (timestamp-based sort)
    latest_dir = sorted(execution_dirs, key=lambda d: d.name)[-1]
    
    print(f"✅ Latest execution folder: {latest_dir}")

    framework_log = latest_dir / "framework.log"

    if not framework_log.exists():
        raise FileNotFoundError(f"{framework_log} not found")

    # ✅ Return RELATIVE path (important)
    #relative_path = framework_log.relative_to(Path.cwd())
    relative_path = framework_log
    print(f"✅ Using framework log: {relative_path}")

    return {
        "artifact_path": str(relative_path),
        "status": "ARTIFACT_READY"
    }
    
