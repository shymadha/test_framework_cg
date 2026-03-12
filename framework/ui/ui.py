import os
import sys
import importlib
import json
import socket
import gradio as gr
from pathlib import Path
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
    """Find the first available TCP port in the given range."""
    for port in range(start_port, max_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise OSError(f"No free port found in range {start_port}-{max_port}")

# ---------------------------
# Project structure / sys.path
# ---------------------------
# Assuming this file is at: <repo_root>/framework/ui/ui Copy.py
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Also add 'framework' folder to sys.path to support internal relative-like imports 
# (e.g. 'from tests.base_test' or 'from core.testbed_utils')
framework_dir = project_root / "framework"
if str(framework_dir) not in sys.path:
    sys.path.insert(0, str(framework_dir))

# Optional import (kept, in case your framework relies on it elsewhere)
try:
    from framework.core.testbed_utils import TestbedUtils  # noqa: F401
except Exception:
    # Safe to continue if this import isn't strictly required for UI
    pass

# ---------------------------
# Discovery
# ---------------------------
def discover_all_test_classes():
    """
    Discover all test classes under 'framework.tests' using pkgutil for reliability.
    """
    base_pkg_name = "framework.tests"
    tests = []
    skipped = []
    
    try:
        # In case it's not in sys.modules yet
        if base_pkg_name not in sys.modules:
            try:
                base_pkg = importlib.import_module(base_pkg_name)
            except ImportError:
                # Fallback to absolute path discovery if import fails
                return _discover_fallback()
        else:
            base_pkg = sys.modules[base_pkg_name]
        
        for finder, mod_name, ispkg in pkgutil.walk_packages(base_pkg.__path__, base_pkg.__name__ + "."):
            if mod_name.endswith(".base_test"):
                continue
            try:
                m = importlib.import_module(mod_name)
                for cname, obj in inspect.getmembers(m, inspect.isclass):
                    if obj.__module__ == m.__name__ and cname.endswith("Test") and cname != "BaseTest":
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
    """Fallback discovery if pkgutil fails due to path issues."""
    tests_dir = project_root / "framework" / "tests"
    tests = []
    skipped = []
    if not tests_dir.exists():
        return [], [("framework.tests", f"Directory not found context: {tests_dir}")]
    for root, _, files in os.walk(tests_dir):
        for f in files:
            if f.endswith(".py") and not f.startswith("__") and f != "base_test.py":
                rel = os.path.relpath(root, tests_dir)
                mod = f"framework.tests.{rel.replace(os.sep, '.')}.{f[:-3]}" if rel != "." else f"framework.tests.{f[:-3]}"
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
    if file_obj is None:
        return {}
    try:
        with open(file_obj.name, 'r') as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}

# ---------------------------
# Execution
# ---------------------------
def _run_single_test(config_file, module_path, class_name):
    """
    Run a single test class and return a rich string report.
    """
    original_argv = sys.argv
    buf = io.StringIO()

    # Prepare argv for ParseUserInput to find the config, if your framework needs it
    sys.argv = [sys.executable, "--config", config_file.name]

    start_ts = time.time()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        # Clear all existing logging handlers so they recreate with our redirected stdout/stderr
        import logging
        logging.getLogger().handlers.clear()
        for name in logging.root.manager.loggerDict:
            logging.getLogger(name).handlers.clear()

        try:
            test_module = importlib.import_module(module_path)
            importlib.reload(test_module)

            test_class = getattr(test_module, class_name, None)
            if test_class is None or not inspect.isclass(test_class):
                raise RuntimeError(f"Could not find class '{class_name}' in module '{module_path}'")

            test_instance = test_class()

            # Run the test
            test_instance.run()

            # Try to extract result fields robustly
            result_obj = getattr(test_instance, "result", None)
            passed = getattr(result_obj, "passed", None)
            message = getattr(result_obj, "message", "")
            duration = getattr(result_obj, "duration", None)
            extra_fields = []
            # If your Result has other useful fields, include them safely
            for name in ("details", "data", "errors", "warnings"):
                if hasattr(result_obj, name):
                    extra_fields.append((name, getattr(result_obj, name)))

            status = "PASS" if passed else "FAIL" if passed is not None else "UNKNOWN"

        except Exception as e:
            status = "EXCEPTION"
            message = f"{e}\n\n{traceback.format_exc()}"
            extra_fields = []
        finally:
            sys.argv = original_argv

    end_ts = time.time()
    captured_output = buf.getvalue()
    buf.close()

    # Build a rich, readable block
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
    lines.append("")  # blank line
    return "\n".join(lines)

def execute_tests(config_file, selected_tests_ids):
    """
    Run one, many, or all tests based on 'selected_tests_ids' (list of "<module>:<ClassName>").
    If user didn't select anything, we run ALL discovered tests.
    Returns a big string report.
    """
    if not config_file:
        return "Error: Please upload a testbed.json file first."

    discovered, skipped = discover_all_test_classes()
    id_to_item = {t["id"]: t for t in discovered}

    # If none selected, run all
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
            header += f"\nWARNING: {len(missing)} tests were not found and will be skipped:\n  - " + "\n  - ".join(missing)

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

    # Summary
    summary_pass = 0
    summary_fail = 0
    summary_unknown = 0
    # Very light post-parse for summary:
    for block in report_lines:
        if isinstance(block, str) and block.startswith("=" * 100):
            # next lines include STATUS
            pass  # we already have rich blocks; optional to parse again

    return "\n".join(report_lines)

# ---------------------------
# UI
# ---------------------------
def refresh_test_choices():
    """
    Returns (choices, info_md)
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

with gr.Blocks(title="Test Framework UI") as demo:
    gr.Markdown("# 🚀 Test Automation Framework UI")
    gr.Markdown("Upload your testbed configuration, select one or more tests, and run them. The full logs will be shown.")

    with gr.Row():
        with gr.Column(scale=1):
            config_file = gr.File(label="1. Upload testbed.json", file_types=[".json"])
            json_display = gr.JSON(label="Testbed Contents")

        with gr.Column(scale=1):
            initial_choices, initial_md = refresh_test_choices()
            test_info = gr.Markdown(initial_md)
            test_selector = gr.CheckboxGroup(
                choices=initial_choices,
                label="2. Select Test(s) (leave empty to run ALL)",
                info="Format: framework.tests.<module>:<ClassName>",
            )
            refresh_btn = gr.Button("↻ Refresh Tests")
            run_button = gr.Button("▶️ Run Selected / All", variant="primary")

    with gr.Row():
        # Bigger area to show full logs nicely
        output = gr.Code(label="Test Execution Output (full)", language="shell")
    with gr.Row():
        # Simple download – we’ll write text to a temp file
        download_btn = gr.File(label="Download Latest Output", interactive=False)

    # Interactions
    def _on_config_change(file_obj):
        return load_json_content(file_obj)

    config_file.change(_on_config_change, inputs=config_file, outputs=json_display)

    def _on_refresh():
        choices, info_md = refresh_test_choices()
        return gr.update(choices=choices), gr.update(value=info_md)

    refresh_btn.click(_on_refresh, outputs=[test_selector, test_info])

    def _on_run(config_file_obj, selected_ids):
        report = execute_tests(config_file_obj, selected_ids)
        # write to temp file so user can download
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = Path(f"test_report_{ts}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(report)
        return report, str(out_path)

    run_button.click(
        _on_run,
        inputs=[config_file, test_selector],
        outputs=[output, download_btn]
    )

    # Automatically refresh test list when page loads
    demo.load(_on_refresh, outputs=[test_selector, test_info])

    gr.Markdown("---")
    gr.Markdown("### Folder Structure Notes")
    gr.Markdown("""
- **Tests Location**: `framework/tests/`
- **UI Location**: `ui/ui.py`
- **Testbed**: Uploaded via UI (copied to temporary storage by Gradio)
    """)

if __name__ == "__main__":
    port = find_free_port()
    print(f"Starting UI on http://127.0.0.1:{port}")
    demo.launch(server_name="127.0.0.1", server_port=port, share=False)
