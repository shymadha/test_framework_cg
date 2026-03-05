import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add project root BEFORE any framework imports
current = Path(__file__).resolve()

for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break

import argparse
from framework.core.test_engine import TestEngine
from framework.core.parser import ParseUserInput
from tests.base_test import BaseTest

class CpuDetectionTest(BaseTest):
    def do_test(self):
        self.logger.info("Running CPU Detection Test")
        output,error,exit_status = self.platform.interface.execute("lscpu")
       
        if output:
            self.result.set_result(True, "CPU detected")
            print(f"The test ouput is {output}")
        else:
            self.result.set_result(False, "CPU not detected")
            print(f"The test err is {error}")
            
if __name__ == "__main__":
    test = Path(__file__).resolve()
    print(f"The test_name is {test}")
    user_input = ParseUserInput(test)
    print("Loaded Config:")
    print(user_input.user_config)
    
    engine = TestEngine(user_input)
    engine.run()
