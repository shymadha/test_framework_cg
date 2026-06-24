import sys
from pathlib import Path

current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break

from framework.tests.base_test import BaseTest
from framework.utilities.os_utils.spi.api_intf_spi import SPIUtilsAPI


class SpiLoopbackTest(BaseTest):
    def do_test(self):
        self.logger.info("Running SPI Loopback Test")

        spi_api = SPIUtilsAPI(self.platform_obj)
        output, error, status = spi_api.loopback()

        self.logger.info(f"Loopback output: {output}")

        if status != 0:
            self.logger.error(
                f"SPILoopbackTest: FAIL — status={status} | {error}"
            )
            self.result.set_result(False, f"SPI loopback failed: {error}")
            return status

        if output.strip().upper() == "PASS":
            self.logger.info("SPILoopbackTest: PASS")
            self.result.set_result(True, "SPI loopback successful")
            return 0
        else:
            self.logger.error(
                f"SPILoopbackTest: FAIL — Output: {output} | "
                f"Check jumper P9.18(MOSI) → P9.21(MISO)"
            )
            self.result.set_result(False, f"SPI loopback mismatch: {output}")
            return 1


if __name__ == "__main__":
    test = SpiLoopbackTest()
    test.run()