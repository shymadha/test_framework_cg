---
id: TASK-004
title: Emit Markdown Report and Enhance Diagnostics
status: draft
parent: REQ-1
layer: reporting
effort: S
tier: 3
created: 2026-08-18
updated: 2026-08-18
dependencies: [TASK-002, TASK-003]
---

## Description
Ensure the test writes a concise Markdown report under reports/ summarizing config, actions, metrics, thresholds, and the final verdict. Improve diagnostics on failure (adapter status, pairing state, playback status).

## Files to Create/Modify
- Modify framework/tests/bt/bt_audio_playback_validation_test.py: After post_test(), write a Markdown report file (timestamped) to reports/ using a minimal helper. Add richer failure logs.
- Optional: Extend framework/agentic_ai/agents/report_agent.py with a helper function write_simple_report(title, body) for reuse; otherwise implement minimal local writer.

## Acceptance Criteria
- On each run, a reports/<timestamp>-bt-audio.md file exists with PASS/FAIL, metric (if any), thresholds, and key timestamps.
- On failure, the report includes actionable diagnostics (connection state, playback check outputs, device info).
- Manual and Agentic UIs display the latest report without changes to their code.

## Test Plan
- Integration: Run test twice (PASS/FAIL) and verify two distinct report files with appropriate contents.
- Edge: Report directory missing is created automatically. File write failures are logged with warning, not causing test crash.

## Technical Notes
- Follow existing logging patterns. Use datetime.now().strftime for filenames. Keep report format Markdown.
