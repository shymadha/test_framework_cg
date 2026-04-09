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
import re
from datetime import datetime


# ---------------------------
# Utility: pick a free port
# ---------------------------
def find_free_port(start_port=7862, max_port=7900):
    """
    Find and return the first available TCP port within the specified range.
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
    """
    project_root = Path(__file__).resolve().parents[2]
    tests_dir = project_root / "framework" / "tests"
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
    """
    original_argv = sys.argv
    buf = io.StringIO()
    sys.argv = [sys.executable, "--config", config_file.name]
    start_ts = time.time()

    import logging
    import framework.core.logger as framework_logger

    # Save original setup_logger to restore it later
    original_setup_logger = framework_logger.setup_logger

    # Create a UI-specific handler for our buffer
    def get_ui_handler(stream):
        h = logging.StreamHandler(stream)
        h.terminator = '\n'
        h.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s', datefmt="%Y-%m-%d %H:%M:%S"))
        return h

    manipulated_loggers = {}

    # UI-friendly setup_logger version that forces output to our buffer
    def ui_setup_logger(name, **kwargs):
        l = logging.getLogger(name)
        if name not in manipulated_loggers:
            manipulated_loggers[name] = l.handlers[:]
        for h in l.handlers[:]:
            l.removeHandler(h)
        l.addHandler(get_ui_handler(buf))
        l.propagate = False
        l.setLevel(logging.INFO)
        return l

    # Apply monkeypatch to all potential import paths for the logger module
    all_logger_mods = [mod for name, mod in sys.modules.items() if name.endswith("core.logger") and hasattr(mod, "setup_logger")]
    for mod in all_logger_mods:
        mod.setup_logger = ui_setup_logger

    # Setup root logger as a fallback
    root_logger = logging.getLogger()
    root_original_handlers = root_logger.handlers[:]
    root_logger.handlers = [get_ui_handler(buf)]
    root_logger.setLevel(logging.INFO)

    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            try:
                test_module = importlib.import_module(module_path)
                importlib.reload(test_module)
                test_class = getattr(test_module, class_name, None)
                if test_class is None:
                    raise RuntimeError(f"Could not find class '{class_name}' in module '{module_path}'")
                test_instance = test_class()
                test_instance.run()

                result_obj = getattr(test_instance, "result", None)
                passed = getattr(result_obj, "passed", None)
                message = getattr(result_obj, "message", "")
                status = "PASS" if passed else "FAIL" if passed is not None else "UNKNOWN"
            except Exception as e:
                status = "EXCEPTION"
                message = f"{e}\n\n{traceback.format_exc()}"
    finally:
        for mod in all_logger_mods:
            mod.setup_logger = original_setup_logger
            
        # Remove our handlers from all active loggers to prevent I/O errors
        for name in logging.root.manager.loggerDict:
            l = logging.getLogger(name)
            l.handlers = [h for h in l.handlers if getattr(h, 'stream', None) is not buf]
            if name in manipulated_loggers:
                # Restore original handlers for this specific logger
                l.handlers = manipulated_loggers[name]
                
        root_logger.handlers = root_original_handlers
        sys.argv = original_argv

    end_ts = time.time()
    raw_output = buf.getvalue().strip()
    buf.close()

    # Safety: If logs are concatenated without newlines, add them using regex
    date_pattern = r'(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})'
    captured_output = re.sub(rf'(?<!^)(?<!\n){date_pattern}', r'\n\1', raw_output)

    status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    
    lines = []
    # Use a styled card for the test header
    header_color = "#28a745" if status == "PASS" else "#dc3545" if status == "FAIL" else "#ffc107"
    lines.append(f"<div style='border-left: 5px solid {header_color}; padding-left: 15px; margin-bottom: 20px;'>")
    lines.append(f"<h3 style='margin-bottom: 5px; color: {header_color};'>{status_icon} {class_name}</h3>")
    lines.append(f"<div style='font-size: 0.9em; opacity: 0.8;'><b>Module:</b> <code>{module_path}</code> | <b>Status:</b> {status} | <b>Duration:</b> {round(end_ts - start_ts, 3)}s</div>")
    if message:
        lines.append(f"<div style='margin-top: 10px; border-top: 1px solid #e5e7eb; padding-top: 5px;'><b>Message:</b> {message}</div>")
    lines.append("</div>")
    
    lines.append("\n<div style='margin-top: 15px; border: 2px solid #e5e7eb; border-radius: 10px; overflow: hidden;'>")
    lines.append("<div style='background-color: #3b69b5; padding: 10px 16px; display: flex; align-items: center; gap: 8px;'><b style='color: #ffffff; font-size: 14px; cursor: pointer;'>\U0001f4dc Execution Logs</b></div>")
    lines.append("<pre style='white-space: pre-wrap; font-family: \"Cascadia Code\", \"Consolas\", monospace; background-color: #f9fafb; color: #1E293B; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin: 0; line-height: 1.6; font-size: 13.5px;'>")
    lines.append(captured_output if captured_output else "(no logs)")
    lines.append("</pre>")
    lines.append("</div>")
    lines.append("\n<hr style='border: 0; border-top: 1px solid #e5e7eb; margin: 20px 0;'>\n")
    return "\n".join(lines)


def execute_tests(config_file, selected_tests_ids):
    """
    Execute one or more tests and return a consolidated report.
    """
    if not config_file:
        return "Error: Please upload a testbed.json file first."

    discovered, skipped = discover_all_test_classes()
    id_to_item = {t["id"]: t for t in discovered}

    if not selected_tests_ids:
        selected = discovered
        header = f"Running ALL discovered tests ({len(discovered)})."
    else:
        selected = [id_to_item[tid] for tid in selected_tests_ids if tid in id_to_item]
        header = f"Running {len(selected)} selected tests."

    report_lines = []
    report_lines.append("# Test Execution Report")
    report_lines.append(header)
    report_lines.append("\n## Results")

    for item in selected:
        report_lines.append(_run_single_test(config_file, item["module"], item["class"]))

    return "\n".join(report_lines)


def refresh_test_choices():
    """
    Refresh and return the list of discovered test choices for the UI.
    """
    discovered, skipped = discover_all_test_classes()
    choices = [t["id"] for t in discovered]
    info_md = f"Discovered {len(discovered)} test classes."
    return choices, info_md


def create_ui():
    """
    Construct the Gradio UI layout with centered headings and refined styling.
    """
    custom_css = """
        body, .gradio-container { background-color: #FAFAF6 !important; }
        
        /* Apply Corporate Blue/Ivory theme globally */
        :root, .dark, body.dark {
            --background-fill-primary: #FAFAF6 !important;
            --background-fill-secondary: #FAFAF6 !important;
            --block-background-fill: #ffffff !important;
            --panel-background-fill: #ffffff !important;
            --border-color-primary: #e5e7eb !important;
            --block-border-color: #e5e7eb !important;
            --body-text-color: #1E293B !important;
            --body-text-color-subdued: #475569 !important;
            --block-label-text-color: #1E293B !important;
            --input-background-fill: #ffffff !important;
            --button-secondary-background-fill: #ffffff !important;
            --button-secondary-background-fill-hover: #f3f4f6 !important;
            --button-secondary-text-color: #1E293B !important;
            --button-primary-background-fill: #3b69b5 !important;
            --button-primary-background-fill-hover: #2c528c !important;
            --button-primary-text-color: #ffffff !important;
        }

        .center-content { text-align: center; margin-bottom: 30px; }
        .section-header { text-align: center; padding: 10px; border-radius: 8px; margin-bottom: 20px !important; }
        footer { display: none !important; }

        /* Make Upload box extremely compact like the screenshot */
        .blue-upload .wrap {
            min-height: 0 !important;
        }
        .blue-upload [data-testid="file-upload"] {
            min-height: 0 !important;
            height: auto !important;
            padding: 8px !important;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        /* Fix dark mode background in uploaded file preview (which renders as an internal table) */
        .blue-upload table, .blue-upload tbody, .blue-upload tr, .blue-upload td, .blue-upload .file-preview, .blue-upload .file-preview-holder, .blue-upload .uploaded-file {
            background-color: #ffffff !important;
            color: #1E293B !important;
            border-color: #ffffff !important;
        }
        .blue-upload table *, .blue-upload tr *, .blue-upload td *, .blue-upload .uploaded-file * {
            color: #1E293B !important;
        }
        .blue-upload a, .blue-upload a:hover {
            color: #3b69b5 !important;
        }
        
        /* Fix completely faint labels like 'Select Tests' */
        .gradio-container label > span,
        .gradio-container span[data-testid="block-info"],
        .blue-dropdown label *,
        .blue-upload label * {
            color: #1E293B !important;
            opacity: 1 !important;
        }
        
        /* Base button styles */
        .blue-btn button, .run-btn button {
            border: 1px solid #e5e7eb !important;
            border-radius: 8px !important;
        }

        /* Fix dark mode token chips in dropdown */
        .gradio-container .token, .gradio-container div.token, .gradio-container [data-testid="dropdown"] .token {
            background-color: #ffffff !important;
            color: #1E293B !important;
            border: 1px solid #e5e7eb !important;
        }
        .gradio-container .token button, .gradio-container .token svg {
            color: #1E293B !important;
            fill: #1E293B !important;
        }
    """

    with gr.Blocks(title="Test Automation Framework") as demo:
        # Inject custom CSS safely for all Gradio versions
        gr.HTML(f"<style>{custom_css}</style>")
        
        # Centered Heading and Subtitle
        with gr.Column(elem_classes="center-content"):
            gr.HTML("""
                <div style='
                    text-align: center;
                    margin: 20px 0 10px 0;
                    padding: 28px 40px;
                    background: #3b69b5;
                    border-radius: 16px;
                    border: 1px solid #355ba0;
                    box-shadow: 0 4px 24px rgba(59,105,181,0.3);
                '>
                    <h1 style='font-size: 2.8rem; margin: 0 0 8px 0; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;'>\U0001f680 Test Automation Framework</h1>
                    <p style='font-size: 1.1rem; color: #ffffff; margin: 0;'>Execute test cases across different platforms and interfaces.</p>
                </div>
            """)

        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("<h3 style='color: #1E293B; font-size: 1.2rem; font-weight: bold; margin-bottom: 10px;'>⚙️ Setup & Configuration</h3>")
                config_input = gr.File(
                    label="Upload testbed.json",
                    file_count="single",
                    type="filepath",
                    elem_classes="blue-upload"
                )
                
                test_selector = gr.Dropdown(
                    label="🎯 Select Tests",
                    choices=[],
                    multiselect=True,
                    interactive=True,
                    info="Leave empty to run all discovered tests.",
                    elem_classes="blue-dropdown"
                )
                
                with gr.Row():
                    refresh_btn = gr.Button("🔄 Refresh Tests", variant="secondary", elem_classes="blue-btn")
                    run_btn = gr.Button("▶️ Run Tests", variant="primary", elem_classes="run-btn")
            
            with gr.Column(scale=2):
                # Styled & Centered Execution Report Header
                gr.HTML("""
                    <div style='
                        background: #3b69b5;
                        border-radius: 10px;
                        padding: 14px 20px;
                        margin-bottom: 16px;
                        display: flex;
                        align-items: center;
                        gap: 10px;
                        box-shadow: 0 2px 12px rgba(59,105,181,0.4);
                    '>
                        <span style='font-size: 1.4rem;'>\U0001f4dc</span>
                        <h2 style='margin: 0; color: #ffffff; font-size: 1.4rem; font-weight: 700; letter-spacing: 0.5px;'>Execution Report</h2>
                    </div>
                """)
                output_display = gr.HTML("<div style='text-align: center; color: #1E293B; padding: 40px; border: 2px dashed #e5e7eb; border-radius: 12px;'>No output yet. Please upload config and hit Run.</div>")
                
                with gr.Accordion("📂 Test Discovery Insights", open=True):
                    info_display = gr.Markdown("Press **Refresh** to discover available test cases.")

        # Event logic
        def on_refresh():
            choices, info = refresh_test_choices()
            cpu_tests = sorted([c for c in choices if ".cpu." in c])
            other_tests = sorted([c for c in choices if ".cpu." not in c])
            return gr.update(choices=cpu_tests + other_tests), info

        def on_run(config_path, selected_ids):
            if not config_path:
                return "<div style='color: #ff4b4b; text-align: center; font-weight: bold; padding: 20px;'>## ❌ Error: Please upload a testbed.json file first.</div>"
            
            class ConfigWrapper:
                def __init__(self, path):
                    self.name = path[0] if isinstance(path, list) and path else path
            
            try:
                # Wrap existing report logic to return as HTML
                report = execute_tests(ConfigWrapper(config_path), selected_ids)
                return f"<div style='padding: 10px;'>{report}</div>"
            except Exception as e:
                return f"<div style='color: #ff4b4b;'>## ❌ Execution Error<br><pre>{traceback.format_exc()}</pre></div>"

        refresh_btn.click(fn=on_refresh, inputs=[], outputs=[test_selector, info_display])
        run_btn.click(fn=on_run, inputs=[config_input, test_selector], outputs=[output_display])
        
        # Initial Load
        demo.load(fn=on_refresh, inputs=[], outputs=[test_selector, info_display])

    return demo


if __name__ == "__main__":
    port = find_free_port()
    print(f"Launching UI on port {port}...")
    ui_app = create_ui()
    ui_app.launch(server_name="127.0.0.1", server_port=port, share=False, inbrowser=True)