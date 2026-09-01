---
id: ASSUME-001
title: External Measurement Is Optional For BT Audio Automation
status: resolved
created: 2026-09-01
updated: 2026-09-01
domain: Testing
component: BT/audio
source_pr: TBD
---

## Context
The Bluetooth audio automation can run in labs without APEX Controller or MOSCORE.

## Assumption
External measurement integrations (APEX, MOSCORE) may not be available. The test must still pass transport validation without metrics.

## Validation
Implemented measurement clients as soft-fail adapters returning `None` when unconfigured or unavailable. Tests compute a verdict using transport-only thresholds when metrics are absent.

## Outcome
Validated during development; tests operate correctly with and without measurement endpoints.
