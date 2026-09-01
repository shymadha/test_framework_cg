from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any

from framework.core.testbed_utils import TestbedUtils


@dataclass
class MOSCoreClient:
    endpoint: str

    @classmethod
    def from_testbed(cls, tb: TestbedUtils) -> Optional["MOSCoreClient"]:
        ep = tb.get_value("moscore.endpoint") or tb.get_value("metrics.moscore.endpoint")
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
            # Simulate a MOS-like score in [1,5]
            return 4.2
        except Exception:
            return None
