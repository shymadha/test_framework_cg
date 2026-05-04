# agentic_ai/planner_agent.py
def planner_agent(state):
    if state["intent"] != "execute":
        return {}

    plan = [
        "executor_agent"
        #"report_agent"
    ]

    return {
        "execution_plan": plan,
        "current_step": plan[0]
    }
