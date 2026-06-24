"""Executor Agent Node"""

from langchain.agents import create_agent

from framework.agentic_ai.llm.gen_engine_llm import GenEngineLLM
from framework.agentic_ai.tools.test_engine_tool import test_engine_tool
from framework.core.logger import setup_logger
from framework.core.test_engine import TestEngine


def extract_tool_output(response):
    import json

    from langchain_core.messages import ToolMessage

    for msg in reversed(response.get("messages", [])):
        if isinstance(msg, ToolMessage):
            try:
                return json.loads(msg.content)
            except:
                return msg.content
    return None


def executor_agent(state):

    from datetime import datetime
    from pathlib import Path

    import framework.core.logger as logger_module

    print("Executor Agent Started")

    llm = GenEngineLLM().get_llm_model()

    agent = create_agent(
        model=llm,
        tools=test_engine_tool,
        system_prompt="""
            You are a test execution agent.

            STRICT RULES:
            - ALWAYS call run_test_tool
            - DO NOT invent values
            - Use domain and test_name exactly as provided
        """,
    )

    log_dir = state.get("log_dir")

    if not log_dir:
        print("log_dir not found → creating new one")

        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_dir_path = Path("logs") / ts
        log_dir_path.mkdir(parents=True, exist_ok=True)

        log_dir = str(log_dir_path)
        state["log_dir"] = log_dir

    logger_module._LOG_DIR = log_dir

    logger = setup_logger("ExecutorAgent")

    try:
        if state.get("execution_done"):
            print("⚠️ Skipping duplicate execution")
            return state

        logger.info("Initializing TestEngine")
        TestEngine()

        domain = state["test_domain"]
        test_name = state["test_name"]

        print(f"Test domain is:{domain}")
        print(f"Test name is:{test_name}")

        response = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": f"""
                            Execute test with:
                            domain = {domain}
                            test_name = {test_name}
                            log_dir={state["log_dir"]}

                            Use these EXACT values.
                        """,
                    }
                ]
            }
        )
        output = extract_tool_output(response)
        if not output:
            raise RuntimeError("No tool output found")

        result = output.get("result")
        status = output.get("status")
        print(f"Test result is {result}")
        print(f"Test status is {status}")

        logger.info(f"Execution result: {result}")

        logs_base = Path("logs")

        execution_dirs = [d for d in logs_base.iterdir() if d.is_dir()]
        latest_dir = sorted(execution_dirs, key=lambda d: d.name)[-1]

        log_dir = str(latest_dir)
        logger.info("=" * 50)
        logger.info(f"END OF TEST: {test_name}")
        logger.info("=" * 50)

        return {
            "execution_status": "PASSED" if status == "SUCCESS" else "FAILED",
            "execution_output": {
                "domain": domain,
                "test": test_name,
                "status": "SUCCESS",
            },
            "log_dir": log_dir,
            "execution_done": True,
            "status": "DONE",
        }

    except Exception as e:
        logger.exception("Test execution failed")

        return {
            "execution_status": "FAILED",
            "execution_output": {"status": "FAILED", "error": str(e)},
            "log_dir": log_dir,
            "execution_done": True,
            "status": "FAILED",
        }
