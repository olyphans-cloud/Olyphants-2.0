# Olyphants Mini App — dashboard PAPER lokal (tema hijau)

Satu-satunya UI dashboard. Disajikan backend lokal pada `/` dan `/miniapp`; membaca `/api/state` dan memakai
`/api/select`, `/api/arm` (ON), `/api/disarm` (OFF).

## Menjalankan
1. Dari root paket: `python -m btc_robot dashboard --coins BTCUSDT,ETHUSDT --port 8765`
2. Buka `http://127.0.0.1:8765/` di browser perangkat yang sama.
3. Pilih Spot atau Futures, buka menu Manual dan pilih simbol (langsung diterapkan), atau AI Scan.
4. Tekan **ON**. Status baru menjadi **AKTIF** setelah siklus PAPER pertama sukses mengambil data Tokocrypto.
   Selama data gagal statusnya MENUNGGU SIKLUS PERTAMA / TERTAHAN. **OFF** menghentikan siklus.

## Batas
- Tokocrypto, PAPER saja, strategi D1 regime / H4 eksekusi. Tidak ada tombol LIVE, M1/H1, "Terapkan simbol", atau "1 Siklus PAPER".
- Robot selalu OFF saat dashboard dimulai; ON tidak tersimpan antar-restart.
- Dashboard bind ke loopback. Telegram Mini App publik butuh backend HTTPS + validasi `initData` (belum tersedia di paket ini).
- Menu News belum terhubung ke backend.
