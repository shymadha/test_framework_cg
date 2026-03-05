import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import importlib
from core.parser import ParseUserInput
from core.logger import setup_logger
from framework.interfaces.interface_factory import InterfaceFactory
from framework.platforms.platform_factory import PlatformFactory

class TestEngine:

    def __init__(self, parser_obj):
        self.logger = setup_logger("TestEngine")
        self.config =parser_obj.user_config
        self.test_files= parser_obj.test_file
        self.platform = None
        self.parser = parser_obj
        self.tests = []

    def pre_test(self):
        self.logger.info("Pre-test phase")
        self.platform = self.parser.create_obj()
        self.platform.setup()
        self._load_tests()

    def _load_tests(self):
        metadata = self.parser.get_test_metadata()
        for item in metadata:
            module_path= item["module_path"]
            class_name = item["class_name"]
            
            if not class_name.endswith("Test"):
                class_name = class_name + "Test"
            
            module = importlib.import_module(module_path)
            test_class = getattr(module, class_name)
            self.tests.append(test_class(self.platform))
    
    def run(self):
        self.pre_test()
        self.do_test()
        self.post_test()      

    def do_test(self):
        for test in self.tests:
            status = test.run()
        
    def post_test(self):
        for test in self.tests:
           verdict = "PASS" if test.result.passed else "FAIL"
           self.logger.info(f"{test.result.name}: {verdict}")
               
        self.platform.cleanup()