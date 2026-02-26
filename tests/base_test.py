import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from abc import ABC, abstractmethod
from framework.core.test_result import TestResult
from framework.core.logger import setup_logger

class BaseTest(ABC):

    def __init__(self, platform):
        self.platform = platform
        self.logger = setup_logger(self.__class__.__name__)
        self.result = TestResult(self.__class__.__name__)

    @abstractmethod
    def run(self):
        pass