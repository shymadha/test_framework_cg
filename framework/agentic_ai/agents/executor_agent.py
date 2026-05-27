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
        logger.info("Initializing TestEngine")
        engine = TestEngine()

        # 1. Framework initializes platform & interface
       # engine.pre_test()

        # 2. Select test class
        domain = state["test_domain"]
        print(f"Test domain is:{domain}")
        test_name = state["test_name"]
        print(f"Test name is:{test_name}")

        logger.info(f"Selecting test: {domain} / {test_name}")
        TestClass = load_test_class(domain, test_name)

        # 3. Instantiate test using platform object
        test_instance = TestClass()

        # 4. Execute test
        logger.info("Executing test")
        engine = test_instance.run()
        if engine is None:
            raise RuntimeError("Test Execution failed")
        print(f"Engine.result is {engine}")

        # 5. Post-test
        #engine.post_test()
        
        logger.info("=" * 50)
        logger.info(f"END OF TEST: {test_name}")
        logger.info("=" * 50)

        return {
            "execution_status": "PASSED" if engine == "PASS" else "FAILED",
            "execution_output": {
                "domain": domain,
                "test": test_name,
                "status": "SUCCESS"
            },
            "status": "DONE"
        }
       

    except Exception as e:
        logger.exception("Test execution failed")

        return {
            "execution_status": "FAILED",
            "execution_output": {
                "status": "FAILED",
                "error": str(e),
                "log_path": "logs/framework.log"
            },
            "status": "FAILED"
        }

