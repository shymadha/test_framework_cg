import os
import sys
import paramiko
 
# ------------------------------------------------------------------------------
# Ensure project root is on sys.path when running this file directly (not as -m)
# This computes two levels up from this file: <project_root>/
# ------------------------------------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
 
# Now absolute imports will work regardless of how the file is executed
# ------------------------------------------------------------------------------
 
import importlib
from framework.core.user_input_parser import ParseUserInput
from framework.core.logger import setup_logger
from framework.interfaces.interface_factory import InterfaceFactory
from framework.platforms.platform_factory import PlatformFactory
 
 
class TestEngine:
    def __init__(self):
        self.logger = setup_logger("TestEngine")
        self.user_input = ParseUserInput()
        self.platform_obj = None
        self.logger.info(f"{self.__class__.__name__} initialized")
 
    def pre_test(self):
        self.logger.info("Pre-test phase started")
        try:
            # Parse config
            self.user_input_dict = self.user_input.parse_user_input(self.user_input.args.config)
            self.logger.debug(f"User input parsed: {self.user_input_dict}")
 
            # Create device object(s)
            self.user_input.create_dev_obj(self.user_input_dict)
            self.logger.info("Device objects created from user input")
 
            # Get platform object
            self.platform_obj = self.user_input.get_platform_obj()
            self.logger.info("Platform object obtained successfully")
            self.logger.debug(f"Platform object type: {type(self.platform_obj).__name__}")
        except Exception as e:
            self.logger.error(f"Pre-test phase failed: {e}")
            raise
        else:
            self.logger.info("Pre-test phase completed successfully")
 
    def run(self):
        self.logger.info("Test run started")
        try:
            self.pre_test()
            self.logger.info("Executing test body (do_test)")
            self.do_test()
        except Exception as e:
            self.logger.error(f"Run encountered an error: {e}")
            raise
        finally:
            # Post test should still attempt to execute to close interfaces cleanly
            try:
                self.post_test()
            except Exception as e:
                self.logger.error(f"Post-test encountered an error: {e}")
                raise
        self.logger.info("Test run finished")
 
    def post_test(self):
        self.logger.info("Post-test phase started")
        try:
            verdict = "PASS" if self.result.passed else "FAIL"
            self.logger.info(f"{self.__class__.__name__}: {verdict}")
        except Exception as e:
            self.logger.error(f"Failed to compute verdict: {e}")
            raise
        finally:
            # Always try to close interface
            try:
                if self.platform_obj and getattr(self.platform_obj, "test_interface_obj", None):
                    self.logger.info("Closing test interface connection...")
                    self.platform_obj.test_interface_obj.close()
                    self.logger.info("Test interface disconnected successfully.")
                else:
                    self.logger.debug("No test interface object found to close.")
            except Exception as e:
                self.logger.error(f"Error while closing test interface: {e}")
                raise
        self.logger.info("Post-test phase completed successfully")
 
 
# ------------------------------------------------------------------------------
# Optional: Allow running this module directly for quick/local tests.
# Preferred execution remains: `python -m framework.core.test_engine`
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    engine = TestEngine()
    # Ensure there is a do_test() defined or mocked for direct runs
    if not hasattr(engine, "do_test"):
        def _mock_do_test():
            engine.logger.info("Mock do_test() executed (no-op).")
            # Optionally mock a result object so post_test() can compute verdict
            class _Result:
                passed = True
            engine.result = _Result()
        engine.do_test = _mock_do_test
 
    engine.run()