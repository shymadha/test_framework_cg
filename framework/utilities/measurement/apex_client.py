from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any

from framework.core.testbed_utils import TestbedUtils


@dataclass
class APEXControllerClient:
    endpoint: str

    @classmethod
    def from_testbed(cls, tb: TestbedUtils) -> Optional["APEXControllerClient"]:
        ep = tb.get_value("apex.endpoint") or tb.get_value("metrics.apex.endpoint")
        if not ep:
            return None
        return cls(endpoint=str(ep))

    def detect(self) -> bool:
        # Placeholder soft-detect; extend to real ping/CLI invocation when available
        return bool(self.endpoint)

    def measure(self, sample: Any) -> Optional[float]:
        # Placeholder; integrate real measurement (HTTP/CLI) here. Return None on failure.
        try:
            _ = sample
            # Simulate a valid measurement in [0,1]
            return 0.9
        except Exception:
            return None
