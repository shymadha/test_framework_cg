import os
import sys
from pathlib import Path
import gradio as gr

# -----------------------------------------
# ✅ Add project path
# -----------------------------------------
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break

# ✅ Import orchestrator
from framework.agentic_ai.graph.orchestrator_graph import orchestrator_graph


# -----------------------------------------
# ✅ LOG HELPERS
# -----------------------------------------
def get_latest_log_file(logs_base_dir="logs"):
    try:
        folders = [
            os.path.join(logs_base_dir, d)
            for d in os.listdir(logs_base_dir)
            if os.path.isdir(os.path.join(logs_base_dir, d))
        ]

        if not folders:
            return None

        latest_folder = sorted(folders)[-1]
        log_file = os.path.join(latest_folder, "framework.log")

        return log_file if os.path.exists(log_file) else None

    except Exception as e:
        print(f"Error finding log file: {e}")
        return None


def read_log_file(log_file):
    try:
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        return f"Failed to read log file: {e}"


def clear_outputs():
    return "", "", "", ""


# -----------------------------------------
# ✅ REPORT HELPERS
# -----------------------------------------
def get_latest_report_file(report_dir="reports"):
    try:
        files = [
            os.path.join(report_dir, f)
            for f in os.listdir(report_dir)
            if f.endswith(".md")
        ]

        if not files:
            return None

        return sorted(files)[-1]

    except Exception as e:
        print(f"Error finding report file: {e}")
        return None


def read_report_file(report_path):
    try:
        with open(report_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        return f"Failed to read report: {e}"


# -----------------------------------------
# ✅ ORCHESTRATOR WRAPPER (NLO-AWARE)
# -----------------------------------------
def run_orchestrator(user_request):
    if not user_request or not user_request.strip():
        return "ERROR", "Please enter a request", None, None

    try:
        result = orchestrator_graph.invoke(
            {
                "user_request": user_request,
                "retry_count": 0,
                "status": "INIT",
                "execution_done": False   # ✅ ensures fresh run
            }
        )

        status = result.get("status", "UNKNOWN")
        execution_status = result.get("execution_status")

        test_domain = result.get("test_domain")
        test_name = result.get("test_name")
        execution_plan = result.get("execution_plan", [])
        current_step = result.get("current_step")

        log_dir = result.get("log_dir", None)
        report_path = result.get("report_path", None)

        # -----------------------------------------
        # ✅ Build message (NLO)
        # -----------------------------------------
        message = ""

        if test_name:
            message += f"🔧 Test: {test_domain} / {test_name}\n\n"

        if execution_status == "PASSED":
            message += "✅ Test Verdict: PASSED\n\n"
        elif execution_status == "FAILED":
            message += "❌ Test Verdict: FAILED\n\n"

        if execution_plan:
            workflow = " → ".join(execution_plan)
            message += f"🧠 Execution Plan: {workflow}\n\n"

        if current_step:
            message += f"🚦 Current Step: {current_step}\n\n"

        return f"Status: {status}", message, log_dir, report_path

    except Exception as e:
        return "ERROR", str(e), None, None


# -----------------------------------------
# ✅ HANDLER
# -----------------------------------------
def handle_user_input(user_text):
    status, message, log_dir, report_path = run_orchestrator(user_text)

    if "ERROR" in status:
        logs = "⚠️ Execution failed."
        report_md = "⚠️ No report generated."

    else:
        log_file = (
            os.path.join(log_dir, "framework.log")
            if log_dir
            else get_latest_log_file()
        )

        logs = read_log_file(log_file) if log_file else "No log file found"

        if not report_path:
            report_path = get_latest_report_file()

        report_md = read_report_file(report_path) if report_path else "No report found"

    return status, message, logs, report_md


# -----------------------------------------
# ✅ UI DESIGN
# -----------------------------------------
with gr.Blocks(
    title="AI Enabled Scalable Test Environment",
    theme=gr.themes.Soft(),
    css="""
    textarea {
        font-family: monospace;
        background-color: #f8fafc !important;
        color: #16a34a !important;
    }

    input {
        background-color: #f8fafc !important;
        color: #111827 !important;
    }

    textarea, input {
        border-radius: 8px !important;
        border: 1px solid #d1d5db !important;
    }

    .header {
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        color: #2563eb;
    }
    """
) as demo:

    # ✅ HEADER
    gr.Markdown("<div class='header'>🤖 AI Enabled Scalable Test Environment</div>")

    # ✅ Input
    with gr.Row():
        user_input = gr.Textbox(
            placeholder="e.g. run cpu monitor test on beagle using ssh",
            show_label=False,
            scale=4
        )
        run_btn = gr.Button("🚀 Run", variant="primary", scale=1)

    # ✅ Outputs
    with gr.Row():
        status_output = gr.Textbox(label="Status", interactive=False)
        result_output = gr.Textbox(label="Result", interactive=False)

    gr.Markdown("### 🧾 Logs")
    log_output = gr.TextArea(lines=20, show_label=False)

    gr.Markdown("### 📄 Report")
    report_output = gr.Markdown()

    # -----------------------------------------
    # ✅ EVENTS
    # -----------------------------------------
    user_input.submit(
        fn=clear_outputs,
        outputs=[status_output, result_output, log_output, report_output],
    ).then(
        fn=handle_user_input,
        inputs=[user_input],
        outputs=[status_output, result_output, log_output, report_output],
    )

    run_btn.click(
        fn=clear_outputs,
        outputs=[status_output, result_output, log_output, report_output],
    ).then(
        fn=handle_user_input,
        inputs=[user_input],
        outputs=[status_output, result_output, log_output, report_output],
    )


# -----------------------------------------
# ✅ RUN
# -----------------------------------------
if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7861,
        share=False,
        inbrowser=True
    )
