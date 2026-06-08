"""Test Engine Tool module"""

import importlib

from langchain.tools import tool
from framework.core.logger import setup_logger


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
        raise RuntimeError(f"Expected class '{class_name}' not found in {module_path}")

    return getattr(module, class_name)


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
    print("Executor Agent Calling Test Engine Tool")

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
        "log_dir": log_dir,
    }


test_engine_tool = [run_test_tool]
