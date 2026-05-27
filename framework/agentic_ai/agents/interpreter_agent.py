from typing import Dict
from framework.agentic_ai.state.orchestrator_state import OrchestratorState
import re
from pathlib import Path

from pathlib import Path

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


def interpreter_agent(state: OrchestratorState) -> OrchestratorState:
    """
    CLASSIFYING state.
    Converts raw user input into a normalized intent and request_type.
    This node NEVER executes tests, analyzes logs, or generates reports.
    """

    user_input = state["user_request"].lower()

    # -----------------------------------------
    # Default classification
    # -----------------------------------------
    request_type = None
    intent = None

    # -----------------------------------------
    # REPORT intent detection
    # -----------------------------------------
    if re.search(r"\breport\b", user_input):
        request_type = "report"
        intent = "summarize"

        # Scope resolution (default behavior)
        if "last" in user_input:
            state["report_scope"] = "last_execution"
        elif re.search(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}", user_input):
            ts_match = re.search(
                r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}", user_input
            )
            state["report_scope"] = "explicit_timestamp"
            state["timestamp"] = ts_match.group(0)
        else:
            state["report_scope"] = "last_execution"

    # -----------------------------------------
    # RCA / ANALYSIS intent detection
    # -----------------------------------------
    elif "framework.log" in user_input or "analyze" in user_input or "fail" in user_input:
        request_type = "rca"
        intent = "analyze"
        state["artifact_type"] = "framework_log"

    # -----------------------------------------
    # EXECUTION intent detection (default)
    # -----------------------------------------
    else:
        request_type = "execution"
        intent = "execute"

        extract_metadata_from_framework(user_input, state)
        
        # Extract test metadata (lightweight parsing)
        # if "cpu" in user_input:
        #     state["test_domain"] = "cpu"
        #     state["test_name"] = "cpu_monitor"

        # if "beagle" in user_input:
        #     state["platform"] = "beagle"

        # if "ssh" in user_input:
        #     state["execution_method"] = "ssh"

    # -----------------------------------------
    # Update state for orchestrator routing
    # -----------------------------------------
    state["request_type"] = request_type
    state["intent"] = intent
    state["status"] = "CLASSIFYING"

    return state


