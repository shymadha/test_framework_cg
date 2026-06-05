from typing import Dict
import json
import re
from pathlib import Path

from framework.agentic_ai.state.orchestrator_state import OrchestratorState

# ✅ Import your helpers
from framework.agentic_ai.llm.gen_engine_llm import GenEngineLLM

# ✅ Initialize LLM
llm = GenEngineLLM().get_llm_model()


# =====================================================
# ✅ ALLOWED STEPS (STRICT CONTROL)
# =====================================================
ALLOWED_STEPS = {
    "execute_test",
    "run_rca_if_failed",
    "generate_report"
}


def sanitize_steps(steps):
    sanitized = []

    for step in steps:
        if step in ALLOWED_STEPS:
            sanitized.append(step)
        else:
            print(f"⚠️ Invalid step from LLM: {step}")

    # ✅ fallback safety
    if not sanitized:
        sanitized = ["execute_test"]

    return sanitized


# =====================================================
# ✅ FORMAT TEST CATALOG FOR LLM
# =====================================================
def format_test_catalog(test_map: dict) -> str:
    lines = []
    for domain, tests in test_map.items():
        tests_str = ", ".join(tests)
        lines.append(f"{domain}: [{tests_str}]")
    return "\n".join(lines)


# =====================================================
# ✅ BUILD SYSTEM PROMPT
# =====================================================
def build_system_prompt(test_catalog: str) -> str:
    return f"""
You are an AI orchestration planner.

AVAILABLE TESTS:
{test_catalog}

AVAILABLE STEPS (STRICT):
- execute_test
- run_rca_if_failed
- generate_report

CRITICAL RULES:
1. ONLY use steps from AVAILABLE STEPS
2. DO NOT generate natural language steps
3. DO NOT invent step names
4. ALWAYS return valid JSON

5. If user wants to run test → include execute_test
6. If failure/analysis mentioned → include run_rca_if_failed
7. If report requested → include generate_report

Output ONLY JSON:

{{
  "intent": "execute | analyze | summarize",
  "request_type": "execution | rca | report",
  "steps": [],
  "test_domain": "",
  "test_name": "",
  "platform": "",
  "execution_method": ""
}}
"""


# =====================================================
# ✅ SAFE JSON PARSER
# =====================================================
def safe_parse_json(content: str):
    try:
        return json.loads(content)
    except:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise


# =====================================================
# ✅ RULE-BASED FALLBACK
# =====================================================
def rule_based_interpreter(state: OrchestratorState):

    user_input = state["user_request"].lower()

    if "report" in user_input:
        return {
            "intent": "summarize",
            "request_type": "report",
            "execution_plan": ["generate_report"],
            "current_step_index": 0,
            "status": "CLASSIFYING"
        }

    elif "analyze" in user_input or "fail" in user_input:
        return {
            "intent": "analyze",
            "request_type": "rca",
            "execution_plan": ["run_rca_if_failed"],
            "current_step_index": 0,
            "status": "CLASSIFYING"
        }

    else:
        fallback_state = {}
        extract_metadata_from_framework(user_input, fallback_state)

        return {
            "intent": "execute",
            "request_type": "execution",
            "execution_plan": ["execute_test"],
            "current_step_index": 0,
            "test_domain": fallback_state.get("test_domain"),
            "test_name": fallback_state.get("test_name"),
            "status": "CLASSIFYING"
        }


# =====================================================
# ✅ MAIN INTERPRETER AGENT (NLO)
# =====================================================
def interpreter_agent(state: OrchestratorState) -> Dict:

    user_input = state["user_request"]

    try:
        # ✅ Discover tests dynamically
        test_map = discover_tests()
        test_catalog = format_test_catalog(test_map)

        # ✅ Build dynamic prompt
        system_prompt = build_system_prompt(test_catalog)

        # ✅ Call LLM
        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ])

        content = response.content

        print("\n🧠 LLM RAW OUTPUT:", content)

        plan = safe_parse_json(content)

    except Exception as e:
        print("⚠️ LLM failed, falling back:", str(e))
        return rule_based_interpreter(state)

    # =====================================================
    # ✅ STEP SANITIZATION
    # =====================================================
    raw_steps = plan.get("steps", [])
    steps = sanitize_steps(raw_steps)

    # ✅ ensure execute_test exists
    if plan.get("intent") == "execute" and "execute_test" not in steps:
        print("⚠️ Injecting missing execute_test")
        steps.insert(0, "execute_test")

    print("✅ FINAL SANITIZED STEPS:", steps)

    # =====================================================
    # ✅ EXTRACT TEST METADATA
    # =====================================================
    test_domain = plan.get("test_domain")
    test_name = plan.get("test_name")

    if not test_domain or not test_name:
        print("⚠️ LLM failed to map test → fallback matching")
        fallback_state = {}
        extract_metadata_from_framework(user_input.lower(), fallback_state)
        test_domain = fallback_state.get("test_domain")
        test_name = fallback_state.get("test_name")

    # =====================================================
    # ✅ VALIDATE EXECUTION METHOD
    # =====================================================
    method = plan.get("execution_method")
    if method not in ["ssh", "local", None, ""]:
        print("⚠️ Invalid execution_method:", method)
        method = None

    # =====================================================
    # ✅ RETURN STATE UPDATE (LANGGRAPH STYLE)
    # =====================================================
    final_state = {
        "intent": plan.get("intent"),
        "request_type": plan.get("request_type"),
        "execution_plan": steps,
        "current_step_index": 0,
        "test_domain": test_domain,
        "test_name": test_name,
        "platform": plan.get("platform"),
        "execution_method": method,
        "status": "CLASSIFYING"
    }

    print("✅ FINAL STATE RETURNED:", final_state)

    return final_state

from pathlib import Path

def format_test_catalog(test_map: dict) -> str:
    lines = []
    for domain, tests in test_map.items():
        tests_str = ", ".join(tests)
        lines.append(f"{domain}: [{tests_str}]")
    return "\n".join(lines)

def discover_tests(test_root=None):
    if test_root is None:
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / "framework" / "tests").exists():
                test_root = parent / "framework" / "tests"
                break
        else:
            raise RuntimeError("framework/tests directory not found")

    root = Path(test_root)
    test_map = {}

    for domain_dir in root.iterdir():
        if domain_dir.is_dir():
            domain = domain_dir.name
            tests = [
                f.stem
                for f in domain_dir.glob("*.py")
                if f.name != "__init__.py"
            ]
            if tests:
                test_map[domain] = tests

    return test_map


def normalize(text: str) -> set:
    text = re.sub(r"[^\w\s]", " ", text.lower())
    return set(text.split())

def match_test_from_request(user_request: str, test_map: dict):
    user_tokens = normalize(user_request)

    best_match = None
    best_score = 0

    for domain, tests in test_map.items():
        for test in tests:
            test_tokens = set(test.split("_"))
            overlap = test_tokens & user_tokens

            score = len(overlap)

            if score > best_score:
                best_score = score
                best_match = (domain, test)

    return best_match if best_match else (None, None)


def extract_platform_and_method(text, state):
    if "beagle" in text:
        state["platform"] = "beagle"
    if "ssh" in text:
        state["execution_method"] = "ssh"
    return state

def extract_metadata_from_framework(user_request: str, state: dict):
    test_map = discover_tests()
    domain, test_name = match_test_from_request(user_request, test_map)
    
    print("Discovered tests:", test_map)
    print("User request:", user_request)
    print("Domain:", domain)
    print("Test name:", test_name)

    if not domain or not test_name:
        raise ValueError("No matching test found in framework")

    state["test_domain"] = domain
    state["test_name"] = test_name

    state = extract_platform_and_method(user_request.lower(), state)

    return state


