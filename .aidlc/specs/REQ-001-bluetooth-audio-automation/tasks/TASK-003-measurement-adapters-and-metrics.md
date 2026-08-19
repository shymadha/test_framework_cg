---
id: TASK-003
title: Add Optional Measurement Adapters (APEX/MOSCORE) and Metric Thresholds
status: draft
parent: REQ-1
layer: utilities
effort: M
tier: 2
created: 2026-08-18
updated: 2026-08-18
dependencies: [TASK-001]
---

## Description
Introduce optional measurement clients for APEX Controller and MOSCORE that can be configured via testbed.json. The test detects availability and, if present, triggers a measurement to retrieve a numeric score used in PASS/FAIL evaluation with configurable thresholds.
## Files to Create/Modify
- Create framework/utilities/measurement/apex_client.py: APEXControllerClient with detect(config), measure(sample) → float|None.
- Create framework/utilities/measurement/moscore_client.py: MOSCoreClient with detect(config), measure(sample) → float|None.
- Modify framework/tests/bt/bt_audio_playback_validation_test.py: Wire optional measurement flow and threshold comparison.

## Acceptance Criteria
- When measurement config is absent, the test runs and evaluates transport-only without error.
- When measurement config is present and reachable, the test logs a numeric metric and compares to thresholds from config or defaults.
- Soft failures (timeout/unreachable) result in metric=None and a logged warning; test still returns a verdict using transport-only rules.

## Test Plan
- Unit: Instantiate clients with fake config and ensure detect() returns False; measure() returns None.
- Integration: With lab endpoints, capture a non-None metric and apply thresholds.
- Edge: Network errors, timeouts, or invalid responses do not crash the test.

## Technical Notes
- Keep adapters minimal and synchronous. No third-party SDKs unless already vendored; use requests/subprocess if needed.
- Threshold keys: metrics.moscore.min_pass, metrics.apex.min_pass; default to documented values if missing.
