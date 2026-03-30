import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import importlib
from framework.core.user_input_parser import ParseUserInput
from core.logger import setup_logger
from framework.interfaces.interface_factory import InterfaceFactory
from framework.platforms.platform_factory import PlatformFactory


class TestEngine:
    """
    Main execution engine responsible for orchestrating the test lifecycle.

    The TestEngine manages:
      - Parsing user input and creating device/platform objects.
      - Running pre-test, test execution, and post-test phases.
      - Handling exceptions and ensuring the platform is properly closed.
      - Logging high‑level execution information.

    Attributes
    ----------
    test_engine_logger : logging.Logger
        Logger instance dedicated to TestEngine logs.
    user_input : ParseUserInput
        Object responsible for fetching and validating user inputs.
    platform_obj : object or None
        Platform object created after parsing input; performs OS/device handling.
    """

    def __init__(self):
        """
        Initialize the TestEngine and create essential components.

        Sets up:
          - A logger for the engine
          - A user input parser
          - A placeholder for the platform object (created later)
        """
        self.test_engine_logger = setup_logger("TestEngine")
        self.user_input = ParseUserInput()
        self.platform_obj = None

    def pre_test(self):
        """
        Perform the pre‑test initialization steps.

        This includes:
          - Logging the start of the pre‑test phase
          - Creating the device object using parsed user input
          - Building and initializing the corresponding platform object
          - Detecting OS or platform details before execution
        """
        self.test_engine_logger.info("Pre-test phase")
        self.user_input.create_dev_obj()
        self.platform_obj = self.user_input.get_platform_obj()
        self.platform_obj.detect_os()

    def run(self):
        """
        Execute the full test lifecycle.

        This method performs:
          1. Pre-test tasks
          2. Actual test execution (`do_test()` - implemented elsewhere)
          3. Post-test cleanup and logging
          4. Graceful exception handling with stack trace logging

        Returns
        -------
        SystemExit
            Exits the program with:
              - Status code returned by post_test()
              - 1 if any error occurs during execution
        """
        try:
            self.pre_test()
            status = self.do_test()
            status = self.post_test()
            #return sys.exit(status)

        except Exception as e:
            # Log full stacktrace
            self.test_engine_logger.exception(f"ERROR in TestEngine: {e}")

            # Cleanup if platform_obj initialized
            if self.platform_obj:
                try:
                    self.platform_obj.close()
                except Exception as close_err:
                    self.test_engine_logger.error(
                        f"Failed to close platform: {close_err}"
                    )
            #return sys.exit(1)

    def post_test(self):
        """
        Perform post‑test actions such as reporting verdict and cleanup.

        Determines PASS/FAIL using `self.result.passed`, logs the verdict,
        and closes the platform object if initialized.

        Returns
        -------
        int
            Typically returns a status integer indicating test success/failure.
            (Actual return semantics depend on integration with the test framework.)
        """
        verdict = "PASS" if self.result.passed else "FAIL"
        self.logger.info(f"{self.__class__.__name__}: {verdict}")

        if self.platform_obj:
            self.platform_obj.close()