# framework/utilities/os_utils/spi/base_spi.py
from abc import ABC, abstractmethod


class BaseSPI(ABC):
    """
    Abstract base class for SPI utilities.
    Defines the contract for SPI operations across OS implementations.
    """

    @abstractmethod
    def device_detection(self):
        """Return command string for SPI device detection"""
        pass

    @abstractmethod
    def loopback(self):
        """Return command string for SPI loopback test"""
        pass

    @abstractmethod
    def speed_mode(self):
        """Return command string for SPI speed & mode test"""
        pass

    @abstractmethod
    def data_integrity(self):
        """Return command string for SPI data integrity test"""
        pass
