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
from framework.core.test_engine import TestEngine
from framework.core.logger import setup_logger
#from framework.tests.test_registry import get_test_class
from langchain.tools import tool
from framework.agentic_ai.llm.gen_engine_llm import GenEngineLLM
import importlib
from langchain.agents import create_agent
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("api_key")
llm = GenEngineLLM().get_llm_model()



@tool
def run_test_tool(domain: str, test_name: str, log_dir: str) -> dict:
    """
    Execute a test given domain and test_name.

    Args:
        domain: Test domain (cpu, i2c, etc.)
        test_name: Specific test name
        log_dir: Directory where logs should be written

    Returns:
        dict: execution result
    """

    logger = setup_logger("TestEngine", log_dir)

    logger.info(f"Selecting test: {domain} / {test_name}")

    TestClass = load_test_class(domain, test_name)
    test_instance = TestClass()

    logger.info("Executing test")

    result = test_instance.run()

    if result is None:
        raise RuntimeError("Test Execution failed")

    return {
        "result": result,
        "status": "SUCCESS" if result == "PASS" else "FAILED",
        "domain": domain,
        "test": test_name,
        "log_dir": log_dir
    }


llm = GenEngineLLM().get_llm_model()

agent = create_agent(
    model=llm,
    tools=[run_test_tool],
    system_prompt="""
You are a test execution agent.

STRICT RULES:
- ALWAYS call run_test_tool
- DO NOT invent values
- Use domain and test_name exactly as provided
"""
)


def snake_to_camel(snake: str) -> str:
    return "".join(word.capitalize() for word in snake.split("_"))


def load_test_class(domain: str, test_name: str):
    """
    domain: cpu
    test_name: cpu_monitor_usage_test
    """
    module_path = f"framework.tests.{domain}.{test_name}"
    
    module = importlib.import_module(module_path)

    class_name = snake_to_camel(test_name)

    if not hasattr(module, class_name):
        raise RuntimeError(
            f"Expected class '{class_name}' not found in {module_path}"
        )

    return getattr(module, class_name)

def extract_tool_output(response):
    from langchain_core.messages import ToolMessage
    import json

    for msg in reversed(response.get("messages", [])):
        if isinstance(msg, ToolMessage):
            try:
                return json.loads(msg.content)
            except:
                return msg.content
    return None

def executor_agent(state):
    
    import framework.core.logger as logger_module
    from datetime import datetime
    from pathlib import Path

    # ✅ SAFE log_dir handling
    log_dir = state.get("log_dir")

    if not log_dir:
        print("⚠️ log_dir not found → creating new one")

        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_dir_path = Path("logs") / ts
        log_dir_path.mkdir(parents=True, exist_ok=True)

        log_dir = str(log_dir_path)
        state["log_dir"] = log_dir

    # ✅ IMPORTANT: force logger to use this folder
    logger_module._LOG_DIR = log_dir

    logger = setup_logger("ExecutorAgent")

    try:
        # ✅ Prevent duplicate execution
        if state.get("execution_done"):
            print("⚠️ Skipping duplicate execution")
            return state

        logger.info("Initializing TestEngine")
        engine = TestEngine()

        domain = state["test_domain"]
        test_name = state["test_name"]

        print(f"Test domain is:{domain}")
        print(f"Test name is:{test_name}")

        # logger.info(f"Selecting test: {domain} / {test_name}")

        # TestClass = load_test_class(domain, test_name)
        # test_instance = TestClass()

        # logger.info("Executing test")

        # result = test_instance.run()

        # if result is None:
        #     raise RuntimeError("Test Execution failed")

        # print(f"Engine.result is {result}")
        response = agent.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": f"""
        Execute test with:
        domain = {domain}
        test_name = {test_name}
        log_dir={state["log_dir"]}

        Use these EXACT values.
        """
                }
            ]
        })

        print(f"response is :{response}")
        # ✅ Extract tool output
        
        output = extract_tool_output(response)
        print(f"output is {output}")

        if not output:
            raise RuntimeError("No tool output found")


        result = output.get("result")
        status = output.get("status")
        print(f"result is {result}")
        print(f"status is {status}")

        logger.info(f"Execution result: {result}")
        # # ✅ IMPORTANT: get log_dir from your engine
        # log_dir = getattr(test_instance, "log_dir", None)

        # # fallback if your framework uses engine
        # if not log_dir and hasattr(engine, "log_dir"):
        #     log_dir = engine.log_dir
        
        #✅ FIX THIS (IMPORTANT)
        logs_base = Path("logs")

        execution_dirs = [d for d in logs_base.iterdir() if d.is_dir()]
        latest_dir = sorted(execution_dirs, key=lambda d: d.name)[-1]

        log_dir = str(latest_dir)


        print("✅ LOG DIR:", log_dir)

        logger.info("=" * 50)
        logger.info(f"END OF TEST: {test_name}")
        logger.info("=" * 50)

        return {
            "execution_status": "PASSED" if status == "PASS" else "FAILED",
            "execution_output": {
                "domain": domain,
                "test": test_name,
                "status": "SUCCESS"
            },
            "log_dir": log_dir,              # ✅ CRITICAL
            "execution_done": True,          # ✅ prevents duplicates
            "status": "DONE"
        }

    except Exception as e:
        logger.exception("Test execution failed")

        return {
            "execution_status": "FAILED",
            "execution_output": {
                "status": "FAILED",
                "error": str(e)
            },
            "log_dir": log_dir, #state.get("log_dir"),  # ✅ preserve if exists
            "execution_done": True,
            "status": "FAILED"
        }



# def executor_agent(state):
#     logger = setup_logger("ExecutorAgent")

#     try:
#         # ✅ Prevent duplicate execution
#         if state.get("execution_done"):
#             print("⚠️ Skipping duplicate execution")
#             return state

#         logger.info("Initializing TestEngine")
#         engine = TestEngine()

#         domain = state["test_domain"]
#         test_name = state["test_name"]

#         print(f"Test domain is:{domain}")
#         print(f"Test name is:{test_name}")

#         logger.info(f"Selecting test: {domain} / {test_name}")

#         TestClass = load_test_class(domain, test_name)
#         test_instance = TestClass()

#         logger.info("Executing test")

#         result = test_instance.run()

#         if result is None:
#             raise RuntimeError("Test Execution failed")

#         print(f"Engine.result is {result}")

#         # # ✅ IMPORTANT: get log_dir from your engine
#         # log_dir = getattr(test_instance, "log_dir", None)

#         # # fallback if your framework uses engine
#         # if not log_dir and hasattr(engine, "log_dir"):
#         #     log_dir = engine.log_dir
        
#         #✅ FIX THIS (IMPORTANT)
#         logs_base = Path("logs")

#         execution_dirs = [d for d in logs_base.iterdir() if d.is_dir()]
#         latest_dir = sorted(execution_dirs, key=lambda d: d.name)[-1]

#         log_dir = str(latest_dir)


#         print("✅ LOG DIR:", log_dir)

#         logger.info("=" * 50)
#         logger.info(f"END OF TEST: {test_name}")
#         logger.info("=" * 50)

#         return {
#             "execution_status": "PASSED" if result == "PASS" else "FAILED",
#             "execution_output": {
#                 "domain": domain,
#                 "test": test_name,
#                 "status": "SUCCESS"
#             },
#             "log_dir": log_dir,              # ✅ CRITICAL
#             "execution_done": True,          # ✅ prevents duplicates
#             "status": "DONE"
#         }

#     except Exception as e:
#         logger.exception("Test execution failed")

#         return {
#             "execution_status": "FAILED",
#             "execution_output": {
#                 "status": "FAILED",
#                 "error": str(e)
#             },
#             "log_dir": log_dir, #state.get("log_dir"),  # ✅ preserve if exists
#             "execution_done": True,
#             "status": "FAILED"
#         }
