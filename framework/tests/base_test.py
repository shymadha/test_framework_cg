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
    def __init__(self):
        super().__init__()
        self.logger = setup_logger(self.__class__.__name__)
        self.result = TestResult(self.__class__.__name__)

        
    def run(self):
        super().pre_test()
        self.pre_test()
        status = self.do_test()
        super().post_test()
        return status
    