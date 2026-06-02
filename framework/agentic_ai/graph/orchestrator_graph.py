import sys
import os
from pathlib import Path

# --------------------------------------------------
# ✅ Path Setup
# --------------------------------------------------
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break

# --------------------------------------------------
# ✅ Imports
# --------------------------------------------------
from langgraph.graph import StateGraph, END
from framework.agentic_ai.state.orchestrator_state import OrchestratorState

from framework.agentic_ai.agents.interpreter_agent import interpreter_agent
from framework.agentic_ai.agents.executor_agent import executor_agent
from framework.agentic_ai.agents.artifact_loader_agent import artifact_loader
from framework.agentic_ai.agents.analysis_agent import analysis_agent
from framework.agentic_ai.agents.report_agent import report_agent


# ==================================================
# ✅ STEP ROUTER (FINAL VERSION)
# ==================================================
def step_router(state):

    plan = state.get("execution_plan", [])
    idx = state.get("current_step_index", 0)
    exec_status = state.get("execution_status")

    print("\n🔍 ROUTER DEBUG")
    print("PLAN:", plan)
    print("INDEX:", idx)
    print("EXEC STATUS:", exec_status)

    # ✅ Modify plan after execution
    if idx == 1 and len(plan) == 1:

        if exec_status == "FAILED":
            print("❌ Execution failed → RCA + Report")

            state["execution_plan"] = [
                "execute_test",
                "artifact_loader",
                "analysis_agent",
                "generate_report"
            ]

        elif exec_status == "PASSED":
            print("✅ Execution passed → artifact_loader + Report")

            state["execution_plan"] = [
                "execute_test",
                "artifact_loader",
                "generate_report"
            ]

        plan = state["execution_plan"]

    # ✅ End condition
    if idx >= len(plan):
        print("✅ All steps completed → END")
        state["current_step"] = "END"
        return state

    step = plan[idx]
    state["current_step"] = step

    print(f"➡️ Routing to step: {step}")

    return state



# ==================================================
# ✅ STEP COMPLETE
# ==================================================
def step_complete(state: OrchestratorState):
    idx = state.get("current_step_index", 0)
    print(f"✅ Completed step index: {idx}")
    state["current_step_index"] = idx + 1
    return state


# ==================================================
# ✅ BUILD GRAPH
# ==================================================
builder = StateGraph(OrchestratorState)

# --------------------------------------------------
# Nodes
# --------------------------------------------------
builder.add_node("classifying_intent", interpreter_agent)
builder.add_node("step_router", step_router)
builder.add_node("step_complete", step_complete)

builder.add_node("execute_test", executor_agent)

# ✅ CRITICAL: use real nodes (not wrapper)
builder.add_node("artifact_loader", artifact_loader)
builder.add_node("analysis_agent", analysis_agent)
builder.add_node("generate_report", report_agent)


# --------------------------------------------------
# Entry
# --------------------------------------------------
builder.set_entry_point("classifying_intent")
builder.add_edge("classifying_intent", "step_router")


# --------------------------------------------------
# ✅ Dynamic Routing
# --------------------------------------------------
builder.add_conditional_edges(
    "step_router",
    lambda state: state.get("current_step"),
    {
        "execute_test": "execute_test",
        "artifact_loader": "artifact_loader",
        "analysis_agent": "analysis_agent",
        "generate_report": "generate_report",
        "END": END,
    },
)


# --------------------------------------------------
# ✅ Execution Flow
# --------------------------------------------------

# ✅ execution
builder.add_edge("execute_test", "step_complete")

# ✅ artifact → analysis
builder.add_edge("artifact_loader", "step_complete")
builder.add_edge("analysis_agent", "step_complete")

# ✅ reporting
builder.add_edge("generate_report", "step_complete")

# ✅ loop
builder.add_edge("step_complete", "step_router")


# --------------------------------------------------
# ✅ Compile
# --------------------------------------------------
orchestrator_graph = builder.compile()