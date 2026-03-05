import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from abc import ABC, abstractmethod
from framework.core.test_result import TestResult
from framework.core.logger import setup_logger
from core.parser import ParseUserInput
from core.test_engine import TestEngine

class BaseTest(TestEngine):
    def __init__(self, platform):
        self.platform = platform
        self.logger = setup_logger(self.__class__.__name__)
        self.result = TestResult(self.__class__.__name__)

    
    #def do_test(self):
    #    pass
    
    def pre_test(self):
        pass
    
    def post_test(self):
        pass

    
    def run(self):
        self.pre_test()
        self.do_test()
        self.post_test()
    