import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.storage.storage_base import StorageBase


class StorageLinux(StorageBase):
    def __init__(self, platform_obj):
        super().__init__(platform_obj)
        self.platform_obj = platform_obj

    def sequential_write(self, file_path, size_mb):
        cmd = f"dd if=/dev/zero of={file_path} bs=1M count={size_mb} conv=fsync"
        return self.platform_obj.exec_cmd(cmd, "ssh")

    def sequential_read(self, file_path):
        cmd = f"dd if={file_path} of=/dev/null bs=1M"
        return self.platform_obj.exec_cmd(cmd, "ssh")

    def random_rw(self, file_path, size_mb):
        # Attempt fio first, otherwise python fallback
        cmd = f"fio --name=rand_rw --ioengine=sync --rw=randrw --bs=4k --size={size_mb}M --filename={file_path}"
        output, error, status = self.platform_obj.exec_cmd(cmd, "ssh")
        if status != 0:
            py_cmd = f"python3 -c \"import os, random; f=os.open('{file_path}', os.O_RDWR); [os.pread(f, 4096, random.randint(0, max(0, ({size_mb}*1024*1024)-4096))) for _ in range(100)]; os.close(f)\""
            output2, error2, status2 = self.platform_obj.exec_cmd(py_cmd, "ssh")
            return output2, f"{error} | fio failed, py fallback: {error2}", status2
        return output, error, status

    def data_integrity(self, file_path):
        cmd = f"md5sum {file_path}"
        return self.platform_obj.exec_cmd(cmd, "ssh")

    def disk_space(self, drive_or_mount="/"):
        cmd = f"df -h {drive_or_mount}"
        return self.platform_obj.exec_cmd(cmd, "ssh")

    def repeated_write(self, file_path, size_mb, cycles):
        cmd = f"for i in $(seq 1 {cycles}); do dd if=/dev/zero of={file_path}_${{i}} bs=1M count={size_mb} conv=fsync; done"
        return self.platform_obj.exec_cmd(cmd, "ssh")
