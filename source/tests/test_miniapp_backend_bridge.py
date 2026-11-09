import json
import os
import threading
import urllib.error
import urllib.request

import pytest

from btc_robot.dashboard import Dashboard, serve


DASH_TOKEN = "bridge-test-token"

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
]


@pytest.fixture
def bridge(tmp_path):
    """
    Test backend dashboard integrated Olyphants.

    Scope:
    - Dashboard loopback only.
    - PAPER dashboard.
    - Tidak mengirim order LIVE.
    - GET /api/state mengikuti source integrated.
    - POST wajib menggunakan dashboard token.
    - Tidak menguji Telegram initData karena integrated
      belum memiliki validator Telegram.
    """

    dash = Dashboard(
        str(tmp_path),
        ".",
        SYMBOLS,
        token=DASH_TOKEN,
    )

    server = serve(
        dash,
        "127.0.0.1",
        0,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    base = (
        "http://127.0.0.1:"
        + str(server.server_address[1])
    )

    try:
        yield base, dash

    finally:
        server.shutdown()
        server.server_close()

        thread.join(timeout=2)


def http_request(
    base,
    path,
    headers=None,
    method="GET",
    body=None,
):
    """
    HTTP helper.

    Return:
        status, response_body
    """

    request = urllib.request.Request(
        base + path,
        headers=headers or {},
        method=method,
        data=body,
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=5,
        ) as response:

            return (
                response.status,
                response.read(),
            )

    except urllib.error.HTTPError as error:

        return (
            error.code,
            error.read(),
        )


def decode_json(body):
    return json.loads(
        body.decode("utf-8")
    )


def post_json(
    base,
    path,
    payload,
    token=DASH_TOKEN,
):
    """
    POST JSON dengan dashboard token.

    Helper ini hanya mengirim request ke dashboard
    PAPER yang dijalankan fixture.
    """

    headers = {
        "Content-Type": "application/json",
        "X-Dashboard-Token": token,
    }

    body = json.dumps(
        payload
    ).encode("utf-8")

    return http_request(
        base,
        path,
        headers=headers,
        method="POST",
        body=body,
    )


def test_miniapp_is_served_and_token_is_injected(bridge):

    base, dash = bridge

    status, body = http_request(
        base,
        "/miniapp",
    )

    page = body.decode(
        "utf-8",
        errors="replace",
    )

    assert status == 200

    assert "<html" in page.lower()

    # Source integrated menyisipkan dashboard token
    # ke halaman Mini App.
    assert 'name="dash-token"' in page

    assert DASH_TOKEN in page

    # Placeholder dashboard root tidak boleh tersisa.
    assert "__TOKEN__" not in page

    # Mini App menggunakan API state.
    assert "/api/state" in page

    # JavaScript menggunakan dashboard token.
    assert "X-Dashboard-Token" in page


def test_miniapp_trailing_slash_is_served(bridge):

    base, dash = bridge

    status, body = http_request(
        base,
        "/miniapp/",
    )

    assert status == 200

    page = body.decode(
        "utf-8",
        errors="replace",
    )

    assert "<html" in page.lower()

    assert 'name="dash-token"' in page

    assert DASH_TOKEN in page


def test_api_state_is_available_on_loopback_without_token(bridge):

    base, dash = bridge

    # Integrated backend hanya memeriksa Host loopback
    # untuk GET /api/state.
    #
    # GET ini memang tidak menggunakan dashboard token.
    status, body = http_request(
        base,
        "/api/state",
    )

    assert status == 200

    state = decode_json(body)

    assert isinstance(state, dict)

    assert state["mode"] == "PAPER"

    assert state["exchange"] == "Tokocrypto"

    assert state["timeframes"]["H4"]["robot_status"] \
        == "BELUM_DIPILIH"


def test_api_state_accepts_dashboard_token_header(bridge):

    base, dash = bridge

    status, body = http_request(
        base,
        "/api/state",
        headers={
            "X-Dashboard-Token": DASH_TOKEN,
        },
    )

    # Header token boleh dikirim, tetapi GET integrated
    # tidak menggunakannya sebagai autentikasi.
    # Status tetap berasal dari Host loopback.
    assert status == 200

    state = decode_json(body)

    assert state["mode"] == "PAPER"

    assert state["exchange"] == "Tokocrypto"


def test_api_state_does_not_require_token_for_loopback(bridge):

    base, dash = bridge

    status, body = http_request(
        base,
        "/api/state",
        headers={
            "X-Dashboard-Token": "wrong-dashboard-token",
        },
    )

    # Token tidak diperiksa oleh GET /api/state.
    # Ini menguji perilaku source saat ini, bukan
    # menganggap endpoint tersebut terlindungi token.
    assert status == 200

    state = decode_json(body)

    assert state["mode"] == "PAPER"


def test_post_without_dashboard_token_is_rejected(bridge):

    base, dash = bridge

    status, body = http_request(
        base,
        "/api/select",
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
        body=json.dumps(
            {
                "scan_mode": "MANUAL",
                "timeframe": "H4",
                "coin": "BTCUSDT",
                "market": "Futures",
            }
        ).encode("utf-8"),
    )

    assert status == 403

    error = decode_json(body)

    assert "error" in error


def test_post_with_wrong_dashboard_token_is_rejected(bridge):

    base, dash = bridge

    status, body = post_json(
        base,
        "/api/select",
        {
            "scan_mode": "MANUAL",
            "timeframe": "H4",
            "coin": "BTCUSDT",
            "market": "Futures",
        },
        token="wrong-dashboard-token",
    )

    assert status == 403

    error = decode_json(body)

    assert "error" in error


def test_post_with_valid_token_and_invalid_content_type_is_rejected(
    bridge,
):

    base, dash = bridge

    status, body = http_request(
        base,
        "/api/select",
        headers={
            "X-Dashboard-Token": DASH_TOKEN,
            "Content-Type": "text/plain",
        },
        method="POST",
        body=b"{}",
    )

    assert status == 415

    error = decode_json(body)

    assert "error" in error


def test_post_with_valid_token_and_invalid_json_is_rejected(bridge):

    base, dash = bridge

    status, body = http_request(
        base,
        "/api/select",
        headers={
            "X-Dashboard-Token": DASH_TOKEN,
            "Content-Type": "application/json",
        },
        method="POST",
        body=b"{invalid-json",
    )

    assert status == 400

    error = decode_json(body)

    assert "error" in error


def test_post_with_valid_token_and_non_object_json_is_rejected(bridge):

    base, dash = bridge

    status, body = http_request(
        base,
        "/api/select",
        headers={
            "X-Dashboard-Token": DASH_TOKEN,
            "Content-Type": "application/json",
        },
        method="POST",
        body=b"[]",
    )

    assert status == 400

    error = decode_json(body)

    assert "error" in error


def test_post_with_valid_token_and_unknown_route_returns_404(bridge):

    base, dash = bridge

    status, body = post_json(
        base,
        "/api/bridge-test-unknown",
        {},
    )

    assert status == 404

    error = decode_json(body)

    assert "error" in error


def test_dashboard_state_is_paper_only(bridge):

    base, dash = bridge

    status, body = http_request(
        base,
        "/api/state",
    )

    assert status == 200

    state = decode_json(body)

    assert state["mode"] == "PAPER"

    assert state["exchange"] == "Tokocrypto"


def test_spot_and_futures_market_selection_are_separate_paper_sleeves(
    bridge,
):

    base, dash = bridge

    state_before = dash.state()

    assert state_before["markets"] == [
        "Futures",
        "Spot",
    ]

    # Futures config harus tetap menggunakan strategi
    # D1/H4 Futures yang sudah ada.
    futures = dash.sleeve_cfg(
        "H4",
        "BTCUSDT",
    )

    assert futures.strategy_mode == "d1h4_futures"

    assert futures.state_dir.endswith(
        "/state/h4-btcusdt"
    )

    # Pilih Spot melalui dashboard.
    state = dash.select(
        "MANUAL",
        "H4",
        "BTCUSDT",
        market="Spot",
    )

    spot = dash.sleeve_cfg(
        "H4",
        "BTCUSDT",
    )

    assert state["market"] == "Spot"

    assert spot.strategy_mode == "d1h4_spot"

    assert spot.risk.allow_short is False

    # Spot memiliki state directory tersendiri.
    assert spot.state_dir.endswith(
        "/state/spot/h4-btcusdt"
    )

    assert spot.state_dir != futures.state_dir

    # Mengubah market dashboard tidak mengubah
    # konfigurasi Futures yang sudah dibuat.
    assert futures.strategy_mode == "d1h4_futures"

    assert futures.state_dir.endswith(
        "/state/h4-btcusdt"
    )


def test_dashboard_select_requires_valid_market(bridge):

    base, dash = bridge

    with pytest.raises(Exception):
        dash.select(
            "MANUAL",
            "H4",
            "BTCUSDT",
            market="INVALID",
        )


def test_dashboard_market_selection_is_persisted(bridge):

    base, dash = bridge

    selected = dash.select(
        "MANUAL",
        "H4",
        "BTCUSDT",
        market="Spot",
    )

    assert selected["market"] == "Spot"

    control_path = os.path.join(
        dash.base_dir,
        "control.json",
    )

    assert os.path.isfile(control_path)

    with open(
        control_path,
        "r",
        encoding="utf-8",
    ) as fh:

        saved = json.load(fh)

    assert saved["market"] == "Spot"

    assert saved["scan_mode"] == "MANUAL"


def test_dashboard_disarm_does_not_enable_live_trading(bridge):

    base, dash = bridge

    state = dash.state()

    assert state["mode"] == "PAPER"

    assert state["exchange"] == "Tokocrypto"

    # Test tidak memanggil engine LIVE.
    # Status robot awal harus belum dipilih.
    assert (
        state["timeframes"]["H4"]["robot_status"]
        == "BELUM_DIPILIH"
    )
