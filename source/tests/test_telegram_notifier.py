import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import btc_robot.telegram_notifier as telegram_module
from btc_robot.telegram_notifier import TelegramNotifier


class TelegramNotifierTests(unittest.TestCase):

    def test_disabled_returns_false(self):
        notifier = TelegramNotifier(
            token="x",
            chat_id="y",
            enabled=False,
        )

        self.assertFalse(notifier.send_message("test"))

    def test_signal_formats_message(self):
        notifier = TelegramNotifier(
            token="x",
            chat_id="y",
            enabled=True,
        )

        with tempfile.TemporaryDirectory() as tmp:
            isolated_file = (
                Path(tmp) / "btc_robot" / "telegram_notifier.py"
            )

            # send_signal menghitung state dari:
            # Path(__file__).resolve().parent.parent / state
            #
            # Arahkan __file__ ke direktori temporary supaya
            # state dedupe produksi tidak dibaca/ditulis.
            with patch.object(
                telegram_module,
                "__file__",
                str(isolated_file),
            ):
                with patch.object(
                    notifier,
                    "send_message",
                    return_value=True,
                ) as send:
                    result = notifier.send_signal(
                        "LONG",
                        123.45,
                        "reason",
                    )

            self.assertTrue(result)
            self.assertIn("LONG", send.call_args.args[0])
            self.assertIn("123.45", send.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
