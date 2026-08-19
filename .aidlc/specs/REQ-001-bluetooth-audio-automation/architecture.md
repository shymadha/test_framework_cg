---
id: REQ-1
title: Bluetooth Audio Automation — Architecture
status: approved
created: 2026-08-18
updated: 2026-08-18
---

## Overview
Design a framework-native automated test that validates Bluetooth audio playback on a DUT. The test pairs/connects to a configured Bluetooth audio device, initiates playback on the DUT, confirms transport/activity, and optionally triggers an external measurement (APEX/MOSCORE) to compute a quality metric. Results and diagnostics are logged to logs/<timestamp>/framework.log, and the test writes a concise Markdown report to reports/ for operator review. The design follows existing BaseTest → TestEngine patterns and reuses BTUtilsAPI for Bluetooth operations. External measurement is optional and must not block basic transport validation.

## System Context
- UI Layer: Manual UI (framework/ui/ui.py) discovers and runs tests; Agentic UI (framework/ui/ui_agentic_ai.py) orchestrates via executor_agent → test_engine_tool.
- Orchestration: TestEngine lifecycle (pre_test → do_test → post_test); logging and report surfacing via existing agents/UI.
- Core/Test Layer: New test under framework/tests/bt/, inheriting BaseTest.
- Device/IO: DUT access via SSHInterface through PlatformFactory; Bluetooth actions via BTUtilsAPI.
- Storage: Logs written under logs/<timestamp>/; a per-run Markdown report written under reports/.

## Data Model Changes
| Entity | Change | Notes |
|-------|--------|-------|
| None  | None   | No persistent storage or schema changes. |

## API Changes
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| None   | N/A  | No HTTP API changes. | N/A |

## Service Layer
- Reuse: BTUtilsAPI(os_type, platform_obj) for scan/pair/connect.
- New (optional): Lightweight measurement adapters to encapsulate external systems without coupling tests to vendor specifics:
  - framework/utilities/measurement/apex_client.py: APEXControllerClient with detect(config), measure(sample_config) → float|None.
  - framework/utilities/measurement/moscore_client.py: MOSCoreClient with detect(config), measure(sample_config) → float|None.
These clients should be no-ops when not configured; they must fail soft and return None.

## Key Decisions
1. Context: External measurement availability is environment-specific. Decision: Make measurement optional behind config flags and auto-detection. Rationale: Preserves basic transport validation in labs without measurement rigs. Consequences: PASS/FAIL logic must handle both metric-present and metric-absent paths.
2. Context: Report generation for Manual UI runs is not guaranteed by agents. Decision: The test itself will emit a concise Markdown report to reports/ summarizing config, actions, metrics, thresholds, and verdict. Rationale: Ensures operator review artifacts exist regardless of UI. Consequences: Minimal duplication with agentic report; acceptable for traceability.
3. Context: Bluetooth utilities expose simulated behaviors on some OS backends. Decision: Implement tolerant assertions (keywords/regex) and bounded retries with backoff; log raw adapter states. Rationale: Reduces flakes and supports mixed environments. Consequences: Tests must clearly log any fallbacks used.
4. Context: Thresholds vary by lab and device. Decision: Read thresholds and device identifiers from userinput/testbed.json with sane defaults documented in the test docstring and this spec. Rationale: Keeps test portable. Consequences: Missing keys result in defaults; log a warning.

## Open Questions
- APEX/MOSCORE interfaces in this lab (CLI/REST endpoints, credentials)? Owner: QA Lead. Due: 2026-08-25.
- Approved audio sample path and playback command on DUT? Owner: Platform Owner. Due: 2026-08-22.
- PASS/FAIL thresholds for metric(s)? Owner: Audio SME. Due: 2026-08-22.
- Max allowed total time for pairing/connection and measurement? Owner: Test Eng. Due: 2026-08-22.

## Proposed Additions to Global Architecture
- Add a short convention to .aidlc/context/architecture.md documenting the pattern “Optional external adapters must be soft-fail and return None; tests decide verdicts with or without metrics.” Rationale: Reusable across future integrations (power meters, analyzers).
