"""Ingestion + validasi data (Dok 01 bagian 3 A/B, gerbang G1)."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from .models import BookQuote, Candle


class DataError(RuntimeError):
    pass


@dataclass
class DataQualityReport:
    ok: bool
    n: int
    issues: List[str] = field(default_factory=list)
    last_ts: Optional[int] = None
    age_seconds: Optional[float] = None

    def summary(self) -> str:
        return "OK" if self.ok else "; ".join(self.issues[:10])


def validate_candles(
    candles: Sequence[Candle],
    interval_ms: int,
    now_ms: Optional[int] = None,
    max_age_seconds: Optional[float] = None,
    allow_gaps: bool = False,
) -> DataQualityReport:
    issues: List[str] = []
    n = len(candles)
    if n == 0:
        return DataQualityReport(False, 0, ["data kosong"])
    prev: Optional[Candle] = None
    for i, c in enumerate(candles):
        vals = (c.open, c.high, c.low, c.close, c.volume)
        if any((not isinstance(v, (int, float))) or math.isnan(v) or math.isinf(v) for v in vals):
            issues.append(f"idx {i}: nilai non-finite")
            prev = c
            continue
        if min(c.open, c.high, c.low, c.close) <= 0 or c.volume < 0:
            issues.append(f"idx {i}: harga<=0 atau volume<0")
        if c.high < max(c.open, c.close) or c.low > min(c.open, c.close) or c.high < c.low:
            issues.append(f"idx {i}: OHLC tidak konsisten")
        if c.ts % interval_ms != 0:
            issues.append(f"idx {i}: ts tidak selaras interval")
        if prev is not None:
            if c.ts == prev.ts:
                issues.append(f"idx {i}: ts duplikat {c.ts}")
            elif c.ts < prev.ts:
                issues.append(f"idx {i}: ts mundur {c.ts} < {prev.ts}")
            elif c.ts - prev.ts != interval_ms and not allow_gaps:
                missing = (c.ts - prev.ts) // interval_ms - 1
                issues.append(f"idx {i}: celah {missing} candle sebelum ts {c.ts}")
        prev = c
    last = candles[-1]
    age = None
    if now_ms is not None:
        # umur dihitung dari waktu TUTUP candle terakhir
        age = (now_ms - (last.ts + interval_ms)) / 1000.0
        if age < -1:
            issues.append("candle terakhir belum tutup / ts di masa depan")
        if max_age_seconds is not None and age > max_age_seconds:
            issues.append(f"data basi: umur {age:.0f}s > {max_age_seconds}s")
    return DataQualityReport(not issues, n, issues, last.ts, age)


def data_fingerprint(candles: Sequence[Candle]) -> str:
    h = hashlib.sha256()
    for c in candles:
        h.update(f"{c.ts},{c.open!r},{c.high!r},{c.low!r},{c.close!r},{c.volume!r};".encode())
    return h.hexdigest()


def load_csv(path: str) -> List[Candle]:
    """CSV dengan kolom ts,open,high,low,close,volume (ts epoch ms UTC)."""
    out: List[Candle] = []
    with open(path, "r", encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        need = {"ts", "open", "high", "low", "close", "volume"}
        if not rd.fieldnames or not need.issubset(set(rd.fieldnames)):
            raise DataError(f"CSV harus punya kolom {sorted(need)}")
        for row in rd:
            try:
                out.append(Candle(int(row["ts"]), float(row["open"]), float(row["high"]),
                                  float(row["low"]), float(row["close"]), float(row["volume"])))
            except (ValueError, TypeError) as exc:
                raise DataError(f"baris CSV rusak: {row!r}") from exc
    return out


def closed_only(candles: Sequence[Candle], interval_ms: int, now_ms: int) -> List[Candle]:
    """Buang candle yang belum tutup."""
    return [c for c in candles if c.ts + interval_ms <= now_ms]


def _tokocrypto_payload(payload, expected_type, endpoint: str):
    """Unwrap documented Tokocrypto {code,msg,data,timestamp} envelopes.

    Direct payloads remain accepted for compatibility with legacy fixtures and
    compatible gateways. Non-zero API codes and malformed envelopes fail closed.
    """
    if isinstance(payload, dict):
        if "code" in payload:
            code = payload.get("code")
            if code != 0:
                raise DataError(
                    f"Tokocrypto {endpoint} API error code={code!r}: "
                    f"{payload.get('msg', 'unknown error')}"
                )
            if "data" not in payload:
                raise DataError(f"Tokocrypto {endpoint}: envelope tanpa data")
            payload = payload["data"]
        elif "data" in payload:
            payload = payload["data"]
    if not isinstance(payload, expected_type):
        raise DataError(f"Tokocrypto {endpoint}: bentuk payload tidak valid")
    return payload


def fetch_tokocrypto_klines(
    symbol: str, interval: str, limit: int = 500,
    base_url: str = "https://www.tokocrypto.site",
    retries: int = 3, timeout: float = 10.0,
) -> List[Candle]:
    """Candles publik Tokocrypto. Tidak menggunakan Binance."""
    if not isinstance(limit, int) or not 1 <= limit <= 1000:
        raise DataError("limit Tokocrypto harus integer 1..1000")
    if not symbol or not isinstance(symbol, str):
        raise DataError("symbol Tokocrypto kosong/tidak valid")
    qs = urllib.parse.urlencode({
        "symbol": symbol.replace("_", ""), "interval": interval, "limit": limit
    })
    url = f"{base_url}/api/v3/klines?{qs}"
    last_exc: Optional[Exception] = None

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                rows = json.loads(resp.read().decode())
            rows = _tokocrypto_payload(rows, list, "klines")
            out = []
            for idx, row in enumerate(rows):
                if not isinstance(row, (list, tuple)) or len(row) < 6:
                    raise DataError(f"Tokocrypto klines: baris {idx} kurang dari 6 kolom")
                out.append(Candle(int(row[0]), float(row[1]), float(row[2]),
                                  float(row[3]), float(row[4]), float(row[5])))
            if not out:
                raise DataError("Tokocrypto mengembalikan candle kosong")
            # API menjanjikan urutan ascending; jangan diam-diam sort karena
            # sorting dapat menyamarkan respons rusak/duplikat.
            if any(b.ts <= a.ts for a, b in zip(out, out[1:])):
                raise DataError("Tokocrypto klines tidak strictly ascending (duplikat/mundur)")
            return out
        except urllib.error.HTTPError as exc:
            # 418/429 membawa Retry-After; jangan retry membabi-buta dan memperpanjang ban.
            retry_after = exc.headers.get("Retry-After") if exc.headers else None
            raise DataError(
                f"Tokocrypto klines HTTP {exc.code}"
                + (f" (Retry-After={retry_after}s)" if retry_after else "")
            ) from exc
        except (
            urllib.error.URLError, TimeoutError, OSError,
            ValueError, KeyError, IndexError, TypeError
        ) as exc:
            last_exc = exc
            if attempt + 1 < retries:
                time.sleep(min(2 ** attempt, 8))

    raise DataError(
        f"Tokocrypto klines gagal setelah {retries} percobaan: {last_exc}"
    )


def fetch_tokocrypto_book_ticker(
    symbol: str,
    base_url: str = "https://www.tokocrypto.site",
    timeout: float = 5.0,
) -> BookQuote:
    """Bid/ask dari order book Tokocrypto. Gagal -> spread tidak diketahui."""
    if not isinstance(symbol, str) or not symbol:
        raise DataError("symbol Tokocrypto kosong/tidak valid")
    qs = urllib.parse.urlencode({"symbol": symbol.replace("_", ""), "limit": 5})
    url = f"{base_url}/api/v3/depth?{qs}"

    request_started = time.time()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            row = json.loads(resp.read().decode())

        row = _tokocrypto_payload(row, dict, "depth")
        bids, asks = row["bids"], row["asks"]
        if not bids or not asks:
            raise ValueError("order book kosong")

        bid, ask = float(bids[0][0]), float(asks[0][0])
        if not (math.isfinite(bid) and math.isfinite(ask)
                and bid > 0 and ask >= bid):
            raise ValueError("bid/ask tidak valid")

    except urllib.error.HTTPError as exc:
        retry_after = exc.headers.get("Retry-After") if exc.headers else None
        raise DataError(
            f"Tokocrypto order book HTTP {exc.code}"
            + (f" (Retry-After={retry_after}s)" if retry_after else "")
        ) from exc
    except (
        urllib.error.URLError, TimeoutError, OSError,
        ValueError, KeyError, TypeError, IndexError
    ) as exc:
        raise DataError(f"Tokocrypto order book gagal: {exc}") from exc

    # Age adalah durasi request lokal (lower-bound freshness), bukan timestamp
    # exchange yang tidak disediakan sebagai update-time per level.
    received_at = time.time()
    return BookQuote(bid, ask, observed_at=request_started, now=received_at)
