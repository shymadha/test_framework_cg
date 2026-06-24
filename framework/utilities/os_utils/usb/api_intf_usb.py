"""
api_intf_usb.py
---------------
Platform-aware USB API interface for the test framework.

Single entry point for all USB test categories (USB-001 through USB-004).
Mirrors the pattern used by api_intf_pm.py — one interface file containing
all USB API classes, each backed by the platform-specific implementation
in usb_linux.py or usb_windows.py.

Classes
-------
USBUtilsAPI          -> USB-001  Device Detection
USBMassStorageAPI    -> USB-002  Mass Storage R/W
USBDataIntegrityAPI  -> USB-003  Data Integrity MD5
USBSerialFT232API    -> USB-004  Serial FT232 Loopback
"""

from framework.utilities.os_utils.usb.usb_linux import (
    USBDataIntegrityLinux, USBDeviceDetectionLinux, USBMassStorageLinux,
    USBSerialFT232Linux)
from framework.utilities.os_utils.usb.usb_win import (
    USBDataIntegrityWindows, USBDeviceDetectionWindows, USBMassStorageWindows,
    USBSerialFT232Windows)

# ===========================================================================
# USB-001 - Device Detection API
# ===========================================================================

class USBUtilsAPI:
    _PLATFORM_MAP = {
        "linux":   USBDeviceDetectionLinux,
        "beagle":  USBDeviceDetectionLinux,
        "windows": USBDeviceDetectionWindows,
    }

    def __init__(self, platform_obj):
        self.platform_obj = platform_obj
        self._backend     = self._resolve(platform_obj)

    def _resolve(self, platform_obj):
        key = (
            getattr(platform_obj, "os_type",    None) or
            getattr(platform_obj, "detected_os", None) or
            getattr(platform_obj, "os",          None) or
            "linux"
        ).lower()
        cls = self._PLATFORM_MAP.get(key)
        if cls is None:
            raise ValueError(
                f"USBUtilsAPI: unsupported platform '{key}'. "
                f"Supported: {list(self._PLATFORM_MAP)}"
            )
        return cls(platform_obj)

    def list_devices(self):
        return self._backend.list_devices()

    def get_device_details(self, vid_pid: str):
        return self._backend.get_device_details(vid_pid)

    def parse_non_hub_device(self, lsusb_output: str):
        return self._backend.parse_non_hub_device(lsusb_output)


# ===========================================================================
# USB-002 - Mass Storage R/W API
# ===========================================================================

class USBMassStorageAPI:
    _PLATFORM_MAP = {
        "linux":   USBMassStorageLinux,
        "beagle":  USBMassStorageLinux,
        "windows": USBMassStorageWindows,
    }

    # Linux/BBB defaults
    _LINUX_DEFAULTS = dict(
        device        = "/dev/sda1",
        mount_point   = "/mnt/pendrive",
        test_file     = "test_write.bin",
        block_size_mb = 1,
        count         = 256,
    )

    # Windows defaults
    _WINDOWS_DEFAULTS = dict(
        drive_letter  = "D:",
        test_file     = "test_write.bin",
        file_size_mb  = 256,
    )

    def __init__(self, platform_obj, **kwargs):
        self.platform_obj = platform_obj
        self._backend     = self._resolve(platform_obj, **kwargs)

    def _resolve(self, platform_obj, **kwargs):
        key = (
            getattr(platform_obj, "os_type",    None) or
            getattr(platform_obj, "detected_os", None) or
            getattr(platform_obj, "os",          None) or
            "linux"
        ).lower()
        cls = self._PLATFORM_MAP.get(key)
        if cls is None:
            raise ValueError(
                f"USBMassStorageAPI: unsupported platform '{key}'. "
                f"Supported: {list(self._PLATFORM_MAP)}"
            )
        defaults = self._WINDOWS_DEFAULTS if key == "windows" else self._LINUX_DEFAULTS
        merged   = {**defaults, **kwargs}
        return cls(platform_obj, **merged)

    def mount_device(self):
        return self._backend.mount_device()

    def write_speed_test(self):
        return self._backend.write_speed_test()

    def read_speed_test(self):
        return self._backend.read_speed_test()

    def cleanup_and_unmount(self):
        # Windows backend exposes cleanup(); Linux exposes cleanup_and_unmount()
        if hasattr(self._backend, "cleanup_and_unmount"):
            return self._backend.cleanup_and_unmount()
        return self._backend.cleanup()

    def parse_speed(self, text: str):
        return self._backend.parse_speed(text)


# ===========================================================================
# USB-003 - Data Integrity MD5 API
# ===========================================================================

class USBDataIntegrityAPI:
    _PLATFORM_MAP = {
        "linux":   USBDataIntegrityLinux,
        "beagle":  USBDataIntegrityLinux,
        "windows": USBDataIntegrityWindows,
    }

    # Linux/BBB defaults
    _LINUX_DEFAULTS = dict(
        device        = "/dev/sda1",
        mount_point   = "/mnt/pendrive",
        source_file   = "/tmp/source.bin",
        dest_file     = "integrity.bin",
        block_size_mb = 1,
        count         = 50,
    )

    # Windows defaults
    _WINDOWS_DEFAULTS = dict(
        drive_letter  = "D:",
        source_file   = "C:\\Windows\\Temp\\source.bin",
        dest_file     = "integrity.bin",
        file_size_mb  = 50,
    )

    def __init__(self, platform_obj, **kwargs):
        self.platform_obj = platform_obj
        self._backend     = self._resolve(platform_obj, **kwargs)

    def _resolve(self, platform_obj, **kwargs):
        key = (
            getattr(platform_obj, "os_type",    None) or
            getattr(platform_obj, "detected_os", None) or
            getattr(platform_obj, "os",          None) or
            "linux"
        ).lower()
        cls = self._PLATFORM_MAP.get(key)
        if cls is None:
            raise ValueError(
                f"USBDataIntegrityAPI: unsupported platform '{key}'. "
                f"Supported: {list(self._PLATFORM_MAP)}"
            )
        defaults = self._WINDOWS_DEFAULTS if key == "windows" else self._LINUX_DEFAULTS
        merged   = {**defaults, **kwargs}
        return cls(platform_obj, **merged)

    def generate_source_file(self):
        return self._backend.generate_source_file()

    def compute_md5(self, file_path: str):
        return self._backend.compute_md5(file_path)

    def mount_and_copy(self):
        # Windows backend uses copy_to_drive() instead of mount_and_copy()
        if hasattr(self._backend, "mount_and_copy"):
            return self._backend.mount_and_copy()
        return self._backend.copy_to_drive()

    def verify_md5_on_drive(self):
        return self._backend.verify_md5_on_drive()

    def compare_checksums(self, source_md5_output: str, dest_md5_output: str):
        return self._backend.compare_checksums(source_md5_output, dest_md5_output)

    def cleanup(self):
        return self._backend.cleanup()


# ===========================================================================
# USB-004 - Serial FT232 Loopback API
# ===========================================================================

class USBSerialFT232API:
    _PLATFORM_MAP = {
        "linux":   USBSerialFT232Linux,
        "beagle":  USBSerialFT232Linux,
        "windows": USBSerialFT232Windows,
    }

    # Linux/BBB defaults
    _LINUX_DEFAULTS = dict(
        port                 = "/dev/ttyUSB0",
        baud                 = 115200,
        loopback_script_path = "/tmp/usb_loopback.py",
        ft232_vid_pid        = "0403:6001",
    )

    # Windows defaults
    _WINDOWS_DEFAULTS = dict(
        com_port             = "COM3",
        baud                 = 115200,
        loopback_script_path = "C:\\Temp\\usb_loopback.py",
        vid_pid_pattern      = "VID_067B&PID_2303",
    )

    def __init__(self, platform_obj, **kwargs):
        self.platform_obj = platform_obj
        self._backend     = self._resolve(platform_obj, **kwargs)

    def _resolve(self, platform_obj, **kwargs):
        key = (
            getattr(platform_obj, "os_type",    None) or
            getattr(platform_obj, "detected_os", None) or
            getattr(platform_obj, "os",          None) or
            "linux"
        ).lower()
        cls = self._PLATFORM_MAP.get(key)
        if cls is None:
            raise ValueError(
                f"USBSerialFT232API: unsupported platform '{key}'. "
                f"Supported: {list(self._PLATFORM_MAP)}"
            )
        defaults = self._WINDOWS_DEFAULTS if key == "windows" else self._LINUX_DEFAULTS
        merged   = {**defaults, **kwargs}
        return cls(platform_obj, **merged)

    def detect_ft232(self):
        return self._backend.detect_ft232()

    def check_tty_port(self):
        # Windows uses check_com_port() instead of check_tty_port()
        if hasattr(self._backend, "check_tty_port"):
            return self._backend.check_tty_port()
        return self._backend.check_com_port()

    def extract_first_tty(self, output: str) -> str:
        # Windows uses extract_com_port() instead of extract_first_tty()
        if hasattr(self._backend, "extract_first_tty"):
            return self._backend.extract_first_tty(output)
        return self._backend.extract_com_port(output)

    def run_loopback_test(self, port: str = None, baud: int = None):
        return self._backend.run_loopback_test(port=port, baud=baud)

    def parse_loopback_result(self, script_output: str):
        return self._backend.parse_loopback_result(script_output)
