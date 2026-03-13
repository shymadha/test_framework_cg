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

