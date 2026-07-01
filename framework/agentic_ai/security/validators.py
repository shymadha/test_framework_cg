"""
Security Validators for the Agentic AI Test Framework.

Covers:
  - Prompt injection detection
  - User input sanitization
  - State integrity validation
  - RCA output poisoning detection
  - Tool call abuse limiting
"""

import re
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALLOWED_INTENTS = {"execute", "rca", "report"}
ALLOWED_REQUEST_TYPES = {"execution", "rca", "report"}
ALLOWED_STEPS = {"execute_test", "run_rca_if_failed", "generate_report"}
ALLOWED_EXECUTION_METHODS = {"ssh", "local", None, ""}
ALLOWED_STATUS_VALUES = {
    "INIT", "CLASSIFYING", "PLANNED", "EXECUTING",
    "ARTIFACT_READY", "ANALYZING", "REPORTING", "COMPLETED", "FAILED",
}
ALLOWED_EXECUTION_STATUSES = {"PASSED", "FAILED"}

MAX_USER_REQUEST_LEN = 2000
MAX_LOG_TEXT_LEN = 500_000     # 500 KB
MAX_TOOL_CALLS_PER_MINUTE = 10

# Patterns that signal a prompt injection attempt inside user-supplied text
_INJECTION_PATTERNS: List[re.Pattern] = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?", re.I),
    re.compile(r"disregard\s+(all\s+)?(previous|prior|above)\s+instructions?", re.I),
    re.compile(r"forget\s+(all\s+)?(previous|prior|above)", re.I),
    re.compile(r"you\s+are\s+now\s+a", re.I),
    re.compile(r"act\s+as\s+(if\s+you\s+are|a\s+new)", re.I),
    re.compile(r"new\s+instructions?\s*:", re.I),
    re.compile(r"system\s*:\s*you", re.I),
    re.compile(r"<\s*/?system\s*>", re.I),
    re.compile(r"\[\s*system\s*\]", re.I),
    re.compile(r"jailbreak", re.I),
    re.compile(r"override\s+(your\s+)?(safety|rules|guidelines)", re.I),
    re.compile(r"do\s+not\s+follow\s+(your\s+)?rules", re.I),
    re.compile(r"execute\s+(os|system|shell|bash|python)\s*(command|code|script)", re.I),
    re.compile(r"import\s+os\s*;\s*os\.", re.I),
    re.compile(r"__import__", re.I),
    re.compile(r"subprocess\.(run|call|Popen)", re.I),
    re.compile(r"eval\s*\(", re.I),
    re.compile(r"exec\s*\(", re.I),
]

# Patterns that signal a poisoned RCA output
_RCA_POISON_PATTERNS: List[re.Pattern] = [
    re.compile(r"ignore\s+(all\s+)?previous", re.I),
    re.compile(r"system\s*:\s*you", re.I),
    re.compile(r"<\s*/?system\s*>", re.I),
    re.compile(r"new\s+instructions?\s*:", re.I),
    re.compile(r"jailbreak", re.I),
    re.compile(r"__import__", re.I),
    re.compile(r"subprocess\.", re.I),
    re.compile(r"eval\s*\(", re.I),
    re.compile(r"exec\s*\(", re.I),
]

# Characters/sequences stripped from user input before LLM use
_STRIP_SEQUENCES = [
    "\x00",          # null bytes
    "\r",            # carriage returns (normalise to \n)
    "\\u0000",       # unicode null
]


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class SecurityError(Exception):
    """Raised when a security check fails."""


class PromptInjectionError(SecurityError):
    """Raised when prompt injection is detected."""


class StateIntegrityError(SecurityError):
    """Raised when the agent state contains invalid/tampered values."""


class RCAPoisoningError(SecurityError):
    """Raised when the RCA output appears to be poisoned."""


class ToolAbuseError(SecurityError):
    """Raised when a tool is being called beyond the allowed rate."""


# ---------------------------------------------------------------------------
# 1. Input sanitization
# ---------------------------------------------------------------------------

def sanitize_user_input(text: str) -> str:
    """
    Strip dangerous characters and truncate oversized input.

    Args:
        text: Raw user-supplied string.

    Returns:
        Sanitized string safe to pass to the LLM.

    Raises:
        ValueError: If input is not a string.
        PromptInjectionError: If an injection pattern is detected.
    """
    if not isinstance(text, str):
        raise ValueError(f"Expected str, got {type(text).__name__}")

    for seq in _STRIP_SEQUENCES:
        text = text.replace(seq, "")

    text = text.strip()

    if len(text) > MAX_USER_REQUEST_LEN:
        text = text[:MAX_USER_REQUEST_LEN]

    _check_injection(text, context="user_input")

    return text


def sanitize_log_text(text: str) -> str:
    """
    Truncate and lightly clean log text before passing to the RCA agent.

    Args:
        text: Raw log file content.

    Returns:
        Sanitized log text.
    """
    if not isinstance(text, str):
        raise ValueError(f"Expected str, got {type(text).__name__}")

    text = text.replace("\x00", "").strip()

    if len(text) > MAX_LOG_TEXT_LEN:
        text = text[:MAX_LOG_TEXT_LEN]

    return text


# ---------------------------------------------------------------------------
# 2. Prompt injection detection
# ---------------------------------------------------------------------------

def _check_injection(text: str, context: str = "unknown") -> None:
    """
    Scan ``text`` for known prompt injection patterns.

    Args:
        text:    Text to scan.
        context: Label used in the error message.

    Raises:
        PromptInjectionError: If any pattern matches.
    """
    for pattern in _INJECTION_PATTERNS:
        match = pattern.search(text)
        if match:
            raise PromptInjectionError(
                f"Prompt injection detected in {context!r}: "
                f"matched pattern {pattern.pattern!r} at position {match.start()}"
            )


def check_prompt_injection(text: str, context: str = "unknown") -> None:
    """Public wrapper around ``_check_injection``."""
    _check_injection(text, context=context)


# ---------------------------------------------------------------------------
# 3. Orchestrator plan validation
# ---------------------------------------------------------------------------

def validate_orchestrator_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize the JSON plan emitted by the orchestrator LLM.

    Ensures:
      - intent is one of the allowed values
      - request_type is one of the allowed values
      - steps contains only whitelisted step names
      - execution_method is whitelisted
      - test_domain and test_name contain only safe characters
      - No injection in string fields

    Args:
        plan: Parsed dict from the LLM.

    Returns:
        Sanitized plan dict.

    Raises:
        StateIntegrityError: If any field is invalid.
        PromptInjectionError: If injection is detected in string fields.
    """
    if not isinstance(plan, dict):
        raise StateIntegrityError(f"Plan must be a dict, got {type(plan).__name__}")

    # intent
    intent = plan.get("intent")
    if intent not in ALLOWED_INTENTS:
        raise StateIntegrityError(
            f"Invalid intent {intent!r}. Allowed: {ALLOWED_INTENTS}"
        )

    # request_type
    request_type = plan.get("request_type")
    if request_type not in ALLOWED_REQUEST_TYPES:
        raise StateIntegrityError(
            f"Invalid request_type {request_type!r}. Allowed: {ALLOWED_REQUEST_TYPES}"
        )

    # steps
    raw_steps = plan.get("steps", [])
    if not isinstance(raw_steps, list):
        raise StateIntegrityError("'steps' must be a list")
    for step in raw_steps:
        if step not in ALLOWED_STEPS:
            raise StateIntegrityError(
                f"Invalid step {step!r}. Allowed: {ALLOWED_STEPS}"
            )

    # execution_method
    method = plan.get("execution_method")
    if method not in ALLOWED_EXECUTION_METHODS:
        raise StateIntegrityError(
            f"Invalid execution_method {method!r}. Allowed: {ALLOWED_EXECUTION_METHODS}"
        )

    # test_domain / test_name — only alphanumeric + underscore allowed
    _validate_identifier(plan.get("test_domain"), "test_domain")
    _validate_identifier(plan.get("test_name"), "test_name")

    # Scan all string values for injection
    for key, value in plan.items():
        if isinstance(value, str):
            _check_injection(value, context=f"plan.{key}")

    return plan


def _validate_identifier(value: Optional[str], field: str) -> None:
    """
    Ensure a field is None/empty or matches ``^[a-zA-Z0-9_]+$``.

    Raises:
        StateIntegrityError: If the value contains illegal characters.
    """
    if not value:
        return
    if not re.match(r"^[a-zA-Z0-9_]+$", value):
        raise StateIntegrityError(
            f"Field {field!r} contains illegal characters: {value!r}"
        )


# ---------------------------------------------------------------------------
# 4. State integrity validation
# ---------------------------------------------------------------------------

def validate_state(state: Dict[str, Any]) -> None:
    """
    Assert that the LangGraph state contains only valid, expected values.

    Checks:
      - status is a known literal
      - intent, if present, is a known literal
      - execution_status, if present, is PASSED or FAILED
      - execution_plan steps are whitelisted
      - test_domain / test_name identifiers are safe
      - artifact_path, if present, resolves inside the project's logs/ dir
        (prevents path traversal)
      - retry_count is a non-negative integer

    Args:
        state: OrchestratorState dict.

    Raises:
        StateIntegrityError: On any integrity violation.
    """
    # status
    status = state.get("status")
    if status not in ALLOWED_STATUS_VALUES:
        raise StateIntegrityError(f"Invalid status {status!r}")

    # intent
    intent = state.get("intent")
    if intent is not None and intent not in ALLOWED_INTENTS:
        raise StateIntegrityError(f"Invalid intent {intent!r}")

    # execution_status
    exec_status = state.get("execution_status")
    if exec_status is not None and exec_status not in ALLOWED_EXECUTION_STATUSES:
        raise StateIntegrityError(f"Invalid execution_status {exec_status!r}")

    # execution_plan
    plan = state.get("execution_plan")
    if plan is not None:
        if not isinstance(plan, list):
            raise StateIntegrityError("execution_plan must be a list")
        for step in plan:
            if step not in ALLOWED_STEPS:
                raise StateIntegrityError(f"Invalid step in execution_plan: {step!r}")

    # identifiers
    _validate_identifier(state.get("test_domain"), "test_domain")
    _validate_identifier(state.get("test_name"), "test_name")

    # artifact_path — must stay inside logs/
    artifact_path = state.get("artifact_path")
    if artifact_path:
        _assert_safe_path(artifact_path, allowed_root="logs")

    # retry_count
    retry_count = state.get("retry_count", 0)
    if not isinstance(retry_count, int) or retry_count < 0:
        raise StateIntegrityError(
            f"retry_count must be a non-negative int, got {retry_count!r}"
        )


def _assert_safe_path(path_str: str, allowed_root: str) -> None:
    """
    Resolve ``path_str`` and verify it sits under ``allowed_root``.

    Raises:
        StateIntegrityError: On path traversal attempt.
    """
    try:
        resolved = Path(path_str).resolve()
        allowed = Path(allowed_root).resolve()
        resolved.relative_to(allowed)
    except ValueError:
        raise StateIntegrityError(
            f"Path traversal detected: {path_str!r} escapes allowed root {allowed_root!r}"
        )
    except Exception as exc:
        raise StateIntegrityError(f"Invalid artifact_path {path_str!r}: {exc}")


# ---------------------------------------------------------------------------
# 5. RCA output validation
# ---------------------------------------------------------------------------

_REQUIRED_RCA_KEYS = {"root_cause", "evidence", "confidence", "summary", "recommended_fix"}


def validate_rca_output(output: Any) -> Dict[str, Any]:
    """
    Validate the dict returned by the analysis (RCA) agent.

    Checks:
      - Output is a dict
      - All required keys are present
      - confidence is a float in [0.0, 1.0]
      - evidence is a list of strings
      - No injection patterns embedded in string fields

    Args:
        output: Object returned by the RCA chain.

    Returns:
        Validated output dict.

    Raises:
        RCAPoisoningError: If the output looks poisoned or malformed.
    """
    if not isinstance(output, dict):
        raise RCAPoisoningError(
            f"RCA output must be a dict, got {type(output).__name__}"
        )

    missing = _REQUIRED_RCA_KEYS - output.keys()
    if missing:
        raise RCAPoisoningError(f"RCA output missing required keys: {missing}")

    # confidence range
    confidence = output.get("confidence")
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        raise RCAPoisoningError(
            f"RCA confidence must be numeric, got {confidence!r}"
        )
    if not (0.0 <= confidence <= 1.0):
        raise RCAPoisoningError(
            f"RCA confidence out of range [0,1]: {confidence}"
        )

    # evidence is a list
    evidence = output.get("evidence")
    if not isinstance(evidence, list):
        raise RCAPoisoningError(
            f"RCA evidence must be a list, got {type(evidence).__name__}"
        )

    # Scan all string fields for injection
    for key, value in output.items():
        if isinstance(value, str):
            for pattern in _RCA_POISON_PATTERNS:
                match = pattern.search(value)
                if match:
                    raise RCAPoisoningError(
                        f"Poison pattern {pattern.pattern!r} detected in RCA field {key!r}"
                    )
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    for pattern in _RCA_POISON_PATTERNS:
                        if pattern.search(item):
                            raise RCAPoisoningError(
                                f"Poison pattern detected in RCA evidence list"
                            )

    return output


# ---------------------------------------------------------------------------
# 6. Tool abuse rate limiter
# ---------------------------------------------------------------------------

class ToolRateLimiter:
    """
    Simple in-process sliding-window rate limiter for tool calls.

    Tracks call timestamps per tool name and raises ``ToolAbuseError``
    if the rate exceeds ``max_calls`` within a 60-second window.

    Usage::

        limiter = ToolRateLimiter(max_calls=10)
        limiter.check("run_test_tool")   # raises ToolAbuseError if exceeded
    """

    def __init__(self, max_calls: int = MAX_TOOL_CALLS_PER_MINUTE):
        self._max_calls = max_calls
        self._history: Dict[str, List[float]] = defaultdict(list)

    def check(self, tool_name: str) -> None:
        """
        Record a call attempt and raise if the rate limit is exceeded.

        Args:
            tool_name: Name of the tool being called.

        Raises:
            ToolAbuseError: If more than max_calls have been made in 60 s.
        """
        now = time.monotonic()
        window = 60.0

        calls = self._history[tool_name]
        # Drop calls outside the window
        self._history[tool_name] = [t for t in calls if now - t < window]

        if len(self._history[tool_name]) >= self._max_calls:
            raise ToolAbuseError(
                f"Tool {tool_name!r} called {len(self._history[tool_name])} times "
                f"in the last {int(window)}s (limit: {self._max_calls}). "
                "Possible tool abuse detected."
            )

        self._history[tool_name].append(now)

    def reset(self, tool_name: Optional[str] = None) -> None:
        """
        Clear history for a specific tool or all tools.

        Args:
            tool_name: Tool to reset, or None to reset all.
        """
        if tool_name:
            self._history[tool_name] = []
        else:
            self._history.clear()


# Shared singleton — import and use directly in agent/tool modules
_default_limiter = ToolRateLimiter()


def check_tool_rate(tool_name: str) -> None:
    """Convenience wrapper using the shared singleton rate limiter."""
    _default_limiter.check(tool_name)