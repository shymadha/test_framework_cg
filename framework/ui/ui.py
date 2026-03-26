import sys
import os
from pathlib import Path

# Ensure project root is on sys.path (same as CPU tests)
current = Path(__file__).resolve()

for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break

import argparse
import importlib
import json
import socket
import gradio as gr
import io
import contextlib
import traceback
import pkgutil
import inspect
import time
from datetime import datetime


# ---------------------------
# Utility: pick a free port
# ---------------------------
def find_free_port(start_port=7862, max_port=7900):
    """
    Find and return the first available TCP port within the specified range.

    Parameters
    ----------
    start_port : int, optional
        Starting port number to scan. Defaults to 7862.
    max_port : int, optional
        Maximum port number to check. Defaults to 7900.

    Returns
    -------
    int
        The first free TCP port in the provided range.

    Raises
    ------
    OSError
        If no ports are available within the specified range.
    """
    for port in range(start_port, max_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise OSError(f"No free port found in range {start_port}-{max_port}")


# ---------------------------
# Discovery utilities
# ---------------------------
def discover_all_test_classes():
    """
    Discover all test classes defined under `framework.tests`.

    Uses `pkgutil.walk_packages` to recursively scan test modules.
    A class is considered a test class if:
      - Its name ends with 'Test'
      - It is not 'BaseTest'
      - It belongs to its module (no imported classes)

    Returns
    -------
    tuple
        (tests, skipped) where:
          - tests is a list of dictionaries containing:
                {"module", "class", "id"}
          - skipped is a list of modules that failed import with reasons
    """
    base_pkg_name = "framework.tests"
    tests = []
    skipped = []

    try:
        if base_pkg_name not in sys.modules:
            try:
                base_pkg = importlib.import_module(base_pkg_name)
            except ImportError:
                return _discover_fallback()
        else:
            base_pkg = sys.modules[base_pkg_name]

        for finder, mod_name, ispkg in pkgutil.walk_packages(
            base_pkg.__path__, base_pkg.__name__ + "."
        ):
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
        skipped.append(("framework.tests", str(e)))

    tests.sort(key=lambda x: x["id"])
    return tests, skipped


def _discover_fallback():
    """
    Fallback discovery method used when pkgutil import resolution fails.

    The fallback manually walks the `framework/tests` directory, attempting to
    import modules directly from filesystem paths.

    Returns
    -------
    tuple
        (tests, skipped) similar to discover_all_test_classes().
    """
    tests_dir = "project_root" / "framework" / "tests"
    tests = []
    skipped = []

    if not tests_dir.exists():
        return [], [("framework.tests", f"Directory not found: {tests_dir}")]

    for root, _, files in os.walk(tests_dir):
        for f in files:
            if f.endswith(".py") and not f.startswith("__") and f != "base_test.py":
                rel = os.path.relpath(root, tests_dir)
                mod = (
                    f"framework.tests.{rel.replace(os.sep, '.')}.{f[:-3]}"
                    if rel != "."
                    else f"framework.tests.{f[:-3]}"
                )

                try:
                    m = importlib.import_module(mod)
                    for cname, obj in inspect.getmembers(m, inspect.isclass):
                        if cname.endswith("Test") and cname != "BaseTest":
                            tests.append({"module": mod, "class": cname, "id": f"{mod}:{cname}"})
                except Exception as e:
                    skipped.append((mod, str(e)))

    tests.sort(key=lambda x: x["id"])
    return tests, skipped


def load_json_content(file_obj):
    """
    Load and return JSON content from an uploaded testbed file.

    Parameters
    ----------
    file_obj : gradio.File
        Uploaded JSON file object.

    Returns
    -------
    dict
        Parsed JSON content, or {"error": "..."} if parsing fails.
    """
    if file_obj is None:
        return {}
    try:
        with open(file_obj.name, 'r') as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}


# ---------------------------
# Execution utilities
# ---------------------------
def _run_single_test(config_file, module_path, class_name):
    """
    Execute a single test class instance and return a formatted string report.

    This function:
      - Temporarily overrides sys.argv so ParseUserInput can locate the config
      - Imports and reloads the test module
      - Instantiates and runs the test class
      - Captures stdout/stderr
      - Builds a detailed execution report block

    Parameters
    ----------
    config_file : gradio.File
        The uploaded testbed JSON file.
    module_path : str
        Full import path of the test module.
    class_name : str
        Name of the test class inside the module.

    Returns
    -------
    str
        A formatted multi-line report containing:
        - Status
        - Output logs
        - Message
        - Timestamps
        - Duration
        - Optional extra metadata
    """
    original_argv = sys.argv
    buf = io.StringIO()

    sys.argv = [sys.executable, "--config", config_file.name]

    start_ts = time.time()

    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        # Reset loggers
        import logging
        logging.getLogger().handlers.clear()
        for name in logging.root.manager.loggerDict:
            logging.getLogger(name).handlers.clear()

        try:
            test_module = importlib.import_module(module_path)
            importlib.reload(test_module)

            test_class = getattr(test_module, class_name, None)
            if test_class is None:
                raise RuntimeError(
                    f"Could not find class '{class_name}' in module '{module_path}'"
                )

            test_instance = test_class()
            test_instance.run()

            result_obj = getattr(test_instance, "result", None)

            passed = getattr(result_obj, "passed", None)
            message = getattr(result_obj, "message", "")
            duration = getattr(result_obj, "duration", None)

            extra_fields = []
            for name in ("details", "data", "errors", "warnings"):
                if hasattr(result_obj, name):
                    extra_fields.append((name, getattr(result_obj, name)))

            status = (
                "PASS" if passed else
                "FAIL" if passed is not None else
                "UNKNOWN"
            )

        except Exception as e:
            status = "EXCEPTION"
            message = f"{e}\n\n{traceback.format_exc()}"
            extra_fields = []

        finally:
            sys.argv = original_argv

    end_ts = time.time()
    captured_output = buf.getvalue()
    buf.close()

    lines = []
    lines.append("=" * 100)
    lines.append(f"TEST: {module_path}:{class_name}")
    lines.append(f"STATUS: {status}")
    if message:
        lines.append(f"MESSAGE: {message}")
    lines.append(f"STARTED: {datetime.fromtimestamp(start_ts).isoformat(timespec='seconds')}")
    lines.append(f"ENDED  : {datetime.fromtimestamp(end_ts).isoformat(timespec='seconds')}")
    lines.append(f"DURATION(s): {round(end_ts - start_ts, 3)}")
    if extra_fields:
        lines.append("--- EXTRA FIELDS ---")
        for k, v in extra_fields:
            try:
                v_str = json.dumps(v, indent=2, default=str)
            except Exception:
                v_str = str(v)
            lines.append(f"{k} = {v_str}")
    lines.append("--- EXECUTION LOGS (stdout & stderr) ---")
    lines.append(captured_output.strip() if captured_output.strip() else "(no logs)")
    lines.append("=" * 100)
    lines.append("")
    return "\n".join(lines)


def execute_tests(config_file, selected_tests_ids):
    """
    Execute one or more tests and return a consolidated report.

    Parameters
    ----------
    config_file : gradio.File
        Uploaded testbed.json file.
    selected_tests_ids : list of str
        List of test identifiers ("module:ClassName").
        If empty, all discovered tests are executed.

    Returns
    -------
    str
        A full execution report containing:
          - Discovery results
          - Execution blocks for each test
          - Summary metadata
    """
    if not config_file:
        return "Error: Please upload a testbed.json file first."

    discovered, skipped = discover_all_test_classes()
    id_to_item = {t["id"]: t for t in discovered}

    if not selected_tests_ids:
        selected = discovered
        header = f"Running ALL discovered tests ({len(discovered)})."
    else:
        selected = []
        missing = []
        for tid in selected_tests_ids:
            if tid in id_to_item:
                selected.append(id_to_item[tid])
            else:
                missing.append(tid)
        header = f"Running {len(selected)} selected tests."
        if missing:
            header += (
                "\nWARNING: The following tests were not found:\n  - "
                + "\n  - ".join(missing)
            )

    report_lines = []
    report_lines.append("# Test Execution Report")
    report_lines.append(header)

    if skipped:
        report_lines.append("")
        report_lines.append("## Skipped Modules During Discovery")
        for mod, reason in skipped:
            report_lines.append(f"- {mod}: {reason}")

    report_lines.append("")
    report_lines.append("## Results")

    for item in selected:
        mod = item["module"]
        cls = item["class"]
        one_report = _run_single_test(config_file, mod, cls)
        report_lines.append(one_report)

    return "\n".join(report_lines)


# ---------------------------
# UI Setup
# ---------------------------
def refresh_test_choices():
    """
    Refresh and return the list of discovered test choices for the UI.

    Returns
    -------
    tuple
        (choices, markdown_info) where:
          - choices is a list of test IDs for selection
          - markdown_info is a human-readable summary string
    """
    discovered, skipped = discover_all_test_classes()
    choices = [t["id"] for t in discovered]

    info_lines = []
    info_lines.append(f"Discovered {len(discovered)} test classes under 'framework.tests'.")
    if skipped:
        info_lines.append("")
        info_lines.append("**Skipped modules (import errors)**:")
        for mod, reason in skipped[:10]:
            info_lines.append(f"- {mod}: {reason}")
        if len(skipped) > 10:
            info_lines.append(f"... and {len(skipped) - 10} more")

    info_md = "\n".join(info_lines)
    return choices, info_md