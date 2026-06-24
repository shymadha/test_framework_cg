"""Orchestrator State Module"""

from typing import Dict, List, Literal, Optional, TypedDict


class OrchestratorState(TypedDict):
    user_request: str
    request_type: Optional[Literal["execution", "rca", "report"]]
    intent: Optional[Literal["execute", "analyze", "summarize"]]
    execution_plan: Optional[List[str]]
    current_step_index: Optional[int]
    current_step: Optional[str]
    test_domain: Optional[str]
    test_name: Optional[str]
    platform: Optional[str]
    execution_method: Optional[str]
    execution_status: Optional[Literal["PASSED", "FAILED"]]
    execution_output: Optional[Dict]
    artifact_type: Optional[str]
    artifact_path: Optional[str]
    analysis_output: Optional[Dict]
    report_scope: Optional[Literal["last_execution", "explicit_timestamp"]]
    timestamp: Optional[str]
    report_path: Optional[str]
    retry_count: int
    status: Literal[
        "INIT",
        "CLASSIFYING",
        "PLANNED",
        "EXECUTING",
        "ARTIFACT_READY",
        "ANALYZING",
        "REPORTING",
        "COMPLETED",
        "FAILED",
    ]
    log_dir: Optional[str]
