from pathlib import Path
import json

from pathlib import Path
import json

def parse_input(config_path: str | Path) -> dict:
    """
    Load config from a path. Supports relative or absolute paths.
    Resolves relative to current working directory.
    """
    p = Path(config_path).expanduser().resolve() if not Path(config_path).is_absolute() else Path(config_path)
    if not p.exists():
        # Helpful diagnostics
        cwd = Path.cwd()
        raise FileNotFoundError(
            f"Config not found: {p}\n"
            f"Current working directory: {cwd}\n"
            f"Tip: run from project root or pass an absolute path."
        )
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)
# def parse_input(config_path: str) -> dict:
#     with open(config_path, "r") as f:
#         return json.load(f)