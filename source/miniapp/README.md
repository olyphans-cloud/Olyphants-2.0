# Olyphants Mini App — dashboard PAPER lokal

Mini App terhubung ke dashboard backend PAPER lokal. Route `/miniapp` menyajikan halaman ini; halaman membaca `/api/state` dan menggunakan endpoint `/api/select`, `/api/disarm`, dan `/api/step` yang sama dengan dashboard robot.

## Menjalankan

1. Dari root source, jalankan dashboard PAPER: `python -m btc_robot dashboard --coins BTCUSDT,ETHUSDT --port 8765`.
2. Buka `http://127.0.0.1:8765/miniapp` pada browser perangkat yang sama.
3. Pilih market Spot atau Futures, pilih simbol, lalu Terapkan. Market hanya dapat berganti bila tidak ada posisi PAPER terbuka di market sebelumnya. Spot dan Futures memakai state directory berbeda; Futures mempertahankan state path lama.
4. `1 Siklus PAPER` memanggil pipeline PAPER; `Nonaktifkan robot` melepas status aktif sesi. Tidak ada order LIVE.

Dashboard tetap bind ke loopback. URL loopback tidak dapat dibuka Telegram dari internet. Telegram Mini App publik memerlukan backend HTTPS yang dapat dijangkau dan validasi Telegram `initData` server-side. Paket ini tidak menyediakan hosting/tunnel publik dan tidak menaruh token bot di frontend.

## Batas

- Exchange: Tokocrypto; mode PAPER saja.
- Strategi: D1 regime / H4 eksekusi. Futures mempertahankan `d1h4_futures`; Spot menggunakan `d1h4_spot` long-only.
- Market selector backend tersedia hanya untuk konfigurasi yang ditemukan saat startup. Jika config Spot tidak tersedia, Spot tidak akan ditawarkan sebagai market aktif.
- AI Scan memerlukan sumber candle yang dikonfigurasi; tanpa sumber data, endpoint menolak scan dengan jelas.
- News belum terhubung ke backend pada paket ini.
