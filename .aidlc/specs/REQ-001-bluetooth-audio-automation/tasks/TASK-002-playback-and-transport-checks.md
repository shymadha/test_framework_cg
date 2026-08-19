id: TASK-002
title: Implement Playback Start and Transport Validation
status: draft
parent: REQ-001
layer: test
effort: M
tier: 2
created: 2026-08-18
updated: 2026-08-18
dependencies: [TASK-001]
---

## Description
Extend the test to pair/connect to the Bluetooth audio device using BTUtilsAPI, initiate DUT audio playback using a configured command, and validate transport is active via CLI/API on the DUT.

## Files to Create/Modify
- Modify framework/tests/bt/bt_audio_playback_validation_test.py: Implement pair/connect logic, playback invocation, and transport validation with bounded retries and backoff.

## Acceptance Criteria
- Test pairs and connects to the configured Bluetooth audio device (name/MAC from testbed.json) or logs a clear diagnostic if already paired.
- Playback command runs on the DUT and the test confirms active A2DP (or equivalent) transport status within a timeout.
- On failures, the test captures adapter state, pairing state, and recent logs for diagnostics.

## Test Plan
- Integration: With a real DUT and device, verify connection and transport detection.
- Edge: Device already paired; transient connection failure with retry; missing playback binary.
- Negative: Invalid device identifier should lead to FAIL with diagnostics, not crash.

## Technical Notes
- Use TestbedUtils to read keys: bt.device_name or bt.device_mac, playback.command, playback.sample_path, timeouts.thresholds.
- Use self.platform_obj.exec_cmd(...) as needed; keep parsing robust (regex/keywords).
