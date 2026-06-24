"""
usb_windows.py
--------------
Windows-specific backend implementations for all USB test categories.

Contains four backend classes consumed by api_intf_usb.py:

  - USBDeviceDetectionWindows  → USB-001 device detection (Get-PnpDevice)
  - USBMassStorageWindows      → USB-002 mass storage R/W (fsutil + robocopy)
  - USBDataIntegrityWindows    → USB-003 data integrity (Get-FileHash)
  - USBSerialFT232Windows      → USB-004 FT232 serial loopback (COMx)

Each method returns a consistent (output, error, exit_status) tuple,
matching the convention used across all OS utility modules in this
framework.

All commands execute on the remote Windows target via SSH
(exec_cmd with "ssh").
"""

import re

# ===========================================================================
# USB-001 — Device Detection
# ===========================================================================

class USBDeviceDetectionWindows:
    """
    Windows backend for USB device enumeration and descriptor inspection.

    Uses PowerShell ``Get-PnpDevice`` to enumerate USB devices.

    Parameters
    ----------
    platform_obj : object
        Active platform connection exposing ``exec_cmd(cmd, mode)``.
    """

    def __init__(self, platform_obj):
        self.platform_obj = platform_obj

    def list_devices(self):
        """
        List all present USB devices via ``Get-PnpDevice``.

        Returns
        -------
        tuple[str, str, int]
            ``(output, error, exit_status)``

        Example output
        --------------
        ::

            Status  Class      FriendlyName
            ------  -----      ------------
            OK      USB        USB Mass Storage Device
            OK      Ports      USB Serial Port (COM3)
        """
        cmd = (
            'powershell -Command "'
            'Get-PnpDevice -PresentOnly '
            "| Where-Object { $_.Class -match 'USB|Ports|DiskDrive' } "
            '| Select-Object Status, Class, FriendlyName '
            '| Format-Table -AutoSize"'
        )
        return self.platform_obj.exec_cmd(cmd, "ssh")

    def get_device_details(self, instance_id_pattern: str):
        """
        Retrieve detailed properties for a USB device matching a pattern.

        Parameters
        ----------
        instance_id_pattern : str
            Partial InstanceId or FriendlyName to match,
            e.g. ``"VID_0403&PID_6001"`` or ``"FT232"``.

        Returns
        -------
        tuple[str, str, int]
            ``(output, error, exit_status)``
        """
        cmd = (
            'powershell -Command "'
            'Get-PnpDevice -PresentOnly '
            f"| Where-Object {{ $_.InstanceId -match '{instance_id_pattern}' "
            f"  -or $_.FriendlyName -match '{instance_id_pattern}' }} "
            '| Select-Object Status, Class, FriendlyName, InstanceId, Manufacturer '
            '| Format-List"'
        )
        return self.platform_obj.exec_cmd(cmd, "ssh")

    @staticmethod
    def parse_non_hub_device(pnp_output: str):
        """
        Extract the first non-hub USB device FriendlyName from
        ``Get-PnpDevice`` output.

        Skips ``USB Root Hub`` and ``Generic USB Hub`` entries.

        Parameters
        ----------
        pnp_output : str
            Raw stdout from :meth:`list_devices`.

        Returns
        -------
        str or None
            FriendlyName of first peripheral, or ``None`` if only hubs found.
        """
        for line in pnp_output.splitlines():
            if re.search(r"OK\s+", line) and not re.search(
                r"Root Hub|Generic Hub", line, re.IGNORECASE
            ):
                parts = line.split()
                if len(parts) >= 3:
                    return " ".join(parts[2:])
        return None


# ===========================================================================
# USB-002 — Mass Storage R/W
# ===========================================================================

class USBMassStorageWindows:
    """
    Windows backend for USB mass storage mount, R/W speed test, and teardown.

    Uses ``fsutil`` for file creation and ``robocopy`` for copy/speed metrics.

    Parameters
    ----------
    platform_obj : object
        Active platform connection.
    drive_letter : str
        Drive letter of the USB mass storage device.  Default: ``"E:"``.
    test_file : str
        Temporary test filename.  Default: ``"test_write.bin"``.
    file_size_mb : int
        Size of the test file in MB.  Default: ``256``.
    """

    _SPEED_PATTERN = re.compile(
        r"([\d.]+)\s*(MB/s|GB/s|KB/s|Bytes/sec)", re.IGNORECASE
    )
    _ROBOCOPY_SPEED_PATTERN = re.compile(
        r"Speed\s*:\s*([\d,]+)\s*Bytes/sec", re.IGNORECASE
    )

    def __init__(
        self,
        platform_obj,
        drive_letter: str = "E:",
        test_file: str = "test_write.bin",
        file_size_mb: int = 256,
    ):
        self.platform_obj = platform_obj
        self.drive_letter = drive_letter.rstrip("\\")
        self.test_file    = test_file
        self.file_size_mb = file_size_mb

    @property
    def _test_file_path(self) -> str:
        return f"{self.drive_letter}\\{self.test_file}"

    @property
    def _file_size_bytes(self) -> int:
        return self.file_size_mb * 1024 * 1024

    def check_drive(self):
        """
        Confirm drive is accessible and show capacity via ``Get-PSDrive``.

        Returns
        -------
        tuple[str, str, int]
        """
        drive_name = self.drive_letter.rstrip(":\\")
        cmd = (
            'powershell -Command "'
            f"$d = Get-PSDrive -Name '{drive_name}' -ErrorAction Stop; "
            "Write-Output ($d.Name + ': Used=' + [math]::Round($d.Used/1MB,1) + 'MB Free=' + [math]::Round($d.Free/1MB,1) + 'MB')\""
        )
        return self.platform_obj.exec_cmd(cmd, "ssh")

    def mount_device(self):
        """
        Alias for :meth:`check_drive` — Windows drives need no mounting.

        Returns
        -------
        tuple[str, str, int]
        """
        return self.check_drive()

    def write_speed_test(self):
        """
        Sequential write test using ``fsutil file createnew``.

        Creates a zero-filled file of :attr:`file_size_mb` MB.

        Returns
        -------
        tuple[str, str, int]
        """
        cmd = (
            'powershell -Command "'
            f"$start = Get-Date; "
            f"fsutil file createnew {self._test_file_path} {self._file_size_bytes}; "
            f"$elapsed = (Get-Date) - $start; "
            f"$speed = {self._file_size_bytes} / $elapsed.TotalSeconds / 1MB; "
            "Write-Output ('Write speed: ' + [math]::Round($speed, 2) + ' MB/s')\""
        )
        return self.platform_obj.exec_cmd(cmd, "ssh")

    def read_speed_test(self):
        """
        Sequential read test by reading the test file into a null stream.

        Returns
        -------
        tuple[str, str, int]
        """
        cmd = (
            'powershell -Command "'
            f"$start = Get-Date; "
            f"$bytes = [System.IO.File]::ReadAllBytes('{self._test_file_path}'); "
            f"$elapsed = (Get-Date) - $start; "
            f"$speed = $bytes.Length / $elapsed.TotalSeconds / 1MB; "
            "Write-Output ('Read speed: ' + [math]::Round($speed, 2) + ' MB/s')\""
        )
        return self.platform_obj.exec_cmd(cmd, "ssh")

    def cleanup(self):
        """
        Remove the test file from the USB drive.

        Returns
        -------
        tuple[str, str, int]
        """
        cmd = f'powershell -Command "Remove-Item -Force \'{self._test_file_path}\'"'
        return self.platform_obj.exec_cmd(cmd, "ssh")

    def parse_speed(self, text: str):
        """
        Extract transfer speed from PowerShell output.

        Returns
        -------
        tuple[float, str] or tuple[None, None]
        """
        match = self._SPEED_PATTERN.search(text)
        if match:
            val = float(match.group(1).replace(",", ""))
            return val, match.group(2)
        return None, None


# ===========================================================================
# USB-003 — Data Integrity MD5
# ===========================================================================

class USBDataIntegrityWindows:
    """
    Windows backend for USB MD5 data integrity verification.

    Uses PowerShell ``Get-FileHash`` with MD5 algorithm.

    Parameters
    ----------
    platform_obj : object
        Active platform connection.
    drive_letter : str
        Drive letter of the USB device.  Default: ``"E:"``.
    source_file : str
        Temporary source file on Windows temp dir.
        Default: ``"C:\\Windows\\Temp\\source.bin"``.
    dest_file : str
        Destination filename on the USB drive.  Default: ``"integrity.bin"``.
    file_size_mb : int
        Size of random test data in MB.  Default: ``50``.
    """

    _MD5_PATTERN = re.compile(r"\bMD5\s+([0-9A-Fa-f]{32})\b|\b([0-9A-Fa-f]{32})\b")

    def __init__(
        self,
        platform_obj,
        drive_letter: str = "E:",
        source_file: str = "C:\\Windows\\Temp\\source.bin",
        dest_file: str = "integrity.bin",
        file_size_mb: int = 50,
    ):
        self.platform_obj = platform_obj
        self.drive_letter = drive_letter.rstrip("\\")
        self.source_file  = source_file
        self.dest_file    = dest_file
        self.file_size_mb = file_size_mb

    @property
    def _dest_path(self) -> str:
        return f"{self.drive_letter}\\{self.dest_file}"

    @property
    def _file_size_bytes(self) -> int:
        return self.file_size_mb * 1024 * 1024

    def generate_source_file(self):
        """
        Generate a random binary source file using PowerShell RNG.

        Returns
        -------
        tuple[str, str, int]
        """
        cmd = (
            'powershell -Command "'
            f"$bytes = New-Object byte[] {self._file_size_bytes}; "
            "(New-Object System.Random).NextBytes($bytes); "
            f"[System.IO.File]::WriteAllBytes('{self.source_file}', $bytes); "
            f"Write-Output 'Generated: {self.source_file}'\""
        )
        return self.platform_obj.exec_cmd(cmd, "ssh")

    def compute_md5(self, file_path: str):
        """
        Compute MD5 checksum of a file using ``Get-FileHash``.

        Parameters
        ----------
        file_path : str
            Absolute Windows path of the file to hash.

        Returns
        -------
        tuple[str, str, int]

        Example output
        --------------
        ::

            Algorithm  Hash                              Path
            ---------  ----                              ----
            MD5        D41D8CD98F00B204E9800998ECF8427E  C:\\file.bin
        """
        cmd = (
            'powershell -Command "'
            f"$h = Get-FileHash -LiteralPath '{file_path}' -Algorithm MD5 "
            "-ErrorAction Stop; "
            "Write-Output ('MD5 ' + $h.Hash + ' ' + $h.Path)\""
        )
        return self.platform_obj.exec_cmd(cmd, "ssh")

    def copy_to_drive(self):
        """
        Copy source file to USB drive and flush write cache.

        Returns
        -------
        tuple[str, str, int]
        """
        cmd = (
            'powershell -Command "'
            f"Copy-Item -LiteralPath '{self.source_file}' "
            f"-Destination '{self._dest_path}' -Force; "
            f"$f = [System.IO.File]::Open('{self._dest_path}', 'Open', 'Read'); "
            "$f.Close(); "
            f"Write-Output 'Copied to: {self._dest_path}'\""
        )
        return self.platform_obj.exec_cmd(cmd, "ssh")

    def verify_md5_on_drive(self):
        """
        Compute MD5 of the copied file on the USB drive.

        Returns
        -------
        tuple[str, str, int]
        """
        return self.compute_md5(self._dest_path)

    def compare_checksums(self, source_md5_output: str, dest_md5_output: str):
        """
        Compare two ``Get-FileHash`` output strings in Python.

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
        Remove copied file from USB drive and delete source temp file.

        Returns
        -------
        tuple[str, str, int]
        """
        cmd = (
            'powershell -Command "'
            f"Remove-Item -Force '{self._dest_path}'; "
            f"Remove-Item -Force '{self.source_file}'; "
            "Write-Output 'Cleanup done'\""
        )
        return self.platform_obj.exec_cmd(cmd, "ssh")

    def _extract_md5(self, md5_output: str) -> str:
        match = self._MD5_PATTERN.search(md5_output)
        if match:
            return (match.group(1) or match.group(2)).upper()
        return ""


# ===========================================================================
# USB-004 — Serial FT232 Loopback
# ===========================================================================

class USBSerialFT232Windows:
    """
    Windows backend for FT232/PL2303 USB-to-UART serial loopback testing.

    Uses PowerShell to detect the COM port via ``Get-PnpDevice`` and
    executes the loopback Python script on the Windows target over SSH.

    Parameters
    ----------
    platform_obj : object
        Active platform connection.
    com_port : str
        Serial COM port on the Windows target.  Default: ``"COM3"``.
    baud : int
        Baud rate.  Default: ``115200``.
    loopback_script_path : str
        Path of ``usb_loopback.py`` on the Windows target.
        Default: ``"C:\\Temp\\usb_loopback.py"``.
    vid_pid_pattern : str
        VID/PID pattern to match in ``Get-PnpDevice`` InstanceId.
        Default: ``"VID_0403&PID_6001"`` (FT232).
        Use ``"VID_067B&PID_2303"`` for PL2303.
    """

    _RESULT_PATTERN = re.compile(r"Result:\s+(\d+)/(\d+)\s+passed", re.IGNORECASE)
    _COM_PATTERN    = re.compile(r"\((COM\d+)\)")

    def __init__(
        self,
        platform_obj,
        com_port: str = "COM3",
        baud: int = 115200,
        loopback_script_path: str = "C:\\Temp\\usb_loopback.py",
        vid_pid_pattern: str = "VID_0403&PID_6001",
    ):
        self.platform_obj        = platform_obj
        self.com_port            = com_port
        self.baud                = baud
        self.loopback_script_path = loopback_script_path
        self.vid_pid_pattern     = vid_pid_pattern

    def detect_ft232(self):
        """
        Detect FT232/PL2303 device on Windows via ``Get-PnpDevice``.

        Matches on :attr:`vid_pid_pattern` in the device InstanceId.

        Returns
        -------
        tuple[str, str, int]

        Example output
        --------------
        ::

            Status  Class  FriendlyName
            ------  -----  ------------
            OK      Ports  USB Serial Port (COM3)
        """
        cmd = (
            'powershell -Command "'
            'Get-PnpDevice -PresentOnly '
            f"| Where-Object {{ $_.InstanceId -match '{self.vid_pid_pattern}' "
            f"  -or $_.FriendlyName -match 'FT232|PL2303|Prolific|Serial Port' }} "
            '| Select-Object Status, Class, FriendlyName, InstanceId '
            '| Format-Table -AutoSize"'
        )
        return self.platform_obj.exec_cmd(cmd, "ssh")

    def check_com_port(self):
        """
        List all present serial COM ports and find the one matching the
        USB-serial adapter via VID/PID pattern or FriendlyName.

        Does NOT filter by a specific COM number — the OS assigns the
        COM number dynamically, so we enumerate all Ports and let
        :meth:`extract_com_port` pick the right one.

        Returns
        -------
        tuple[str, str, int]

        Example output
        --------------
        ::

            OK  Ports  USB-SERIAL CH340 (COM5)
        """
        cmd = (
            'powershell -Command "'
            'Get-PnpDevice -PresentOnly -Class Ports '
            f"| Where-Object {{ $_.InstanceId -match '{self.vid_pid_pattern}' "
            f"  -or $_.FriendlyName -match 'PL2303|FT232|Prolific|CH340|USB Serial|USB-SERIAL' }} "
            '| Select-Object Status, Class, FriendlyName '
            '| Format-Table -AutoSize"'
        )
        return self.platform_obj.exec_cmd(cmd, "ssh")

    def extract_com_port(self, pnp_output: str) -> str:
        """
        Extract COM port name from ``Get-PnpDevice`` FriendlyName output.

        Parameters
        ----------
        pnp_output : str
            Raw stdout from :meth:`detect_ft232` or :meth:`check_com_port`.

        Returns
        -------
        str
            COM port string e.g. ``"COM3"``, or ``""`` if not found.
        """
        match = self._COM_PATTERN.search(pnp_output)
        return match.group(1) if match else ""

    def run_loopback_test(self, com_port: str = None, baud: int = None, port: str = None):
        """
        Execute ``usb_loopback.py`` on the Windows target via SSH.

        Parameters
        ----------
        com_port : str, optional
            Overrides :attr:`com_port` if provided.
        baud : int, optional
            Overrides :attr:`baud` if provided.

        Returns
        -------
        tuple[str, str, int]

        Example output
        --------------
        ::

            PASS | Sent: b'HELLO_BBB'           | Got: b'HELLO_BBB'
            PASS | Sent: b'LOOPBACK_01'         | Got: b'LOOPBACK_01'
            PASS | Sent: b'DATA_XYZ'            | Got: b'DATA_XYZ'
            PASS | Sent: b'\\xde\\xad\\xbe\\xef' | Got: b'\\xde\\xad\\xbe\\xef'

            Result: 4/4 passed
        """
        port = com_port or port or self.com_port
        baud = baud or self.baud
        cmd  = (
            f"python {self.loopback_script_path} "
            f"--port {port} "
            f"--baud {baud}"
        )
        return self.platform_obj.exec_cmd(cmd, "ssh")

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