import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add project root BEFORE any framework imports
current = Path(__file__).resolve()

for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break 

import importlib

class CpuUtil:

    @staticmethod
    def get_core_count(platform_obj):
        os_type = platform_obj.os_type.lower()
        module = importlib.import_module(
            f"framework.utils.os_utils.{os_type}.cpu_utils"
        )
        return module.CpuUtil.get_core_count(platform_obj)


    @staticmethod
    def get_cpu_info(platform_obj):
        os_type = platform_obj.os_type.lower()
        module = importlib.import_module(
            f"framework.utils.os_utils.{os_type}.cpu_utils"
        )
        return module.CpuUtil.get_cpu_info(platform_obj)

# class CpuUtil:

#     @staticmethod
#     def get_core_count(platform):
#         os_type = platform.get_os()
#         if os_type == "linux":
#             command = "nproc"
#         elif os_type == "windows":
#             command = "wmic cpu get NumberOfCores"
#         else:
#             raise Exception(f"Unsupported OS: {os_type}")
#         output, error, status = platform.execute(command)
#         if status != 0:
#             raise Exception("Failed to get CPU core count")
#         return output, error, status
#         #return CpuUtil._parse_core_count(output, os_type)


#     @staticmethod
#     def _parse_core_count(output, os_type):
#         if os_type == "linux":
#             return int(output.strip())
#         elif os_type == "windows":
#             lines = output.splitlines()
#             return int(lines[1].strip())