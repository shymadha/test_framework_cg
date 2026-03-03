import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import importlib
#from core.parser import parse_input
from core.parser import ParseUserInput
from core.logger import setup_logger
from factory.interface_factory import InterfaceFactory
from factory.platform_factory import PlatformFactory

class TestEngine:

    def __init__(self, parser_obj):
        self.logger = setup_logger("TestEngine")
        self.config =parser_obj.config
        self.test_files= parser_obj.test_files
        self.test_metadata=parser_obj.test_metadata
        self.platform = None
        self.tests = []

    def pre_test(self):
        self.logger.info("Pre-test phase")

        interface = InterfaceFactory.create_interface(
            self.config["interface"]
        )

        self.platform = PlatformFactory.create_platform(
            self.config["platform"],
            interface
        )

        self.platform.setup()
        self._load_tests()

    def _load_tests(self):
        # for test_path in self.config["tests"]:
        #     module_path, class_name = test_path.rsplit(".", 1)
        #     module = importlib.import_module(module_path)
        #     test_class = getattr(module, class_name)
        #     self.tests.append(test_class(self.platform))
        
        for item in self.test_metadata:
            module_path= item["module_path"]
            class_name = item["class_name"]
            
            if not class_name.endswith("Test"):
                class_name = class_name + "Test"
            print(f"class_name is {class_name}")
            module = importlib.import_module(module_path)
            test_class = getattr(module, class_name)
            self.tests.append(test_class(self.platform))
            

    def do_test(self):
        for test in self.tests:
            test.run()

    def post_test(self):
        for test in self.tests:
            verdict = "PASS" if test.result.passed else "FAIL"
            self.logger.info(f"{test.result.name}: {verdict}")

        self.platform.cleanup()