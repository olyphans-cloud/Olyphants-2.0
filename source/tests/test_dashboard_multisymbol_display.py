import tempfile
import unittest

from btc_robot.dashboard import Dashboard, INDEX_HTML, TIMEFRAMES


class DashboardMultiSymbolDisplayTests(unittest.TestCase):
    def test_dashboard_accepts_multiple_configured_symbols(self):
        with tempfile.TemporaryDirectory() as work:
            dash = Dashboard(work, ".", ["BTCUSDT", "ETHUSDT", "SOLUSDT"])
            state = dash.state()
            self.assertEqual(state["coins"], ["BTCUSDT", "ETHUSDT", "SOLUSDT"])
            self.assertEqual(state["exchange"], "Tokocrypto")
            self.assertEqual(state["mode"], "PAPER")
            self.assertEqual(set(state["timeframes"]), {"H4"})

    def test_page_displays_symbol_count_and_latest_scan_results(self):
        self.assertIn('id="coin-count"', INDEX_HTML)
        self.assertIn('id="scan-results"', INDEX_HTML)
        self.assertIn("s.coins.length", INDEX_HTML)
        self.assertIn("s.scan&&s.scan[tf]", INDEX_HTML)
        self.assertIn("item.symbol", INDEX_HTML)
        self.assertIn("textContent", INDEX_HTML)
        self.assertNotIn("innerHTML", INDEX_HTML)


if __name__ == "__main__":
    unittest.main()
