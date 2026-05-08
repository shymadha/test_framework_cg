import sys
import os
from pathlib import Path

current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break

from framework.tests.base_test import BaseTest
from framework.core.testbed_utils import TestbedUtils
from framework.utilities.os_utils.api_intf_os_base import OSBaseAPI


class StorageDiskSpaceTest(BaseTest):
    def pre_test(self):
        super().pre_test()
        self.logger.info("Executing pre-test for StorageDiskSpace Test")

    def do_test(self):
        self.logger.info("Running Storage Disk Space Test")

        os_obj = OSBaseAPI(self.platform_obj)
        output, error, exit_status = os_obj.storage.disk_space()

        self.logger.info(f"Disk Space Check Output:\n{output}")

        if exit_status == 0:
            self.result.set_result(True, "Disk space check succeeded")
        else:
            self.logger.error(f"Disk space check failed: {error}")
            self.result.set_result(False, "Disk space check failed")

        return exit_status

if __name__ == "__main__":
    test = StorageDiskSpaceTest()
    test.run()
