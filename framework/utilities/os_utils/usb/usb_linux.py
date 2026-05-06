"""
usb_linux.py
------------
Linux-specific backend implementations for all USB test categories.

Contains four backend classes consumed by api_intf_usb.py:

  - USBDeviceDetectionLinux   → USB-001 device detection (lsusb)
  - USBMassStorageLinux       → USB-002 mass storage R/W (dd + mount)
  - USBDataIntegrityLinux     → USB-003 data integrity (MD5 checksum)
  - USBSerialFT232Linux       → USB-004 FT232 serial loopback

Each method returns a consistent (output, error, exit_status) tuple,
matching the convention used across all OS utility modules in this
framework.
"""

import re


# ===========================================================================
# USB-001 — Device Detection
# ===========================================================================

class USBDeviceDetectionLinux:
    """
    Linux backend for USB device enumeration and descriptor inspection.

    Parameters
    ----------
    platform_obj : object
        Active platform connection exposing ``execute_command(cmd)``.
    """

    def __init__(self, platform_obj):
        self.platform_obj = platform_obj

    def list_devices(self):
        """
        List all USB devices via ``lsusb``.

        Returns
        -------
        tuple[str, str, int]
            ``(output, error, exit_status)``

        Example output
        --------------
        ::

            Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
            Bus 001 Device 002: ID 0781:5567 SanDisk Corp. Cruzer Blade
        """
        return self.platform_obj.exec_cmd("lsusb", "ssh")

    def get_device_details(self, vid_pid: str):
        """
        Retrieve filtered descriptor fields for a specific USB device.

        Parameters
        ----------
        vid_pid : str
            Vendor:Product ID in ``XXXX:XXXX`` format, e.g. ``"0781:5567"``.

        Returns
        -------
        tuple[str, str, int]
            ``(output, error, exit_status)``

        Raises
        ------
        ValueError
            If ``vid_pid`` does not match ``XXXX:XXXX`` pattern.
        """
        if not re.fullmatch(r"[0-9a-fA-F]{4}:[0-9a-fA-F]{4}", vid_pid):
            raise ValueError(
                f"Invalid vid_pid '{vid_pid}'. Expected 'XXXX:XXXX'."
            )
        cmd = (
            f"lsusb -v -d {vid_pid} "
            r'| grep -E "idVendor|idProduct|bcdUSB|MaxPower"'
        )
        return self.platform_obj.exec_cmd(cmd, "ssh")

    @staticmethod
    def parse_non_hub_device(lsusb_output: str):
        """
        Extract the first non-root-hub VID:PID from ``lsusb`` output.

        Skips Linux Foundation root hubs (``1d6b:00xx``).

        Parameters
        ----------
        lsusb_output : str
            Raw stdout from :meth:`list_devices`.

        Returns
        -------
        str or None
            First peripheral VID:PID, or ``None`` if only hubs found.
        """
        pattern = re.compile(r"ID\s+([0-9a-fA-F]{4}:[0-9a-fA-F]{4})\s+(.*)")
        for line in lsusb_output.splitlines():
            match = pattern.search(line)
            if match and not match.group(1).startswith("1d6b"):
                return match.group(1)
        return None


# ===========================================================================
# USB-002 — Mass Storage R/W
# ===========================================================================

class USBMassStorageLinux:
    """
    Linux backend for USB mass storage mount, R/W speed test, and teardown.

    Parameters
    ----------
    platform_obj : object
        Active platform connection.
    device : str
        Block device path.  Default: ``"/dev/sda1"``.
    mount_point : str
        Mount target directory.  Default: ``"/mnt/pendrive"``.
    test_file : str
        Temporary test file name.  Default: ``"test_write.bin"``.
    block_size_mb : int
        ``dd`` block size in MB.  Default: ``1``.
    count : int
        Number of blocks.  Default: ``256`` (256 MB).
    """

    _DD_SPEED_PATTERN = re.compile(
        r"([\d.]+)\s*(MB/s|GB/s|kB/s)", re.IGNORECASE
    )

    def __init__(
        self,
        platform_obj,
        device: str = "/dev/sda1",
        mount_point: str = "/mnt/pendrive",
        test_file: str = "test_write.bin",
        block_size_mb: int = 1,
        count: int = 256,
    ):
        self.platform_obj  = platform_obj
        self.device        = device
        self.mount_point   = mount_point
        self.test_file     = test_file
        self.block_size_mb = block_size_mb
        self.count         = count

    @property
    def _test_file_path(self) -> str:
        return f"{self.mount_point}/{self.test_file}"

    def mount_device(self):
        """
        Create mount point, mount device, and confirm via ``df -h``.

        Returns
        -------
        tuple[str, str, int]
        """
        return self._run_sequence([
            f"sudo mkdir -p {self.mount_point}",
            f"sudo mount {self.device} {self.mount_point}",
            f"df -h {self.mount_point}",
        ])

    def write_speed_test(self):
        """
        Sequential write test using ``dd`` with ``oflag=sync``.

        Returns
        -------
        tuple[str, str, int]
        """
        cmd = (
            f"sudo dd if=/dev/zero "
            f"of={self._test_file_path} "
            f"bs={self.block_size_mb}M "
            f"count={self.count} "
            f"oflag=sync status=progress"
        )
        return self.platform_obj.exec_cmd(cmd, "ssh")

    def read_speed_test(self):
        """
        Sequential read test using ``dd`` with ``iflag=direct``.

        Returns
        -------
        tuple[str, str, int]
        """
        cmd = (
            f"sudo dd if={self._test_file_path} "
            f"of=/dev/null "
            f"bs={self.block_size_mb}M "
            f"iflag=direct status=progress"
        )
        return self.platform_obj.exec_cmd(cmd, "ssh")

    def cleanup_and_unmount(self):
        """
        Remove test file and unmount device. Silent on success.

        Returns
        -------
        tuple[str, str, int]
        """
        return self._run_sequence([
            f"sudo rm {self._test_file_path}",
            f"sudo umount {self.mount_point}",
        ])

    def parse_speed(self, text: str):
        """
        Extract transfer speed and unit from ``dd`` output.

        Returns
        -------
        tuple[float, str] or tuple[None, None]
        """
        match = self._DD_SPEED_PATTERN.search(text)
        if match:
            return float(match.group(1)), match.group(2)
        return None, None

    def _run_sequence(self, commands: list):
        out_parts, err_parts = [], []
        for cmd in commands:
            out, err, status = self.platform_obj.exec_cmd(cmd, "ssh")
            out_parts.append(out)
            err_parts.append(err)
            if status != 0:
                return "\n".join(out_parts), "\n".join(err_parts), status
        return "\n".join(out_parts), "\n".join(err_parts), 0


# ===========================================================================
# USB-003 — Data Integrity MD5
# ===========================================================================

class USBDataIntegrityLinux:
    """
    Linux backend for USB MD5 data integrity verification.

    Parameters
    ----------
    platform_obj : object
        Active platform connection.
    device : str
        Block device to mount.  Default: ``"/dev/sda1"``.
    mount_point : str
        Mount target directory.  Default: ``"/mnt/pendrive"``.
    source_file : str
        Temporary source file path.  Default: ``"/tmp/source.bin"``.
    dest_file : str
        Destination filename on the pen drive.  Default: ``"integrity.bin"``.
    block_size_mb : int
        ``dd`` block size in MB.  Default: ``1``.
    count : int
        Number of blocks.  Default: ``50`` (50 MB).
    """

    _MD5_PATTERN = re.compile(r"^([0-9a-fA-F]{32})\s+", re.MULTILINE)

    def __init__(
        self,
        platform_obj,
        device: str = "/dev/sda1",
        mount_point: str = "/mnt/pendrive",
        source_file: str = "/tmp/source.bin",
        dest_file: str = "integrity.bin",
        block_size_mb: int = 1,
        count: int = 50,
    ):
        self.platform_obj  = platform_obj
        self.device        = device
        self.mount_point   = mount_point
        self.source_file   = source_file
        self.dest_file     = dest_file
        self.block_size_mb = block_size_mb
        self.count         = count

    @property
    def _dest_path(self) -> str:
        return f"{self.mount_point}/{self.dest_file}"

    def generate_source_file(self):
        """
        Generate a random binary file via ``dd if=/dev/urandom``.

        Returns
        -------
        tuple[str, str, int]
        """
        cmd = (
            f"dd if=/dev/urandom "
            f"of={self.source_file} "
            f"bs={self.block_size_mb}M "
            f"count={self.count} "
            f"status=progress"
        )
        return self.platform_obj.exec_cmd(cmd, "ssh")

    def compute_md5(self, file_path: str):
        """
        Compute MD5 checksum of a file on the target.

        Parameters
        ----------
        file_path : str
            Absolute path of the file to hash.

        Returns
        -------
        tuple[str, str, int]
        """
        return self.platform_obj.exec_cmd(f"md5sum {file_path}", "ssh")

    def mount_and_copy(self):
        """
        Mount device, copy source file, and flush with ``sync``.

        Returns
        -------
        tuple[str, str, int]
        """
        return self._run_sequence([
            f"sudo mkdir -p {self.mount_point}",
            f"sudo mount {self.device} {self.mount_point}",
            f"sudo cp {self.source_file} {self._dest_path} && sync",
        ])

    def verify_md5_on_drive(self):
        """
        Compute MD5 of the copied file on the pen drive.

        Returns
        -------
        tuple[str, str, int]
        """
        return self.compute_md5(self._dest_path)

    def compare_checksums(self, source_md5_output: str, dest_md5_output: str):
        """
        Compare two ``md5sum`` output strings in Python.

        Parameters
        ----------
        source_md5_output : str
            Raw stdout from Step 2.
        dest_md5_output : str
            Raw stdout from Step 4.

        Returns
        -------
        tuple[bool, str, str, str]
            ``(match, result_msg, source_hash, dest_hash)``
        """
        source_hash = self._extract_md5(source_md5_output)
        dest_hash   = self._extract_md5(dest_md5_output)

        if not source_hash:
            return False, "FAIL: could not parse source MD5", source_hash, dest_hash
        if not dest_hash:
            return False, "FAIL: could not parse destination MD5", source_hash, dest_hash
        if source_hash == dest_hash:
            return True, "PASS: Integrity OK", source_hash, dest_hash
        return (
            False,
            f"FAIL: Mismatch — source={source_hash}  dest={dest_hash}",
            source_hash,
            dest_hash,
        )

    def cleanup(self):
        """
        Remove copied file, unmount device, and delete source file.

        Returns
        -------
        tuple[str, str, int]
        """
        return self._run_sequence([
            f"sudo rm -f {self._dest_path}",
            f"sudo umount {self.mount_point}",
            f"rm -f {self.source_file}",
        ])

    def _extract_md5(self, md5sum_output: str) -> str:
        match = self._MD5_PATTERN.search(md5sum_output)
        return match.group(1).lower() if match else ""

    def _run_sequence(self, commands: list):
        out_parts, err_parts = [], []
        for cmd in commands:
            out, err, status = self.platform_obj.exec_cmd(cmd, "ssh")
            out_parts.append(out)
            err_parts.append(err)
            if status != 0:
                return "\n".join(out_parts), "\n".join(err_parts), status
        return "\n".join(out_parts), "\n".join(err_parts), 0

 
# ===========================================================================
# USB-004 — Serial FT232 Loopback
# ===========================================================================
 
class USBSerialFT232Linux:
    """
    Linux backend for FT232 USB-to-UART serial loopback testing.
 
    NOTE: All commands in this class execute LOCALLY on the server
    (exec_cmd with "local") because the FT232 device is physically
    connected to the server, NOT to the BBB.
 
    Parameters
    ----------
    platform_obj : object
        Active platform connection.
    port : str
        Serial port path on the server.  Default: ``"/dev/ttyUSB0"``.
    baud : int
        Baud rate.  Default: ``115200``.
    loopback_script_path : str
        Path of ``usb_loopback.py`` on the server.
        Default: ``"/tmp/usb_loopback.py"``.
    ft232_vid_pid : str
        Expected FT232 VID:PID.  Default: ``"0403:6001"``.
    """
 
    _RESULT_PATTERN = re.compile(r"Result:\s+(\d+)/(\d+)\s+passed", re.IGNORECASE)
    _TTY_PATTERN    = re.compile(r"(/dev/ttyUSB\d+)")
 
    def __init__(
        self,
        platform_obj,
        port: str = "/dev/ttyUSB0",
        baud: int = 115200,
        loopback_script_path: str = "/tmp/usb_loopback.py",
        ft232_vid_pid: str = "0403:6001",
    ):
        self.platform_obj         = platform_obj
        self.port                 = port
        self.baud                 = baud
        self.loopback_script_path = loopback_script_path
        self.ft232_vid_pid        = ft232_vid_pid
 
    def detect_ft232(self):
        """
        Detect FT232 on the server USB bus via ``lsusb | grep``.
        Runs LOCALLY on the server.
 
        Returns
        -------
        tuple[str, str, int]
        """
        return self.platform_obj.exec_cmd(
        r'lsusb | grep -i "Prolific\|PL2303\|067b"', "ssh"  # runs on BBB
        )
 
    def check_tty_port(self):
        """
        Confirm ``/dev/ttyUSBx`` node exists on the server.
        Runs LOCALLY on the server.
 
        Returns
        -------
        tuple[str, str, int]
        """
        return self.platform_obj.exec_cmd("ls /dev/ttyUSB*", "ssh") # runs on BBB
 
    def extract_first_tty(self, ls_output: str) -> str:
        """Extract first ``/dev/ttyUSBx`` path from ``ls`` output."""
        match = self._TTY_PATTERN.search(ls_output)
        return match.group(1) if match else ""
 
    def run_loopback_test(self, port: str = None, baud: int = None):
        """
        Execute ``usb_loopback.py`` LOCALLY on the server.
 
        Parameters
        ----------
        port : str, optional
            Overrides :attr:`port` if provided.
        baud : int, optional
            Overrides :attr:`baud` if provided.
 
        Returns
        -------
        tuple[str, str, int]
 
        Example output
        --------------
        ::
 
            PASS | Sent: b'HELLO_BBB'        | Got: b'HELLO_BBB'
            PASS | Sent: b'LOOPBACK_01'      | Got: b'LOOPBACK_01'
            PASS | Sent: b'DATA_XYZ'         | Got: b'DATA_XYZ'
            PASS | Sent: b'\\xde\\xad\\xbe\\xef' | Got: b'\\xde\\xad\\xbe\\xef'
 
            Result: 4/4 passed
        """
        cmd = (
            f"python3 {self.loopback_script_path} "
            f"--port {port or self.port} "
            f"--baud {baud or self.baud}"
        )
        return self.platform_obj.exec_cmd(cmd, "ssh") # runs on BBB, but executes the script on the server via "local"
 
    def parse_loopback_result(self, script_output: str):
        """
        Parse ``Result: N/M passed`` from loopback script output.
 
        Returns
        -------
        tuple[int, int] or tuple[None, None]
        """
        match = self._RESULT_PATTERN.search(script_output)
        if match:
            return int(match.group(1)), int(match.group(2))
        return None, None