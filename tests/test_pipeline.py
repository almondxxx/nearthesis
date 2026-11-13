"""Run with:  python -m unittest discover -s tests -v"""
import json
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from pipeline import build as B

ROOT = Path(__file__).resolve().parent.parent


class RollingPercentile(unittest.TestCase):
    def test_rising_series_scores_100(self):
        s = pd.Series(np.arange(400, dtype=float))
        self.assertEqual(B.rolling_pct(s).iloc[-1], 100.0)

    def test_falling_series_scores_0(self):
        s = pd.Series(np.arange(400, 0, -1, dtype=float))
        self.assertEqual(B.rolling_pct(s).iloc[-1], 0.0)

    def test_needs_min_history(self):
        s = pd.Series(np.arange(100, dtype=float))
        self.assertTrue(B.rolling_pct(s).isna().all())

    def test_no_lookahead(self):
        s = pd.Series(np.random.default_rng(1).normal(size=500))
        full = B.rolling_pct(s)
        cut = B.rolling_pct(s.iloc[:300])
        pd.testing.assert_series_equal(full.iloc[:300], cut)


class Combine(unittest.TestCase):
    def test_equal_weights_are_means(self):
        sc = pd.DataFrame({"active_accounts": [10.0], "txns": [30.0], "tvl_usd": [80.0], "net_issuance_ann": [40.0]})
        out = B.combine(sc)
        self.assertAlmostEqual(out["network"].iloc[0], 20.0)
        self.assertAlmostEqual(out["defi"].iloc[0], 80.0)
        self.assertAlmostEqual(out["tokenomics"].iloc[0], 40.0)
        self.assertAlmostEqual(out["fundamentals"].iloc[0], (20 + 80 + 40) / 3)

    def test_missing_pillar_is_skipped(self):
        sc = pd.DataFrame({"active_accounts": [60.0], "tvl_usd": [np.nan]})
        out = B.combine(sc)
        self.assertAlmostEqual(out["fundamentals"].iloc[0], 60.0)


class OfflineBuild(unittest.TestCase):
    """Rebuild from the committed snapshot and check the published payload."""

    @classmethod
    def setUpClass(cls):
        cls.out = B.build()

    def test_payload_shape(self):
        d = json.loads((ROOT / "docs" / "data" / "dashboard.json").read_text())
        self.assertEqual(len(d["dates"]), B.DISPLAY_DAYS)
        for c in ("near", "avax"):
            for k in ("fundamentals", "valuation", "confidence_premium", "network", "defi", "tokenomics"):
                self.assertEqual(len(d["series"][c]["index"][k]), B.DISPLAY_DAYS)

    def test_premium_is_valuation_minus_fundamentals(self):
        for c in ("near", "avax"):
            L = self.out["latest"][c]
            self.assertAlmostEqual(L["confidence_premium"], L["valuation"] - L["fundamentals"], delta=0.11)

    def test_scores_in_range(self):
        for c in ("near", "avax"):
            for k, v in self.out["latest"][c].items():
                if v is not None and k != "confidence_premium":
                    self.assertTrue(0 <= v <= 100, (c, k, v))

    def test_report_written(self):
        self.assertIn("Confidence Premium", (ROOT / "reports" / "latest.md").read_text())


if __name__ == "__main__":
    unittest.main()
