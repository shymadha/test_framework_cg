import sys
import os
from pathlib import Path
import pkgutil
import importlib
import inspect

current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break

base_pkg_name = "framework.tests"
tests = []
skipped = []

try:
    base_pkg = importlib.import_module(base_pkg_name)
    print(f"Base package path: {base_pkg.__path__}")
    
    for finder, mod_name, ispkg in pkgutil.walk_packages(
        base_pkg.__path__, base_pkg.__name__ + "."
    ):
        print(f"Found module: {mod_name}")
        if mod_name.endswith(".base_test"):
            continue

        try:
            m = importlib.import_module(mod_name)
            for cname, obj in inspect.getmembers(m, inspect.isclass):
                if (
                    obj.__module__ == m.__name__
                    and cname.endswith("Test")
                    and cname != "BaseTest"
                ):
                    tests.append({
                        "module": mod_name,
                        "class": cname,
                        "id": f"{mod_name}:{cname}"
                    })
        except Exception as e:
            skipped.append((mod_name, str(e)))
except Exception as e:
    print(f"Error: {e}")

print(f"\nDiscovered {len(tests)} tests.")
print("\nMemory tests found:")
for test in tests:
    if "memory" in test['id']:
        print(f" - {test['id']}")

print("\nSkipped modules with 'memory' in name:")
for s in skipped:
    if "memory" in s[0]:
        print(f" - {s[0]}: {s[1]}")
