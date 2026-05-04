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
from langgraph.graph import StateGraph, END
from agentic_ai.orchestrator_state import OrchestratorState

from agentic_ai.interpreter_agent import interpreter_agent       # CLASSIFYING
from agentic_ai.executor_agent import executor_agent             # EXECUTING
from agentic_ai.artifact_loader_agent import artifact_loader     # ARTIFACT_READY
from agentic_ai.analysis_agent import analysis_agent             # ANALYZING
from agentic_ai.report_agent import report_agent                 # REPORTING
from agentic_ai.reporting_placeholder import reporting_placeholder #temporary placeholder

def route_by_intent(state: OrchestratorState):
    """
    Routes based on classified intent
    """
    return state["intent"]         # execute | rca | report
	
def route_by_execution_status(state: OrchestratorState):
    """
    Routes based on execution result
    """
    return state["execution_status"]   # PASSED | FAILED

builder = StateGraph(OrchestratorState)
builder.add_node("classifying", interpreter_agent)      # CLASSIFYING
builder.add_node("executing", executor_agent)           # EXECUTING
builder.add_node("artifact_ready", artifact_loader)     # ARTIFACT_READY
builder.add_node("analyzing", analysis_agent)            # ANALYZING
builder.add_node("reporting", report_agent)              # REPORTING
builder.add_node("reporting_placeholder", reporting_placeholder)

builder.set_entry_point("classifying")
builder.add_conditional_edges(
    "classifying",
    route_by_intent,
    {
        "execute": "executing",
        "rca": "artifact_ready",
        "report": "reporting",
    },
)
builder.add_conditional_edges(
    "executing",
    route_by_execution_status,
    {
        "PASSED": "reporting_placeholder", #to use reporting
        "FAILED": "artifact_ready",
    },
)

builder.add_edge("artifact_ready", "analyzing")
builder.add_edge("analyzing", "reporting")
builder.add_edge("reporting", END)
orchestrator_graph = builder.compile()

result = orchestrator_graph.invoke(
    {
        "user_request": "run cpu frequency test on beagle platform using ssh",
        "retry_count": 0,
        "status": "INIT",
    }
)

print(result["status"])   # COMPLETED
#print(result.get("report_path"))
