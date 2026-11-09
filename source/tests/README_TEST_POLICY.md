# Rebuild test policy (2026-11-08)

Legacy tests that generated synthetic candles/prices or used `generate_synthetic()` as market data have been removed from this test suite. They must not be reintroduced as evidence of market-data correctness, strategy performance, or PAPER readiness.

Remaining tests are contract/unit tests (e.g. parsing documented Tokocrypto API envelopes, validating safeguards, and checking Mini App wiring). A mocked HTTP response in a contract test is only a parser fixture; it is not real market evidence.

Market-data validation must be performed separately on-device with network access, against Tokocrypto public endpoints. Preserve the raw response/source, symbol, interval, retrieval timestamp, candle open timestamps, and validation result. If live data cannot be retrieved, report the check as BLOCKED/NOT RUN; never fabricate candles or use synthetic data to make it pass.
