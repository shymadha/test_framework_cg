import os
import sys
import importlib
import json
import io
import contextlib
import gradio as gr
from pathlib import Path
 
# -----------------------------------------
# ✅ SAFE sys.path injection
# -----------------------------------------
current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "framework").exists():
        if str(parent) not in sys.path:
            sys.path.append(str(parent))
        break
 
from framework.core.testbed_utils import TestbedUtils
 
 
# ✅ Get tests as before
def get_all_tests():
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    tests_dir = PROJECT_ROOT / "framework" / "tests"
    test_list = []
 
    for root, _, files in os.walk(tests_dir):
        for f in files:
            if f.endswith(".py") and not f.startswith("__") and f != "base_test.py":
                rel_path = os.path.relpath(root, tests_dir).replace(os.sep, ".")
                module_name = f"{rel_path}.{f[:-3]}" if rel_path != "." else f[:-3]
                test_list.append(module_name)
 
    return sorted(test_list)
 
 
# ✅ ✅ MAIN FIX — FULL LOG CAPTURE
def execute_test(config_file, test_name):
    """
    FULLY capture logs, stdout, stderr, result message.
    """
 
    if not config_file:
        return "ERROR: Upload testbed.json first."
 
    if not test_name:
        return "ERROR: Select a test to run."
 
    try:
        # Capture all stdout/stderr
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
 
            original_argv = sys.argv
            sys.argv = [sys.executable, "--config", config_file.name]
 
            module_path = f"framework.tests.{test_name}"
            test_module = importlib.import_module(module_path)
            importlib.reload(test_module)
 
            # find test class
            test_class = None
            for name, obj in vars(test_module).items():
                if isinstance(obj, type) and name.endswith("Test") and name != "BaseTest":
                    test_class = obj
                    break
 
            if not test_class:
                return f"Error: No test class found in {module_path}"
 
            # run test
            test_instance = test_class()
            test_instance.run()
 
            sys.argv = original_argv
 
        # ✅ Get captured logs
        logs = buf.getvalue().strip()
 
        # ✅ Result message
        result_msg = f"RESULT: {'PASS' if test_instance.result.passed else 'FAIL'}\n"
        result_msg += f"MESSAGE: {test_instance.result.message}\n\n"
 
        # ✅ Combine logs + result
        final_output = result_msg + "---------------- LOGS ----------------\n" + logs
 
        # ✅ Wrap for Gradio
        return f"```\n{final_output}\n```"
 
    except Exception as e:
        import traceback
        return f"Exception:\n{e}\n\n{traceback.format_exc()}"
 
 
def load_json_content(file_obj):
    if file_obj is None:
        return {}
    try:
        with open(file_obj.name, 'r') as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}
 
 
# ✅ BUILD UI
with gr.Blocks(title="Test Framework UI") as demo:
    gr.Markdown("# ✅ Test Automation UI")
    gr.Markdown("Upload config → Select test → View FULL logs including INFO lines.")
 
    with gr.Row():
        with gr.Column(scale=1):
            config_file = gr.File(label="1. Upload testbed.json", file_types=[".json"])
            json_display = gr.JSON(label="Parsed Config")
 
        with gr.Column(scale=1):
            test_dropdown = gr.Dropdown(
                choices=get_all_tests(),
                label="2. Select Test"
            )
            run_button = gr.Button("▶ Run Test", variant="primary")
 
    output = gr.TextArea(label="Execution Logs (FULL)", lines=35)
 
    config_file.change(load_json_content, inputs=config_file, outputs=json_display)
 
    run_button.click(
        execute_test,
        inputs=[config_file, test_dropdown],
        outputs=output
    )
 
if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)