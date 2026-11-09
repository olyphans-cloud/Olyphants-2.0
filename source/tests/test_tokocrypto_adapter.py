"""Contract tests for documented Tokocrypto market-data envelopes."""
import json
import unittest
from unittest.mock import patch

from btc_robot.data import DataError, fetch_tokocrypto_klines, fetch_tokocrypto_book_ticker


class _Response:
    def __init__(self, payload):
        self.payload = payload
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self):
        return json.dumps(self.payload).encode()


class TokocryptoAdapterTests(unittest.TestCase):
    def test_klines_unwrap_documented_envelope_and_keep_open_time(self):
        rows = [[1440000000000, "10", "12", "9", "11", "4",
                 1440000239999, "44", 3, "2", "22", "0"]]
        with patch("btc_robot.data.urllib.request.urlopen", return_value=_Response(
                {"code": 0, "msg": "success", "data": rows, "timestamp": 1440000240000})) as req:
            candles = fetch_tokocrypto_klines("BTC_USDT", "4h", 1, retries=1)
        self.assertEqual(len(candles), 1)
        self.assertEqual(candles[0].ts, 1440000000000)
        self.assertEqual(candles[0].volume, 4.0)
        self.assertIn("symbol=BTCUSDT", req.call_args.args[0])

    def test_klines_reject_api_error_code(self):
        with patch("btc_robot.data.urllib.request.urlopen", return_value=_Response(
                {"code": 1001, "msg": "symbol unavailable", "timestamp": 1})):
            with self.assertRaisesRegex(DataError, "code=1001"):
                fetch_tokocrypto_klines("BADUSDT", "4h", 1, retries=1)

    def test_book_unwrap_documented_envelope(self):
        payload = {"code": 0, "msg": "success", "data": {
            "lastUpdateId": 1, "bids": [["100", "2"]], "asks": [["101", "3"]]
        }, "timestamp": 123}
        with patch("btc_robot.data.urllib.request.urlopen", return_value=_Response(payload)):
            quote = fetch_tokocrypto_book_ticker("BTCUSDT")
        self.assertEqual((quote.bid, quote.ask), (100.0, 101.0))

    def test_book_rejects_crossed_market(self):
        payload = {"code": 0, "data": {"bids": [["102", "1"]], "asks": [["101", "1"]]}}
        with patch("btc_robot.data.urllib.request.urlopen", return_value=_Response(payload)):
            with self.assertRaises(DataError):
                fetch_tokocrypto_book_ticker("BTCUSDT")

    def test_limit_over_documented_maximum_rejected(self):
        with self.assertRaises(DataError):
            fetch_tokocrypto_klines("BTCUSDT", "4h", 1001)


if __name__ == "__main__":
    unittest.main()
