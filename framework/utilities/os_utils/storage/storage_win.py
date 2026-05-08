import sys
import os
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.storage.storage_base import StorageBase


class StorageWindows(StorageBase):
    def __init__(self, platform_obj):
        super().__init__(platform_obj)
        self.platform_obj = platform_obj

    def sequential_write(self, file_path, size_mb):
        cmd = f"powershell -command \"$f=[System.IO.File]::Create('{file_path}'); $f.SetLength({size_mb}MB); $f.Flush(); $f.Close()\""
        return self.platform_obj.exec_cmd(cmd, "ssh")

    def sequential_read(self, file_path):
        cmd = f"powershell -command \"Measure-Command {{ Get-Content -Path '{file_path}' | Out-Null }}\""
        return self.platform_obj.exec_cmd(cmd, "ssh")

    def random_rw(self, file_path, size_mb):
        cmd = f"fio --name=rand_rw --ioengine=windowsaio --rw=randrw --bs=4k --size={size_mb}M --filename='{file_path}'"
        output, error, status = self.platform_obj.exec_cmd(cmd, "ssh")
        if status != 0:
            # Fallback
            py_cmd = f"python -c \"import os, random; f=open('{file_path}', 'a+b'); f.close(); f=open('{file_path}', 'r+b'); [f.seek(random.randint(0, max(0, ({size_mb}*1024*1024)-4096))) or f.read(4096) for _ in range(100)]; f.close()\""
            output2, error2, status2 = self.platform_obj.exec_cmd(py_cmd, "ssh")
            return output2, f"{error} | fio failed, py fallback: {error2}", status2
        return output, error, status

    def data_integrity(self, file_path):
        cmd = f"powershell -command \"Get-FileHash -Path '{file_path}' -Algorithm MD5\""
        return self.platform_obj.exec_cmd(cmd, "ssh")

    def disk_space(self, drive_or_mount="C:"):
        cmd = f"powershell -command \"Get-PSDrive -PSProvider FileSystem | Where-Object {{ $_.Name -eq '{drive_or_mount.strip(':')}' }}\""
        return self.platform_obj.exec_cmd(cmd, "ssh")

    def repeated_write(self, file_path, size_mb, cycles):
        cmd = f"powershell -command \"for ($i=1; $i -le {cycles}; $i++) {{ $f=[System.IO.File]::Create('{file_path}_'+$i); $f.SetLength({size_mb}MB); $f.Flush(); $f.Close() }}\""
        return self.platform_obj.exec_cmd(cmd, "ssh")
