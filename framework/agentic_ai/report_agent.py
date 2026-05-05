import sys
import os
from pathlib import Path
from langchain_openai import ChatOpenAI
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
from agentic_ai.orchestrator_state import OrchestratorState

from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("api_key")

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
        You are a test execution reporter. Generate a clean, structured markdown report based on the
        following execution data
        
        **Execution Data:**
        - Timestamp : {timestamp}
        - Test Name : {state.get("test_name", "N/A")}
        - Test Domain: {state.get("test_domain", "N/A")}
        - Platform : {state.get("platform", "N/A")}
        - Execution Method : {state.get("execution_method", "N/A")}
        - Execution Status : {state.get("execution_status", "N/A")}
        
        **Execution Output:** {state.get("execution_output", "No output available.")} 
        **Analysis Output:** {state.get("analysis_output", "No analysis available.")} 
        **Instructions:** 
        - Use proper markdown headings (# ## ###) 
        - Include a summary section at the top 
        - Include a detailed findings section 
        - Include a conclusion / recommendations section 
        - Use tables, bullet points, and code blocks where appropriate 
        - Keep the tone professional and concise
    """

    llm = ChatOpenAI(
        model="openai.gpt-5.1",
        base_url="https://openai.generative.engine.capgemini.com/v1",
        api_key=api_key,
        default_headers={
            "x-api-key": api_key
        },
    )
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
