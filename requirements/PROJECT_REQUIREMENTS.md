# OLYPHANTS PROJECT REQUIREMENTS

Dokumen ini merangkum keputusan dan permintaan Olyphants
yang tersedia dalam konteks percakapan.

Dokumen ini bukan bukti fitur telah selesai.
Implementasi harus diverifikasi dari source dan test.

============================================================
A. TUJUAN
============================================================

1. Periksa full source Olyphants.
2. Integrasikan Mini App/dashboard terbaru ke full source.
3. Periksa wallet sesuai permintaan terbaru.
4. Pertahankan strategi dan konfigurasi yang ada.
5. Jalankan pemeriksaan dan test yang dapat dilakukan.
6. Hasil pekerjaan akhir berupa source yang diperbaiki dan ZIP.
7. Jangan mengklaim selesai sebelum implementasi diverifikasi.

Gunakan paket Mini App terbaru.
Jangan mencampur prototipe dashboard lama dengan versi terbaru.

============================================================
B. STRATEGI
============================================================

1. Pertahankan Futures D1/H4.
2. Spot dan Futures harus terpisah.
3. Adaptasi Spot harus terpisah dari strategi Futures.
4. Jangan menghapus Futures ketika membuat Spot.
5. Hanya satu mode strategi aktif pada satu waktu.
6. Futures tetap tersedia ketika Spot dipilih.
7. Pertahankan profil operasional D1/H4.
8. Jangan mengganti strategi dengan M1/H1 tanpa permintaan.
9. Strategy Library merupakan komponen internal Olyphants.
10. Strategy Selector mengikuti kondisi market.
11. NO TRADE merupakan hasil yang valid.
12. Candidate strategy harus diuji sebelum tervalidasi.
13. Jangan mengarang strategi yang tidak ditemukan di source.

============================================================
C. DASHBOARD / MINI APP
============================================================

1. Integrasikan dashboard terbaru ke full source.
2. Jangan menggunakan prototipe lama sebagai pengganti.
3. Spot dan Futures terlihat terpisah.
4. Masing-masing mode menyediakan:
   - AI Scan
   - Manual
   - Trade Strategy
5. Trade Strategy menyediakan pemilihan strategi.
6. Detail/config mengikuti strategi yang tersedia.
7. D1/H4 tetap menjadi profil operasional.
8. Dashboard menunjukkan PAPER.
9. Dashboard tidak boleh mengaktifkan LIVE.
10. ZIP ditemukan bukan berarti dashboard terintegrasi.
11. Periksa tombol, callback, endpoint, backend, dan status.
12. Periksa menu lama yang masih menunjuk strategi/interval
    yang tidak sesuai.

============================================================
D. WALLET
============================================================

1. Wallet termasuk ruang lingkup pekerjaan terbaru.
2. Sebelumnya wallet ditunda; permintaan terbaru
   menggantikan penundaan tersebut.
3. Periksa implementasi wallet yang sudah ada.
4. Identifikasi file, fungsi, endpoint, konfigurasi,
   dependensi, dan test wallet.
5. Tentukan fungsi wallet dari source aktual.
6. Jangan membuat wallet baru berdasarkan dugaan.
7. Jangan menampilkan seed, private key, token,
   credential, atau saldo privat di laporan.
8. Jangan menghapus wallet atau data wallet.
9. Jangan mengirim transaksi.
10. Jangan mengaktifkan LIVE.
11. Jika kebutuhan tidak jelas dari source,
    tandai BELUM TERVERIFIKASI.

============================================================
E. EXCHANGE
============================================================

Tujuan migrasi yang dibahas:

- Tokocrypto menjadi exchange target.
- Binance dan Bybit dilepas dari integrasi robot
  sesuai permintaan pengguna.
- Jangan menganggap migrasi selesai.
- Periksa source, konfigurasi, market data, candle,
  symbol mapping, order interface, dan test.
- Jangan mengarang endpoint atau symbol.
- Jangan menguji LIVE trading.
- Jangan menghapus audit atau state.
- API discovery sebelumnya belum membuktikan
  integrasi robot selesai.

============================================================
F. PAPER / SAFETY
============================================================

1. PAPER menjadi batas operasional.
2. Tidak menjalankan LIVE trading.
3. Jangan mengubah kill switch.
4. Jangan menghapus KILL_SWITCH atau KILL_ALL.
5. Jangan menghapus state atau audit evidence.
6. Jangan mereset paper_state.
7. Jangan mengubah safeguard agar test terlihat lulus.
8. Periksa konsistensi state dan ledger.
9. Periksa konfigurasi PAPER D1/H4.
10. API berhasil bukan berarti trading boleh aktif.

============================================================
G. AI / TELEGRAM
============================================================

1. Gemini digunakan untuk analisis PAPER.
2. Gemini bukan executor LIVE.
3. NEWS merupakan fitur terpisah.
4. Tidak membuat free-chat Gemini tanpa permintaan.
5. Periksa Telegram bot dan command handler.
6. Periksa deduplication signal/reply.
7. Hindari pesan duplikat.
8. Jangan memasukkan token Telegram ke laporan.
9. Periksa menu dashboard dan command bot.

============================================================
H. PENGUJIAN
============================================================

Periksa:

- Python compile.
- Full pytest.
- Strategi.
- Spot/Futures separation.
- PAPER guard.
- Dashboard syntax.
- Frontend jika tool tersedia.
- Exchange tests.
- Wallet tests.
- Regression tests.
- Missing configuration examples.
- Error dan traceback.

Test gagal tidak boleh disembunyikan.
Test yang tidak dapat dijalankan harus ditandai.
Jangan mengubah expected result untuk memaksa lulus.
Jangan mengklaim browser test dilakukan jika tidak.

============================================================
I. HASIL YANG DIHARAPKAN
============================================================

Setelah source diperiksa:

- Laporan temuan.
- Daftar file yang perlu diubah.
- Dashboard terbaru terintegrasi.
- Wallet diperiksa sesuai source dan kebutuhan.
- Spot/Futures tetap terpisah.
- PAPER tetap menjadi batas.
- Test dan regression report.
- Source ZIP hasil perbaikan.
- Daftar pekerjaan belum selesai.
- Tidak mengklaim LIVE/exchange execution berhasil
  tanpa pengujian yang sesuai.

============================================================
J. STATUS AWAL
============================================================

Dashboard integration : BELUM DIVERIFIKASI
Wallet implementation: BELUM DIVERIFIKASI
Exchange migration   : BELUM DIVERIFIKASI
Full test suite     : BELUM DIVERIFIKASI
Browser testing     : BELUM DIVERIFIKASI
LIVE trading        : TIDAK DIIZINKAN
PAPER               : BATAS OPERASIONAL
