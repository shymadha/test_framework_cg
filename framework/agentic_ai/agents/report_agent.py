"""Reporting agent node"""

import sys
import os
import json

from pathlib import Path
from datetime import datetime

from framework.agentic_ai.llm.gen_engine_llm import GenEngineLLM
from framework.agentic_ai.prompts.agent_prompts import report_agent_prompt
from framework.agentic_ai.tools.jira_tool import jira_tools

from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
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
    """
    print("Generating report based on the RCA")
    
    state["status"] = "REPORTING"
    timestamp = state.get("timestamp") or _resolve_latest_execution()
    state["timestamp"] = timestamp
    
    agent = create_agent(
        model=llm,
        tools=jira_tools,
    )
    
    report_context = report_agent_prompt.format(
        timestamp=timestamp,
        test_name=state.get("test_name", "N/A"),
        test_domain=state.get("test_domain", "N/A"),
        platform=state.get("platform", "N/A"),
        execution_method=state.get("execution_method", "N/A"),
        execution_status=state.get("execution_status", "N/A"),
        execution_output=state.get("execution_output", "No output available."),
        analysis_output=state.get("analysis_output", "No analysis available."),
    )
    
    report_context += """
        Instructions:
        - Always generate a detailed markdown report.
        - If execution_status is FAILED:
            - You MUST call the tool `create_jira_ticket`
            - summary = "Test Failure: <test_name>"
            - description = full report
            - testcase_name = test_name
        - If execution_status is NOT FAILED:
            - DO NOT call any tool
    """

    response = agent.invoke(
        {"messages": [HumanMessage(content=report_context)]},
        handle_tool_errors=True,
        return_intermediate_steps=True,
    )

    final_output = response["messages"][-1].content
    messages = response['messages']
    jira_ticket_info = None

    # Check intermediate steps for Jira ticket creation
    for msg in messages:
        # Identify the Jira tool response
        if msg.__class__.__name__ == "ToolMessage" and msg.name == "create_jira_ticket":
            jira_ticket_info = json.loads(msg.content)
            break

    if jira_ticket_info:
        jira_report_section = f"\n\n## Jira Ticket Details\n\n"
        jira_report_section += f"- **Ticket ID:** {jira_ticket_info.get("ticket_id", "N/A")}\n"
        jira_report_section += f"- **Summary:** {jira_ticket_info.get("summary", "N/A")}\n"
        jira_report_section += f"- **Status:** {jira_ticket_info.get("status", "N/A")}\n"
        jira_report_section += f"- **Test Case:** {jira_ticket_info.get("testcase", "N/A")}\n"
        final_output = final_output + jira_report_section

    # Save report
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    report_path = reports_dir / f"report_{timestamp}.md"
    with report_path.open("w", encoding="utf-8") as f:
        f.write(f"<!-- Generated at: {datetime.utcnow().isoformat()} -->\n\n")
        f.write(final_output)

    state["report_path"] = str(report_path)
    state["status"] = "COMPLETED"
    print("Report Generated")
    return state
