import sys
import os
from pathlib import Path

# Setup path
current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break

from framework.ui.ui import discover_all_test_classes

tests, skipped = discover_all_test_classes()
print(f"Total tests discovered: {len(tests)}")
print("\nMemory tests found:")
found_memory = False
for t in tests:
    if "memory" in t["id"]:
        print(f" - {t['id']}")
        found_memory = True

if not found_memory:
    print("No memory tests found!")

if skipped:
    print("\nSkipped modules:")
    for s in skipped:
        print(f" - {s[0]}: {s[1]}")
