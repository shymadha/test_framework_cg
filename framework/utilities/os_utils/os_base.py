# os_base.py
"""
Base OS class providing a common interface for all OS-specific implementations.
All OS-specific classes (Windows/Linux) must inherit from OSBase.
"""
import platform
import socket
import time
#import psutil

class OSBase:
    def __init__(self, platform_obj):
        self.platform_obj = platform_obj
        
        self.os_name = None
        self.os_version= None
        self.host_name = None

        # System API Interfaces (CPU, Disk, other modules)
        self.cpu = None
        self.ethernet= None
        self.disk = None
        
        
    # ---------- OS Information APIs ----------
    def get_os_name(self):
        """Return operating system name"""
        self.os_name = platform.system()
        return self.os_name

    def get_os_version(self):
        """Must be implemented by each OS type"""
        self.get_os_version = platform.version()
        return self.get_os_version
        

    def get_hostname(self):
        """Must be implemented by each OS type"""
        self.hostname=socket.gethostname()
        return self.hostname
    
    # ---------- System Health APIs ----------
    def get_uptime(self):
        """Return system uptime (to be implemented by child class)."""
        pass
        # boot_time = psutil.boot_time()   # seconds since epoch
        # uptime_seconds = time.time() - boot_time
        # return uptime_seconds

    # ---------- Utility Debug ----------
    def dump_system_info(self):
        """Optional: Debug info for logging"""
        return {
            "os_name": self.get_os_name(),
            "hostname": self.get_hostname(),
            "version": self.get_os_version(),
        }