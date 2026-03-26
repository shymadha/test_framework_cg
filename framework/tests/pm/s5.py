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
from framework.core.user_input_parser import ParseUserInput
from tests.base_test import BaseTest
from core.testbed_utils import TestbedUtils
from framework.utilities.os_utils.api_intf_os_base import OSBaseAPI

class ShutdownTest(BaseTest):
   def pre_test(self):
      super().pre_test()
      testbed_utils = TestbedUtils(self.user_input.args.config)
      self.min_cores =testbed_utils.get_value("shutdown")
      self.password = testbed_utils.get_value("password")
      
   
   def do_test(self):
      self.logger.info("Running Shutdown Test")
      pm_obj = OSBaseAPI(self.platform_obj)
      output, error, exit_status = pm_obj.pm.shutdown()
      self.logger.info(f"Output : {output}")
      self.logger.info(f"Error : {error}")
      self.logger.info(f"Exit Status : {exit_status}")
      
      if exit_status == 0:
         self.result.set_result(True, "Shutdown triggered successfully")
     
      else:
         self.result.set_result(False, "Shutdown failed")
            
         return exit_status

if __name__ == "__main__":
    test = ShutdownTest()
    test.run()