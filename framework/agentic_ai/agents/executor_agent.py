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

import importlib

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


def executor_agent(state):
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

        logger.info(f"Selecting test: {domain} / {test_name}")

        TestClass = load_test_class(domain, test_name)
        test_instance = TestClass()

        logger.info("Executing test")

        result = test_instance.run()

        if result is None:
            raise RuntimeError("Test Execution failed")

        print(f"Engine.result is {result}")

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
            "execution_status": "PASSED" if result == "PASS" else "FAILED",
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
