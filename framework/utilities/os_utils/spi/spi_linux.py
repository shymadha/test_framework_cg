# framework/utilities/os_utils/spi/spi_linux.py

from framework.utilities.os_utils.spi.base_spi import BaseSPI


class SPILinux(BaseSPI):

    def __init__(self, platform_obj):
        """
        Initialize SPILinux with platform object.

        Parameters
        ----------
        platform_obj : object
            Platform object providing exec_cmd and logger.
        """
        self.platform_obj = platform_obj

    def device_detection(self):
        """
        Detect SPI devices on Linux/BBB.

        Returns
        -------
        tuple
            (output, error, exit_status)
        """
        cmd = "ls /dev/spidev*"
        return self.platform_obj.exec_cmd(cmd, "ssh")
    
        # try:
        #     cmd = "ls /dev/spidev*"
        #     return self.platform_obj.exec_cmd(cmd, "ssh")
        #     # output, error, status = self.platform_obj.exec_cmd(cmd, "ssh")
        #     # return output.strip(), error.strip(), status

        # except Exception as e:
        #     self.platform_obj.logger.error(
        #         f"SPI device detection error: {str(e)}", exc_info=True
        #     )
        #     return "", str(e), -1

    def loopback(self):
        """
        Execute SPI loopback test on Linux/BBB target.

        Requires jumper: P9.18 (MOSI) → P9.21 (MISO)

        Returns
        -------
        tuple
            (output, error, exit_status)
        """
        try:
            cmd = (
                "python3 -c \""
                "import spidev; "
                "spi = spidev.SpiDev(); "
                "spi.open(0, 0); "
                "spi.max_speed_hz = 1000000; "
                "spi.mode = 0; "
                "tx = [0xAA, 0xBB, 0xCC, 0xDD]; "
                "rx = spi.xfer2(tx); "
                "print('PASS' if tx == rx else 'FAIL'); "
                "spi.close()\""
            )
            output, error, status = self.platform_obj.exec_cmd(cmd, "ssh")
            return output.strip(), error.strip(), status

        except Exception as e:
            self.platform_obj.logger.error(
                f"SPI loopback error: {str(e)}", exc_info=True
            )
            return "", str(e), -1

    def speed_mode(self):
        """
        Test SPI at multiple speeds (100K/500K/1M/4MHz) and modes (0-3).

        Requires jumper: P9.18 (MOSI) → P9.21 (MISO)

        Returns
        -------
        tuple
            (output, error, exit_status)
        """
        try:
            cmd = (
                "python3 -c \""
                "import spidev; "
                "spi = spidev.SpiDev(); "
                "spi.open(0, 0); "
                "spi.mode = 0; "
                "tx = [0x55] * 4; "
                "results = []; "
                "speeds = [100000, 500000, 1000000, 4000000]; "
                "[results.append(str(s//1000)+'KHz:'+('PASS' if (spi.__setattr__('max_speed_hz',s) or True) and spi.xfer2(tx)==tx else 'FAIL')) for s in speeds]; "
                "modes = range(4); "
                "[results.append('Mode'+str(m)+':'+('PASS' if (spi.__setattr__('mode',m) or True) and spi.xfer2(tx)==tx else 'FAIL')) for m in modes]; "
                "print(','.join(results)); "
                "spi.close()\""
            )
            output, error, status = self.platform_obj.exec_cmd(cmd, "ssh")
            return output.strip(), error.strip(), status

        except Exception as e:
            self.platform_obj.logger.error(
                f"SPI speed mode error: {str(e)}", exc_info=True
            )
            return "", str(e), -1

    def data_integrity(self):
        """
        Test SPI data integrity using MD5 checksum on 256 random bytes.

        Requires jumper: P9.18 (MOSI) → P9.21 (MISO)

        Returns
        -------
        tuple
            (output, error, exit_status)
        """
        try:
            cmd = (
                "python3 -c \""
                "import spidev, os, hashlib; "
                "spi = spidev.SpiDev(); "
                "spi.open(0, 0); "
                "spi.max_speed_hz = 1000000; "
                "spi.mode = 0; "
                "data = list(os.urandom(256)); "
                "rx   = spi.xfer2(data); "
                "src  = hashlib.md5(bytes(data)).hexdigest()[:8]; "
                "dst  = hashlib.md5(bytes(rx)).hexdigest()[:8]; "
                "print('PASS' if data == rx else 'FAIL src='+src+' dst='+dst); "
                "spi.close()\""
            )
            output, error, status = self.platform_obj.exec_cmd(cmd, "ssh")
            return output.strip(), error.strip(), status

        except Exception as e:
            self.platform_obj.logger.error(
                f"SPI data integrity error: {str(e)}", exc_info=True
            )
            return "", str(e), -1