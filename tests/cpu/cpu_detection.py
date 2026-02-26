from tests.base_test import BaseTest

class CPUDetectionTest(BaseTest):

    def run(self):
        self.logger.info("Running CPU Detection Test")
        output,error,exit_status = self.platform.interface.execute("lscpu")
       
        if output:
            self.result.set_result(True, "CPU detected")
            print(f"The test ouput is {output}")
        else:
            self.result.set_result(False, "CPU not detected")
            print(f"The test err is {error}")