import sys
import os
from pathlib import Path
import importlib

current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break

modules = [
    "framework.tests.memory.mem_001_ram_size_info",
    "framework.tests.memory.mem_002_ram_rw_speed",
    "framework.tests.memory.mem_003_ram_stress",
    "framework.tests.memory.mem_004_ram_integrity",
    "framework.tests.memory.mem_005_memory_leak_detect"
]

results = {}
for mod_name in modules:
    try:
        importlib.import_module(mod_name)
        results[mod_name] = "OK"
    except Exception as e:
        results[mod_name] = f"ERROR: {e}"

for m, r in results.items():
    print(f"{m}: {r}")
