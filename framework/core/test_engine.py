import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import importlib
from framework.core.user_input_parser import ParseUserInput
from core.logger import setup_logger
from framework.interfaces.interface_factory import InterfaceFactory
from framework.platforms.platform_factory import PlatformFactory

class TestEngine:
    def __init__(self):
        self.test_engine_logger = setup_logger("TestEngine")
        self.user_input = ParseUserInput()
        self.platform_obj = None
        
    def pre_test(self):
        self.test_engine_logger.info("Pre-test phase")
        self.user_input.create_dev_obj()
        self.platform_obj = self.user_input.get_platform_obj()
        self.platform_obj.detect_os()
        
    def run(self):
        try:
            self.pre_test()
            status = self.do_test()
            status = self.post_test()
            return sys.exit(status) 
        except Exception as e:
            # Log full stacktrace
            self.test_engine_logger.exception(f"ERROR in TestEngine: {e}")

            # Cleanup if platform_obj initialized
            if self.platform_obj:
                try:
                    self.platform_obj.close()
                except Exception as close_err:
                    self.test_engine_logger.error(f"Failed to close platform: {close_err}")
            return sys.exit(1)  # failure
     

    def post_test(self):
        verdict = "PASS" if self.result.passed else "FAIL"
        self.logger.info(f"{self.__class__.__name__}: {verdict}")
        if self.platform_obj:
            self.platform_obj.close()
        
        
        

        
    