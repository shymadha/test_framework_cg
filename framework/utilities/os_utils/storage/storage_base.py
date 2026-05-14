# storage_base.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.os_base import OSBase


class StorageBase(OSBase):
    """
    Abstract base class defining the contract for storage-related OS utilities.

    Concrete OS-specific classes (StorageLinux, StorageWindows) must inherit
    from this base and implement all defined methods.

    Inherits from
    -------------
    OSBase
        Provides platform execution utilities used by storage operations.
    """

    def check_disk_space(self):
        """
        Retrieve disk space usage statistics.

        Returns
        -------
        tuple
            (output, error, exit_status)

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError("Must be implemented in derived classes")

    def test_sequential_read(self):
        """
        Run a sequential read performance test.

        Returns
        -------
        tuple
            (output, error, exit_status)

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError("Must be implemented in derived classes")

    def test_sequential_write(self):
        """
        Run a sequential write performance test.

        Returns
        -------
        tuple
            (output, error, exit_status)

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError("Must be implemented in derived classes")

    def test_random_read_write(self):
        """
        Run a random read/write performance test.

        Returns
        -------
        tuple
            (output, error, exit_status)

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError("Must be implemented in derived classes")

    def test_data_integrity(self):
        """
        Verify data integrity by writing and reading back a file.

        Returns
        -------
        tuple
            (output, error, exit_status)

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError("Must be implemented in derived classes")

    def test_repeated_write(self):
        """
        Run a repeated write endurance test.

        Returns
        -------
        tuple
            (output, error, exit_status)

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError("Must be implemented in derived classes")
