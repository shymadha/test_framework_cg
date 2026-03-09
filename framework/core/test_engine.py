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
        self.logger = setup_logger("TestEngine")
        self.user_input = ParseUserInput()
        self.platform_obj = None
        
    def pre_test(self):
        self.logger.info("Pre-test phase")
        self.user_input_dict = self.user_input.parse_user_input(self.user_input.args.config)
        self.user_input.create_dev_obj(self.user_input_dict)
        self.platform_obj = self.user_input.get_platform_obj()
        
    def run(self):
        self.pre_test()
        self.do_test()
        self.post_test()      

    def post_test(self):
        verdict = "PASS" if self.result.passed else "FAIL"
        self.logger.info(f"{self.__class__.__name__}: {verdict}")
        self.platform_obj.test_interface_obj.close()