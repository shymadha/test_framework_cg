from tests.base_test import BaseTest

class CPUCoreCountTest(BaseTest):

    def run(self):
        self.logger.info("Running CPU Core Count Test")

        output,error,exit_status = self.platform.interface.execute("nproc")
        print(f"The test ouput is {output}")
        if output and int(output) >= 1:
            self.result.set_result(True, "Valid core count")
        else:
            self.result.set_result(False, "Invalid core count")