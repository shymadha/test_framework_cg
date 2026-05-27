# agentic_ai/recovery_agent.py
def recovery_agent(state):
    if state["retry_count"] < 2:
        return {
            "retry_count": state["retry_count"] + 1,
            "current_step": "executor_agent"
        }

    return {"status": "FAILED"}