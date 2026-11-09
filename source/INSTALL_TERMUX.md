# Instalasi di Termux (PAPER)

Paket ini belum pernah dipasang pada perangkat Termux pengguna. Instal ke folder terpisah terlebih dahulu agar source/state aktif tidak tertimpa.

```sh
pkg install python unzip -y
mkdir -p "$HOME/termux-studio/Olyphants-integrated-check"
unzip -q olyphants_full_source_integrated_final.zip -d "$HOME/termux-studio/Olyphants-integrated-check"
cd "$HOME/termux-studio/Olyphants-integrated-check/olyphants_release_clean"
python -m compileall -q btc_robot
python -m pytest -q tests/test_miniapp_backend_bridge.py tests/test_dashboard_multisymbol_display.py tests/test_tokocrypto_adapter.py tests/test_d1h4_isolation.py tests/test_paper.py tests/test_safeguard.py tests/test_recovery.py
```

Setelah hasil dan konfigurasi lokal diperiksa, integrasikan secara manual ke working copy aktif. Jangan menimpa `state/`, `config.active.json`, `.env`, kill switch, atau audit evidence. PAPER only; jangan gunakan LIVE.
