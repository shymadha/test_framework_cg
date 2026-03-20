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
        self.test_engine_logger = setup_logger("TestEngine")
        self.user_input = ParseUserInput()
        self.platform_obj = None
        self.logger.info(f"{self.__class__.__name__} initialized")
 
    def pre_test(self):
        self.test_engine_logger.info("Pre-test phase")
        self.user_input.create_dev_obj()
        self.platform_obj = self.user_input.get_platform_obj()
        self.platform_obj.detect_os()
        
    def run(self):
        self.pre_test()
        status = self.do_test()
        status = self.post_test()
        return sys.exit(status)      

    def post_test(self):
        verdict = "PASS" if self.result.passed else "FAIL"
        self.logger.info(f"{self.__class__.__name__}: {verdict}")
        self.platform_obj.close()
        
    