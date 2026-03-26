import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from abc import ABC, abstractmethod
from framework.core.test_result import TestResult
from framework.core.logger import setup_logger
from framework.core.user_input_parser import ParseUserInput
from core.test_engine import TestEngine
from pathlib import Path


class BaseTest(TestEngine):
    """
    Base class for all test cases in the automation framework.

    This class extends `TestEngine` and provides:
      - A per-test logger
      - A `TestResult` object to store the outcome of each test
      - A shared initialization pattern for derived test classes

    Test case classes must inherit from `BaseTest` instead of directly from
    `TestEngine`. This ensures consistent logging, result handling, and lifecycle
    behavior across all framework test modules.

    Attributes
    ----------
    logger : logging.Logger
        Logger instance named after the specific test class.
    result : TestResult
        Object used to store PASS/FAIL status and descriptive messages.
    """

    def __init__(self):
        """
        Initialize the base test environment.

        This constructor:
          - Calls TestEngine.__init__() to set up the test engine and platform.
          - Creates a test-specific logger.
          - Initializes a TestResult object tied to the current test class name.

        Raises
        ------
        Exception
            If TestEngine initialization fails.
        """
        super().__init__()
        self.logger = setup_logger(self.__class__.__name__)
        self.result = TestResult(self.__class__.__name__)