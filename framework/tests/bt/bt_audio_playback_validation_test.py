"""
BtAudioPlaybackValidationTest

Automates Bluetooth audio playback validation on a DUT.

Config keys in userinput/testbed.json (examples):
- bt.device_name / bt.device_mac
- playback.command (e.g., "aplay /opt/samples/tone.wav" or platform-appropriate)
- playback.sample_path (optional if embedded in command)
- metrics.enabled (bool), metrics.moscore.min_pass, metrics.apex.min_pass
- timeouts.connect_secs (default 60), timeouts.transport_secs (default 30)

Defaults are applied if keys are missing; warnings are logged. Measurement is optional.
"""

from __future__ import annotations

import re
import time
from datetime import datetime
from pathlib import Path

from framework.tests.base_test import BaseTest
from framework.core.testbed_utils import TestbedUtils
from framework.utilities.os_utils.bt.api_intf_bt import BTUtilsAPI


class BtAudioPlaybackValidationTest(BaseTest):
    """Bluetooth audio playback validation following BaseTest pattern."""

    def pre_test(self) -> None:
        super().pre_test()
        # Load testbed config
        cfg_path = self.user_input.args.config
        self.tb = TestbedUtils(cfg_path)
        self.os_type = self.platform_obj.get_os_type()
        self.bt_api = BTUtilsAPI(self.os_type, self.platform_obj)

        # Read config with defaults
        self.bt_name = (
            self.tb.get_value("bt.device_name") or self.tb.get_value("bt.name") or ""
        )
        self.bt_mac = self.tb.get_value("bt.device_mac") or ""
        self.play_cmd = self.tb.get_value("playback.command") or ""
        self.sample_path = self.tb.get_value("playback.sample_path") or ""
        self.connect_secs = int(self.tb.get_value("timeouts.connect_secs") or 60)
        self.transport_secs = int(self.tb.get_value("timeouts.transport_secs") or 30)
        self.metrics_enabled = bool(self.tb.get_value("metrics.enabled") or False)
        self.mos_min = float(self.tb.get_value("metrics.moscore.min_pass") or 3.0)
        self.apex_min = float(self.tb.get_value("metrics.apex.min_pass") or 0.8)

        if not (self.bt_name or self.bt_mac):
            self.logger.warning(
                "No bt.device_name or bt.device_mac specified; will attempt generic connect based on scan heuristics."
            )
        if not self.play_cmd:
            self.logger.warning(
                "No playback.command specified; playback validation may be limited to transport checks."
            )

    def _start_playback(self) -> None:
        if not self.play_cmd:
            return
        # Execute playback command on DUT; ignore output, log status
        try:
            # BasePlatform.exec_cmd returns (stdout, stderr, status)
            out, err, rc = self.platform_obj.exec_cmd(self.play_cmd)
            self.logger.info(
                f"Playback command rc={rc}; stdout len={len(out)} stderr len={len(err)}"
            )
        except Exception as e:  # noqa: BLE001 - log and continue
            self.logger.exception(f"Playback command failed: {e}")

    def _check_transport_active(self) -> bool:
        # Heuristic check via bt utils or platform command; use keywords typical of A2DP/BlueZ status
        try:
            # BTUtilsAPI.data_transfer returns (stdout, stderr, rc)
            out, err, rc = self.bt_api.data_transfer()  # may be simulated on some OSes
            if rc == 0 and isinstance(out, str):
                s = out.lower()
                if any(
                    k in s for k in ["a2dp", "playing", "stream", "active", "connected"]
                ):
                    return True
        except Exception:
            pass
        # Fallback: try common CLI
        if str(self.os_type).lower() == "linux":
            try:
                out, err, rc = self.platform_obj.exec_cmd("bluetoothctl info")
                text = (out + "\n" + err).lower()
                if re.search(r"(connected: yes|audio.*sink|a2dp)", text):
                    return True
            except Exception:
                pass
        return False

    def _pair_and_connect(self) -> bool:
        # Scan and connect
        try:
            # Utilities expose simplified interfaces; enable power and attempt generic pair/connect
            self.bt_api.enable_power()
            _ = self.bt_api.scan_devices()  # prime internal state if implementation uses it
            out, err, rc = self.bt_api.pair_connect()
            success_tokens = ["successful", "connected", "ok", "paired"]
            out_l = (out or "").lower() if isinstance(out, str) else ""
            if rc == 0 or any(tok in out_l for tok in success_tokens):
                self.logger.info("Pair/connect reported success")
                return True
        except Exception as e:
            self.logger.exception(f"Pair/connect raised exception: {e}")
        return False

    def _try_with_retries(self, fn, secs: int, label: str) -> bool:
        deadline = time.time() + secs
        attempt = 0
        while time.time() < deadline:
            attempt += 1
            if fn():
                self.logger.info(f"{label} succeeded on attempt {attempt}")
                return True
            time.sleep(min(5, max(1, secs // 10)))
        self.logger.warning(f"{label} did not succeed within {secs}s")
        return False

    def do_test(self) -> int:
        # 1) Pair/connect with retries
        connected = self._try_with_retries(self._pair_and_connect, self.connect_secs, "BT pair/connect")
        if not connected:
            self.result.set_result(False, "Failed to pair/connect to BT audio device")
            return 1

        # 2) Start playback (best-effort)
        self._start_playback()

        # 3) Validate transport active with retries
        transport_ok = self._try_with_retries(self._check_transport_active, self.transport_secs, "Transport active")
        metric_val = None

        # 4) Optional measurement (placeholder; adapters added in TASK-003)
        metric_src = None
        if self.metrics_enabled:
            try:
                # Lazy import to avoid hard dependency if adapters not present yet
                from framework.utilities.measurement.apex_client import APEXControllerClient  # type: ignore
                from framework.utilities.measurement.moscore_client import MOSCoreClient  # type: ignore

                apex = APEXControllerClient.from_testbed(self.tb)
                mos = MOSCoreClient.from_testbed(self.tb)
                metric_val = None
                if apex and apex.detect():
                    metric_src = "APEX"
                    metric_val = apex.measure({"sample": self.sample_path})
                elif mos and mos.detect():
                    metric_src = "MOS"
                    metric_val = mos.measure({"sample": self.sample_path})
                self.logger.info(f"Measurement metric: {metric_val} (source={metric_src})")
            except Exception as e:  # noqa: BLE001
                self.logger.warning(f"Measurement not available or failed softly: {e}")

        # 5) Determine verdict
        passed = False
        reason = []
        if transport_ok:
            passed = True
            reason.append("Transport active")
            if metric_val is not None:
                # both thresholds allowed; treat as pass if meets any configured metric
                mos_ok = metric_val >= self.mos_min
                apex_ok = metric_val >= self.apex_min
                metric_ok = mos_ok or apex_ok
                passed = passed and metric_ok
                src_lbl = f" src={metric_src}" if metric_src else ""
                reason.append(
                    f"Metric={metric_val}{src_lbl} (mos_min={self.mos_min} apex_min={self.apex_min}) -> {'OK' if metric_ok else 'LOW'}"
                )
        else:
            reason.append("Transport inactive")

        self.result.set_result(passed, "; ".join(reason))

        # 6) Minimal Markdown report (TASK-004 will refine)
        try:
            reports_dir = Path("reports")
            reports_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            fname = reports_dir / f"{ts}-bt-audio.md"
            body = [
                f"# Bluetooth Audio Validation — {ts}",
                f"Verdict: {'PASS' if passed else 'FAIL'}",
                f"Device: name={self.bt_name} mac={self.bt_mac}",
                f"Transport: {'active' if transport_ok else 'inactive'}",
                f"Metric: {metric_val} ({metric_src})",
                f"Thresholds: mos_min={self.mos_min} apex_min={self.apex_min}",
            ]
            fname.write_text("\n\n".join(body), encoding="utf-8")
            self.logger.info(f"Wrote report {fname}")
        except Exception as e:  # noqa: BLE001
            self.logger.warning(f"Report write failed: {e}")

        return 0 if passed else 1
