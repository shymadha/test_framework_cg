from typing import TypedDict, Optional, Dict, Literal, List


class OrchestratorState(TypedDict):
    # =====================================================
    # ✅ External Input
    # =====================================================
    user_request: str


    # =====================================================
    # ✅ Classification (from interpreter_agent)
    # =====================================================
    request_type: Optional[
        Literal["execution", "rca", "report"]
    ]

    intent: Optional[
        Literal["execute", "analyze", "summarize"]
    ]


    # =====================================================
    # ✅ 🧠 Natural Language Orchestration (NEW)
    # =====================================================
    execution_plan: Optional[List[str]]
    """
    Dynamically generated steps from user request.

    Examples:
    ["execute_test"]

    ["execute_test", "run_rca_if_failed"]

    ["execute_test", "run_rca_if_failed", "generate_report"]
    """

    current_step_index: Optional[int]
    """
    Pointer to track progress in execution_plan.
    """

    current_step: Optional[str]
    """
    Current step being executed in orchestration loop.
    """


    # =====================================================
    # ✅ Execution metadata (EXECUTOR_AGENT)
    # =====================================================
    test_domain: Optional[str]
    test_name: Optional[str]

    platform: Optional[str]
    execution_method: Optional[str]

    execution_status: Optional[
        Literal["PASSED", "FAILED"]
    ]

    execution_output: Optional[Dict]


    # =====================================================
    # ✅ Artifact Resolution
    # =====================================================
    artifact_type: Optional[str]
    artifact_path: Optional[str]


    # =====================================================
    # ✅ RCA / Analysis Output
    # =====================================================
    analysis_output: Optional[Dict]
    """
    Example:
    {
        "root_cause": "CPU spike",
        "evidence": "...",
        "confidence": 0.92
    }
    """


    # =====================================================
    # ✅ Reporting Output
    # =====================================================
    report_scope: Optional[
        Literal["last_execution", "explicit_timestamp"]
    ]

    timestamp: Optional[str]

    report_path: Optional[str]


    # =====================================================
    # ✅ Control / Lifecycle
    # =====================================================
    retry_count: int

    status: Literal[
        "INIT",
        "CLASSIFYING",
        "PLANNED",        # ✅ NEW (after LLM planning)
        "EXECUTING",
        "ARTIFACT_READY",
        "ANALYZING",
        "REPORTING",
        "COMPLETED",
        "FAILED",
    ]
    
