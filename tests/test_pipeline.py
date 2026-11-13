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


class Valuation(unittest.TestCase):
    def _panel(self, n=900, rich=1.0):
        idx = pd.date_range("2023-01-01", periods=n, freq="D")
        base = pd.Series(np.exp(np.linspace(0, 1, n)), index=idx)
        df = pd.DataFrame({c: base * k for c, k in [("revenue_usd", 1e3), ("dex_volume_usd", 1e6), ("tvl_usd", 1e8),
                                                     ("stablecoins_usd", 1e8), ("returning_accounts", 1e4)]})
        df["market_cap_usd"] = base * 1e9
        df.iloc[-1, df.columns.get_loc("market_cap_usd")] *= rich
        return df

    def test_constant_multiples_give_fair_value_equal_to_market_cap(self):
        from pipeline.valuation import fair_value
        fv = fair_value(self._panel())
        last = fv.dropna(subset=["fair_value_mid"]).iloc[-1]
        self.assertAlmostEqual(last["fair_value_gap"], 0.0, delta=0.02)

    def test_rich_market_cap_is_above_band(self):
        from pipeline.valuation import fair_value
        fv = fair_value(self._panel(rich=3.0))
        last = fv.iloc[-1]
        self.assertGreater(last["market_cap_usd"], last["fair_value_high"])

    def test_fair_value_has_no_lookahead(self):
        from pipeline.valuation import fair_value
        df = self._panel()
        full = fair_value(df)["fair_value_mid"].iloc[:700]
        cut = fair_value(df.iloc[:700])["fair_value_mid"]
        pd.testing.assert_series_equal(full, cut)

    def test_verdict_majority(self):
        from pipeline.valuation import verdict_row
        row = pd.Series({"market_cap_usd": 10.0, "fair_value_low": 1.0, "fair_value_high": 5.0})
        self.assertEqual(verdict_row(row, 30.0, 50.0)["verdict"], "Overvalued")
        self.assertEqual(verdict_row(row, -30.0, 10.0)["verdict"], "Undervalued")
        self.assertEqual(verdict_row(row, -30.0, 50.0)["verdict"], "Mixed")  # over, under, fair
        row2 = pd.Series({"market_cap_usd": 3.0, "fair_value_low": 1.0, "fair_value_high": 5.0})
        self.assertEqual(verdict_row(row2, 0.0, 10.0)["verdict"], "Fairly valued")


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
        txt = (ROOT / "reports" / "latest.md").read_text()
        self.assertIn("## Verdict:", txt)
        self.assertIn("Confidence Premium", txt)

    def test_near_verdict_is_valid(self):
        self.assertIn(self.out["near"]["verdict"], {"Overvalued", "Undervalued", "Fairly valued", "Mixed"})


if __name__ == "__main__":
    unittest.main()
