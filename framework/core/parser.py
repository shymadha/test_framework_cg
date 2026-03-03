# parse_user_input.py

import argparse
import json
from pathlib import Path


class ParseUserInput:
    def __init__(self):
        self.args = self._parse_arguments()
        self.config = self._load_config(self.args.config)
        print(f"The self.config is {self.config} " )
        self.test_files = self._collect_test_files(
            self.args.test,
            self.args.test_folder
        )
        print(f"The self.test_files  is {self.test_files} " )
        self.test_metadata=self.get_test_metadata()
        
    def _parse_arguments(self):
        parser = argparse.ArgumentParser(
            description="Test Runner CLI"
        )

        parser.add_argument(
            "--config",
            required=True,
            help="Path to configuration JSON file"
        )

        group = parser.add_mutually_exclusive_group(required=True)

        group.add_argument(
            "--test",
            nargs="+",
            help="Path to one or more test files"
        )

        group.add_argument(
            "--test-folder",
            help="Path to folder containing test files"
        )

        return parser.parse_args()

    def _load_config(self, config_path):
        path= Path(config_path).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with path.open("r") as f:
            return json.load(f)

    def _collect_test_files(self, test_files, test_folder):
        collected = []

        if test_files:
            for file in test_files:
                path = Path(file).expanduser().resolve()
                if not path.is_file():
                    raise FileNotFoundError(f"Test file not found: {file}")
                collected.append(path)

        if test_folder:
            folder = Path(test_folder).expanduser().resolve()
            if not folder.is_dir():
                raise NotADirectoryError(f"Folder not found: {test_folder}")

            collected.extend(folder.glob("*.py"))

        if not collected:
            raise ValueError("No valid test files found.")

        return collected


    def get_test_metadata(self):
        metadata = []

        for test_file in self.test_files:
            path = Path(test_file).resolve()
            project_root = Path.cwd().resolve()
            relative_path = path.relative_to(project_root)

            module_path = ".".join(
                relative_path.with_suffix("").parts
            )

            class_name = "".join(
                part.capitalize()
                for part in path.stem.split("_")
            )

            metadata.append({
                "module_path": module_path,
                "class_name": class_name
            })

        return metadata

# from pathlib import Path
# import json

# from pathlib import Path
# import json

# def parse_input(config_path: str | Path) -> dict:
#     """
#     Load config from a path. Supports relative or absolute paths.
#     Resolves relative to current working directory.
#     """
#     p = Path(config_path).expanduser().resolve() if not Path(config_path).is_absolute() else Path(config_path)
#     if not p.exists():
#         # Helpful diagnostics
#         cwd = Path.cwd()
#         raise FileNotFoundError(
#             f"Config not found: {p}\n"
#             f"Current working directory: {cwd}\n"
#             f"Tip: run from project root or pass an absolute path."
#         )
#     with p.open("r", encoding="utf-8") as f:
#         return json.load(f)
