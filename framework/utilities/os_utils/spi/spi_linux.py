from framework.utilities.os_utils.spi.base_spi import BaseSPI

class SPILinux(BaseSPI):
    def device_detection(self):
        return "ls /dev/spidev*"

    def loopback(self):
        return """python3 -c "import spidev; spi=spidev.SpiDev(); spi.open(0,0); spi.max_speed_hz=1000000; spi.mode=0; tx=[0xAA,0xBB,0xCC,0xDD]; rx=spi.xfer2(tx); print('PASS' if tx==rx else 'FAIL'); spi.close()" """

    def speed_mode(self):
        return """python3 -c "import spidev; spi=spidev.SpiDev(); spi.open(0,0); tx=[0x55]*4;
for speed in [100000,500000,1000000,4000000]: spi.max_speed_hz=speed; rx=spi.xfer2(tx); print(f'{speed//1000} KHz → {'PASS' if rx==tx else 'FAIL'});
for mode in range(4): spi.mode=mode; rx=spi.xfer2(tx); print(f'Mode {mode} → {'PASS' if rx==tx else 'FAIL'}); spi.close()" """

    def data_integrity(self):
        return """python3 -c "import spidev, os, hashlib; spi=spidev.SpiDev(); spi.open(0,0); spi.max_speed_hz=1000000; data=list(os.urandom(256)); rx=spi.xfer2(data); src_md5=hashlib.md5(bytes(data)).hexdigest()[:8]; rx_md5=hashlib.md5(bytes(rx)).hexdigest()[:8]; print('PASS' if data==rx else 'FAIL'); spi.close()" """
