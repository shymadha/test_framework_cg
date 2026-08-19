id: REQ-001
title: Bluetooth Audio Automation Test
status: complete
priority: high
effort: L
deployable: false
created: 2026-08-18
updated: 2026-08-18
---

## Description
Automate the existing manual Bluetooth audio validation to reduce manual effort and make results repeatable and measurable within the Aster FW framework. The flow covers pairing the DUT with a Bluetooth audio device, initiating audio playback, optionally interfacing with APEX Controller and/or MOSCORE if automation hooks are available, collecting objective audio quality metrics, and deriving an automatic PASS/FAIL based on thresholds. The test integrates with the framework’s TestEngine, logs under `logs/<timestamp>/`, and emits a markdown report under `reports/` for operator review.

## Acceptance Criteria
- [ ] The test connects the DUT to a configured Bluetooth audio device using credentials from `userinput/testbed.json`.
- [ ] The test successfully initiates audio playback from the DUT and confirms audio transport is active (e.g., A2DP stream status via CLI or API on DUT).
- [ ] If APEX/MOSCORE automation is available, the test triggers a measurement and retrieves a numeric score or metric.
- [ ] Measurement results and key events are captured in `logs/<timestamp>/framework.log` and summarized in the test run report.
- [ ] PASS/FAIL is determined automatically using configurable thresholds; defaults are documented in the spec and test docstring.
- [ ] On failure, the test records actionable diagnostics (connection state, playback state, device info).
- [ ] The test is selectable and runnable via the Manual UI and callable via the Agentic UI.

## External Dependencies
- Bluetooth stack and tools on the DUT (e.g., `bluetoothctl`, BlueZ or equivalent APIs).
- A Bluetooth audio device in the testbed with stable power and discoverable/pairable state.
- Optional: APEX Controller and/or MOSCORE with automation interfaces (CLI, REST, or SDK) reachable from the test host.

## Assumptions
- Real hardware execution is required; no simulator is in scope.
- The testbed definition (`userinput/testbed.json`) includes DUT SSH details and Bluetooth device identifiers (name/MAC) and any measurement endpoints for APEX/MOSCORE if used.
- The DUT can play a known audio sample non-interactively (local file or stream) and expose playback/transport status via CLI/API.
- Network access to measurement controllers exists when measurement automation is enabled.

## Risks
- Bluetooth pairing/connection flakiness: Likelihood medium, Impact medium. Mitigation: bounded retries with backoff; thorough logging of adapter state and pairing status.
- Measurement API instability or unavailability: Likelihood medium, Impact high. Mitigation: make measurement optional; mark as skipped-with-note when unavailable.
- Environmental noise or device variability affecting scores: Likelihood medium, Impact medium. Mitigation: require stable test setup; use relative thresholds or calibration runs.

## Questions
- What concrete automation interfaces exist for APEX Controller and MOSCORE in this lab (CLI endpoints, IPs, credentials)?
- Which audio sample(s) and playback method are approved for automation on the DUT (file path, player command)?
- What PASS/FAIL thresholds should be applied to the chosen quality metric(s)?
- Are reconnection attempts permitted, and what is the maximum total elapsed time for connection and measurement?

## Out of Scope
- Subjective listening tests and human-in-the-loop scoring.
- Multi-device Bluetooth topologies or handoff/roaming scenarios.
- Cloud result publishing or Jira auto-ticketing.

## Success Metrics
- Automated runs complete without manual steps in >= 95% of attempts on supported hardware.
- Reported metrics are captured for 100% of runs when measurement interfaces are available.
- Flake rate (retries needed) remains under an agreed target over 30 consecutive runs.
