import os
import tempfile
import unittest
from dataclasses import replace

from btc_robot.config import Mode, load_config, validate
from btc_robot.identity import check_identity, write_identity
from btc_robot.paper import paper_step
from btc_robot.recovery import diagnose


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def make_cfg(filename, state_dir):
    cfg = load_config(os.path.join(ROOT, filename))
    return validate(replace(
        cfg,
        mode=Mode.PAPER,
        state_dir=state_dir,
    ))


class D1H4IsolationTests(unittest.TestCase):

    def test_spot_and_futures_have_separate_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            spot = make_cfg(
                "config.spot_4h.example.json",
                os.path.join(tmp, "spot"),
            )
            futures = make_cfg(
                "config.futures_4h.example.json",
                os.path.join(tmp, "futures"),
            )

            self.assertNotEqual(spot.state_dir, futures.state_dir)
            self.assertEqual(check_identity(spot)[1], "fresh")
            self.assertEqual(check_identity(futures)[1], "fresh")

            write_identity(spot)
            write_identity(futures)

            self.assertEqual(check_identity(spot)[1], "ok")
            self.assertEqual(check_identity(futures)[1], "ok")

    def test_shared_state_dir_rejects_second_strategy(self):
        with tempfile.TemporaryDirectory() as tmp:
            shared = os.path.join(tmp, "shared")

            futures = make_cfg(
                "config.futures_4h.example.json",
                shared,
            )
            spot = make_cfg(
                "config.spot_4h.example.json",
                shared,
            )

            write_identity(futures)

            ok, status, _ = check_identity(spot)
            self.assertFalse(ok)
            self.assertEqual(status, "state_identity_mismatch")

            # Identitas Futures harus tetap utuh.
            self.assertEqual(check_identity(futures)[1], "ok")

    def test_paper_step_refuses_wrong_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            futures = make_cfg(
                "config.futures_4h.example.json",
                os.path.join(tmp, "futures"),
            )
            spot = make_cfg(
                "config.spot_4h.example.json",
                os.path.join(tmp, "spot"),
            )

            write_identity(futures)

            # Spot diarahkan ke state Futures.
            wrong = replace(spot, state_dir=futures.state_dir)
            result = paper_step(wrong)

            self.assertEqual(
                result.get("status"),
                "state_identity_mismatch",
            )

            # State Futures tetap teridentifikasi sebagai Futures.
            self.assertEqual(check_identity(futures)[1], "ok")

    def test_recovery_refuses_wrong_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            futures = make_cfg(
                "config.futures_4h.example.json",
                os.path.join(tmp, "futures"),
            )
            spot = make_cfg(
                "config.spot_4h.example.json",
                os.path.join(tmp, "spot"),
            )

            write_identity(futures)
            wrong = replace(spot, state_dir=futures.state_dir)

            result = diagnose(wrong)

            self.assertFalse(result.get("identity_ok"))
            self.assertEqual(
                result.get("identity_status"),
                "state_identity_mismatch",
            )
            self.assertFalse(result.get("recovery_allowed"))

    def test_legacy_state_without_identity_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            legacy_dir = os.path.join(tmp, "legacy")
            os.makedirs(legacy_dir)

            with open(
                os.path.join(legacy_dir, "paper_state.json"),
                "w",
                encoding="utf-8",
            ) as fh:
                fh.write("{}")

            spot = make_cfg(
                "config.spot_4h.example.json",
                legacy_dir,
            )

            ok, status, _ = check_identity(spot)
            self.assertFalse(ok)
            self.assertEqual(status, "state_identity_missing")


if __name__ == "__main__":
    unittest.main()
