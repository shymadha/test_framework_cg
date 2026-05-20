import os
import sys
from pathlib import Path
import gradio as gr

# -----------------------------------------
# Add project path
# -----------------------------------------
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break

# ✅ Import orchestrator
from agentic_ai.orchestrator_agent import orchestrator_graph

# -----------------------------------------
# LOG HELPERS
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
        with open(log_file, "r") as f:
            return f.read()
    except Exception as e:
        return f"Failed to read log file: {e}"


def clear_outputs():
    return "", "", "", ""



# -----------------------------------------
# REPORT HELPERS
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

        latest_file = sorted(files)[-1]
        return latest_file

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
# ORCHESTRATOR WRAPPER
# -----------------------------------------
# def run_orchestrator(user_request):
#     if not user_request or not user_request.strip():
#         return "ERROR", "Please enter a test request", None, None

#     try:
#         result = orchestrator_graph.invoke(
#             {
#                 "user_request": user_request,
#                 "retry_count": 0,
#                 "status": "INIT",
#             }
#         )

#         status = result.get("status", "UNKNOWN")
#         test_status = result.get("test_status", "")
#         execution_status = result.get("execution_status", "")
#         matched_test = result.get("matched_test", "")
#         log_dir = result.get("log_dir", None)
#         report_path = result.get("report_path", None)

#         message = ""

#         # ✅ Verdict
#         if execution_status == "PASSED":
#             message += "✅ Test Verdict: PASSED\n\n"
#         elif execution_status == "FAILED":
#             message += "❌ Test Verdict: FAILED\n\n"

#         # ✅ Test interpretation
#         if test_status == "VAGUE":
#             message += "⚠️ Your request is too vague.\nPlease specify the exact test."

#         elif test_status == "NOT_FOUND":
#             message += "❌ Requested test not found in framework."

#         elif test_status == "VALID":
#             message += f"🔧 Running test: {matched_test}"

#         return f"Status: {status}", message, log_dir, test_status, report_path

#     except Exception as e:
#         return "ERROR", str(e), None, None,None
def run_orchestrator(user_request):
    if not user_request or not user_request.strip():
        return "ERROR", "Please enter a test request", None, None, None  # ✅ 5 values

    try:
        result = orchestrator_graph.invoke(
            {
                "user_request": user_request,
                "retry_count": 0,
                "status": "INIT",
            }
        )
        status = result.get("status", "UNKNOWN")
        request_type = result.get("request_type", "execution")
        test_status = result.get("test_status", "")
        execution_status = result.get("execution_status", "")
        matched_test = result.get("matched_test", "")
        log_dir = result.get("log_dir", None)
        report_path = result.get("report_path", None)

        message = ""

        # ✅ REPORT FLOW
        if request_type == "report":
            message = "📄 Report generated successfully"
            return f"Status: {status}", message, log_dir, test_status, report_path

        
        # ✅ EXECUTION FLOW
        if execution_status == "PASSED":
            message += "✅ Test Verdict: PASSED\n\n"
        elif execution_status == "FAILED":
            message += "❌ Test Verdict: FAILED\n\n"
        
        

        if test_status == "VAGUE":
            message += "⚠️ Your request is too vague.\nPlease specify the exact test."

        elif test_status == "NOT_FOUND":
            message += "❌ Requested test not found in framework."

        elif test_status == "VALID":
            message += f"🔧 Running test: {matched_test}"

        # ✅ ALWAYS return 5 values
        return f"Status: {status}", message, log_dir, test_status, None

    except Exception as e:
        return "ERROR", str(e), None, None, None  # ✅ 5 values


# -----------------------------------------
# HANDLER
# -----------------------------------------
def handle_user_input(user_text):
    status, message, log_dir, test_status, report_path = run_orchestrator(user_text)

    # ✅ Logs handling
    if test_status in ["NOT_FOUND", "VAGUE"] or "ERROR" in status:
        logs = "⚠️ No execution logs generated for this request."
        report_md = "⚠️ No report generated."

    else:
        log_file = (
            os.path.join(log_dir, "framework.log")
            if log_dir
            else get_latest_log_file()
        )

        logs = read_log_file(log_file) if log_file else "No log file found"

        # ✅ Report handling
        if not report_path:
            report_path = get_latest_report_file()

        report_md = read_report_file(report_path) if report_path else "No report found"

    return status, message, logs, report_md


# -----------------------------------------
# UI DESIGN
# -----------------------------------------
with gr.Blocks(
    title="AI Enabled Scalable Test Environment",
    theme=gr.themes.Soft(),
    css="""
    textarea {
        font-family: monospace;
        background-color: #f8fafc !important;
        color: #16a34a !important; /* soft green logs */
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

    .subtext {
        text-align: center;
        color: #475569;
        margin-bottom: 20px;
    }
    """
) as demo:

    # ✅ HEADER
    gr.Markdown("<div class='header'>🤖 AI Enabled Scalable Test Environment Framework</div>")
    #gr.Markdown("<div class='subtext'>Run hardware validation tests using natural language</div>")

    # ✅ Examples
#     gr.Markdown("""
# ### 💡 Example Commands  
# ✅ `run cpu frequency test`  
# ⚠️ `run cpu test`  
# ❌ `run gpu test`
# """)

    # ✅ Test list
    with gr.Accordion("📋 Available Test Domains", open=False):
        gr.Markdown("""
### 🖥️ CPU
• run cpu core count test  
• run cpu monitor usage test  
• run cpu frequency test  
• run cpu stress test  

### 🌐 Ethernet  
• run ethernet device detection test  
• run ethernet connectivity test  
• run ethernet link status test  

### ⚡ PM  
• run s3  
• run restart  
• run s5  

### 🔌 I2C  
• run i2c register read test  
• run i2c device detection test  
• run i2c register write test  
• run i2c burst read test  

### 📶 Bluetooth  
• run bt data transfer test  
• run bt device scan test  
• run bt pair connect test  
• run bt adapter detection test  
• run bt enable poweron test  

### 🔄 SPI  
• run spi loopback test  
• run spi data integrity test  
• run spi speed mode test  
• run spi device detection test  

### 🔘 GPIO  
• run gpio output toggle test  
• run gpio led blink test  
• run gpio interrupt detect test  
• run gpio input read test  
""")


    # ✅ Input row
    with gr.Row():
        user_input = gr.Textbox(
            placeholder="e.g. run cpu frequency test on beagle using ssh",
            show_label=False,
            scale=4
        )
        run_btn = gr.Button("🚀 Run Test", variant="primary", scale=1)

    # ✅ Status + Result
    with gr.Row():
        status_output = gr.Textbox(label="Test Status", interactive=False)
        result_output = gr.Textbox(label="Test Result", interactive=False)

    # ✅ Logs
    gr.Markdown("### 🧾 Execution Logs")
    log_output = gr.TextArea(lines=20, show_label=False)
    
    # ✅ Report Section
    gr.Markdown("### 📄 Test Report")
    report_output = gr.Markdown()

    # -----------------------------------------
    # EVENTS
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
# RUN
# -----------------------------------------
if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False,inbrowser=True)