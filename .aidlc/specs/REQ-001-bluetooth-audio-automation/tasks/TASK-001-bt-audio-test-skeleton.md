id: TASK-001
title: Create Bluetooth Audio Test Skeleton (BaseTest)
status: complete
parent: REQ-001
layer: test
effort: S
tier: 1
created: 2026-08-18
updated: 2026-08-18
dependencies: []
---

## Description
Add a new test under framework/tests/bt/ that follows the BaseTest/TestEngine pattern. The skeleton wires ParseUserInput, platform_obj, BTUtilsAPI, and structured logging, with placeholders for playback and optional measurement.

## Files to Create/Modify
- Create framework/tests/bt/bt_audio_playback_validation_test.py: Define class BtAudioPlaybackValidationTest(BaseTest) with pre_test()/do_test() and docstring documenting thresholds and config keys.
- Modify framework/tests/__init__.py: Ensure bt package is included if needed (should already exist).

## Acceptance Criteria
- The new test is discovered by Manual UI and listed with class name BtAudioPlaybackValidationTest.
- Running via Agentic UI using domain "bt" and test_name "bt_audio_playback_validation_test" executes and logs to logs/<timestamp>/framework.log.
- The test reads DUT and BT device identifiers from userinput/testbed.json when provided; falls back to sane defaults with a warning.

## Test Plan
- Unit: Import the class and verify class name ends with Test and inherits BaseTest.
- Integration: Run via Manual UI with a minimal testbed.json; verify lifecycle logs and a PASS/FAIL placeholder verdict.
- Edge: Missing config keys result in defaults and warnings; no crash.

## Technical Notes
- Follow existing bt_*_test.py structure. Ensure do_test() sets self.result.set_result(...) and returns an int.
