---
id: LESSON-001
title: Retries and On-Test Reporting Reduce BT Flakes
created: 2026-09-01
updated: 2026-09-01
domain: Bluetooth
component: BT/audio
tags: [stability, reporting]
frequency: occasional
source_pr: TBD
---

## Summary
Bounded retries with backoff around pairing/connection and emitting a per-run Markdown report from the test stabilized results and improved operator traceability.

## Details
- Pair/connect operations can intermittently fail due to adapter/device state. Implementing short backoff retries with clear logging reduced flakes.
- Generating a concise report from the test itself ensured artifacts exist even when higher-level reporting is bypassed.

## Guidance
- Prefer tolerant assertions (keywords/regex) for adapter state checks.
- Keep report content minimal but consistent: config snapshot, actions, metrics (if any), thresholds, verdict.
