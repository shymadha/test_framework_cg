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


class CpuCoreCountTest(BaseTest):
    def pre_test(self):
        print("Eexcuting pre-test for CpuCoreCount")
        
    def do_test(self):
        self.logger.info("Running CPU Core Count Test")
        output,error,exit_status = self.platform.interface.execute("nproc")
        print(f"The test ouput is {output}")
        if output and int(output) >= 1:
            self.result.set_result(True, "Valid core count")
        else:
            self.result.set_result(False, "Invalid core count")
            
if __name__ == "__main__":
    test = Path(__file__).resolve()
    print(f"The test_name is {test}")
    user_input = ParseUserInput(test)
    print("Loaded Config:")
    print(user_input.user_config)
    
    
    engine = TestEngine(user_input)
    engine.run()
    