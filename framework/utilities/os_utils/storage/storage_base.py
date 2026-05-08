import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.os_base import OSBase


class StorageBase(OSBase):
    """
    Abstract base class defining the contract for Storage-related OS utilities.
    """

    def sequential_write(self, file_path, size_mb):
        raise NotImplementedError("Must be implemented in derived classes")

    def sequential_read(self, file_path):
        raise NotImplementedError("Must be implemented in derived classes")

    def random_rw(self, file_path, size_mb):
        raise NotImplementedError("Must be implemented in derived classes")

    def data_integrity(self, file_path):
        raise NotImplementedError("Must be implemented in derived classes")

    def disk_space(self, drive_or_mount):
        raise NotImplementedError("Must be implemented in derived classes")

    def repeated_write(self, file_path, size_mb, cycles):
        raise NotImplementedError("Must be implemented in derived classes")
