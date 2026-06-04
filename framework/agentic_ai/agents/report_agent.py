import sys
import os
from pathlib import Path
from framework.agentic_ai.llm.gen_engine_llm import GenEngineLLM
from langchain_core.messages import HumanMessage
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add project root BEFORE any framework imports
current = Path(__file__).resolve()

for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break
from pathlib import Path
from datetime import datetime
from framework.agentic_ai.state.orchestrator_state import OrchestratorState

from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("api_key")

llm = GenEngineLLM().get_llm_model()

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
    
    timestamp = state.get("timestamp")
    if not timestamp:
        # Default to latest execution if not already resolved
        timestamp = _resolve_latest_execution()
        state["timestamp"] = timestamp

    # Context for LLM
    report_context = f"""
        You are a test execution reporter. Create a concise professional markdown report.

        Input:
        - Timestamp: {timestamp}
        - Test Name: {state.get("test_name", "N/A")}
        - Test Domain: {state.get("test_domain", "N/A")}
        - Platform: {state.get("platform", "N/A")}
        - Method: {state.get("execution_method", "N/A")}
        - Status: {state.get("execution_status", "N/A")}
        - Execution Output: {state.get("execution_output", "No output available.")}
        - Analysis Output: {state.get("analysis_output", "No analysis available.")}

        Output structure:
        # Test Execution Report

        ## Summary
        3-5 bullets: status, main issue, confidence score + reason.

        ## Root Cause Evidence
        | Root Cause | Key Evidence | Failure Stage |
        |---|---|---|

        ## Recommended Fix
        2-4 actionable bullets.

        ## Execution Details
        Compact metadata table.

        ## Analysis Details
        | Finding | Evidence | Impact |
        |---|---|---|
        Max 3-5 findings.

        ## Conclusion
        2-3 sentences: final assessment, issue category, next step.

        Rules: 
        1. Be brief, avoid repetition, no "Symptom vs Cause", use N/A if unknown, quote only critical logs.
        2. Incase of status=passed, don't include Root Cause Evidence & Recommended Fix.
        
    """
    response = llm.invoke([HumanMessage(content=report_context)]) 
    markdown_report = response.content  
    
    reports_dir = Path("reports") 
    reports_dir.mkdir(exist_ok=True) 
    report_path = reports_dir / f"report_{timestamp}.md" 

    with report_path.open("w", encoding="utf-8") as f: 
        f.write(f"<!-- Generated at: {datetime.utcnow().isoformat()} -->\n\n") 
        f.write(markdown_report) 
    
    state["report_path"] = str(report_path) 
    state["status"] = "COMPLETED" 
    return state
