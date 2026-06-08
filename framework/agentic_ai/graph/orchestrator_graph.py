"""Orchestrator Graph Module"""

import sys
import os
from pathlib import Path

from langgraph.graph import StateGraph, END
from framework.agentic_ai.state.orchestrator_state import OrchestratorState

from framework.agentic_ai.agents.orchestrator_agent import (
    orchestrator_agent,
)
from framework.agentic_ai.agents.executor_agent import executor_agent
from framework.agentic_ai.agents.artifact_loader_agent import (
    artifact_loader,
)
from framework.agentic_ai.agents.analysis_agent import analysis_agent
from framework.agentic_ai.agents.report_agent import report_agent
from framework.agentic_ai.agents.reporting_placeholder import (
    reporting_placeholder,
)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add project root BEFORE any framework imports
current = Path(__file__).resolve()

for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break


def route_by_intent(state: OrchestratorState):
    """
    Routes based on classified intent
    """
    return state["intent"]  # execute | rca | report


def route_by_execution_status(state: OrchestratorState):
    """
    Routes based on execution result
    """
    return state["execution_status"]


builder = StateGraph(OrchestratorState)
builder.add_node("classifying_intent", orchestrator_agent)
builder.add_node("executor_agent", executor_agent)
builder.add_node("artifact_ready", artifact_loader)
builder.add_node("analysis_agent", analysis_agent)
builder.add_node("reporting_agent", report_agent)
builder.add_node("reporting_artificact_ready", reporting_placeholder)

builder.set_entry_point("classifying_intent")
builder.add_conditional_edges(
    "classifying_intent",
    route_by_intent,
    {
        "execute": "executor_agent",
        "rca": "artifact_ready",
        "report": "reporting_agent",
    },
)
builder.add_conditional_edges(
    "executor_agent",
    route_by_execution_status,
    {
        "PASSED": "reporting_artificact_ready",
        "FAILED": "artifact_ready",
    },
)
builder.add_edge("reporting_artificact_ready", "reporting_agent")
builder.add_edge("artifact_ready", "analysis_agent")
builder.add_edge("analysis_agent", "reporting_agent")
builder.add_edge("reporting_agent", END)
orchestrator_graph = builder.compile()
