from typing import TypedDict, Optional, Dict, Literal


class OrchestratorState(TypedDict):
    # =====================================================
    # External Input
    # =====================================================
    user_request: str
    """
    Raw user / CI / API request.
    Example:
      - "run cpu monitor test on beagle platform using ssh"
      - "analyze framework.log"
      - "generate report for last execution"
    """

    # =====================================================
    # Classification (CLASSIFYING state)
    # =====================================================
    request_type: Optional[
        Literal["execution", "rca", "report"]
    ]
    """
    Determined by the interpreter / intent router.
    Controls DAG entry path.
    """

    intent: Optional[
        Literal["execute", "analyze", "summarize"]
    ]
    """
    Normalized action intent.
    """

    # =====================================================
    # Execution metadata (EXECUTING state)
    # =====================================================
    test_domain: Optional[str]        # e.g. cpu
    test_name: Optional[str]          # e.g. cpu_monitor
    platform: Optional[str]           # e.g. beagle
    execution_method: Optional[str]   # e.g. ssh

    execution_status: Optional[
        Literal["PASSED", "FAILED"]
    ]
    """
    Set by executor_agent.
    Drives PASS / FAIL conditional branching.
    """

    execution_output: Optional[Dict]
    """
    Raw execution output: logs, metrics, exit codes, etc.
    """

    # =====================================================
    # Artifact resolution (ARTIFACT_READY state)
    # =====================================================
    artifact_type: Optional[str]      # e.g. framework_log
    artifact_path: Optional[str]      # Resolved filesystem path

    # =====================================================
    # Analysis / RCA (ANALYZING state)
    # =====================================================
    analysis_output: Optional[Dict]
    """
    RCA result:
      - root_cause
      - evidence
      - confidence
    """

    # =====================================================
    # Reporting (REPORTING state)
    # =====================================================
    report_scope: Optional[
        Literal["last_execution", "explicit_timestamp"]
    ]
    """
    Used for direct report requests.
    """

    timestamp: Optional[str]
    """
    Execution timestamp used for report scoping.
    Example: "2026-04-17_15-29-13"
    """

    report_path: Optional[str]
    """
    Final report artifact location.
    """

    # =====================================================
    # Lifecycle / Orchestration
    # =====================================================
    retry_count: int

    status: Literal[
        "INIT",
        "CLASSIFYING",
        "EXECUTING",
        "ARTIFACT_READY",
        "ANALYZING",
        "REPORTING",
        "COMPLETED",
        "FAILED",
    ]
