import pytest


def _build_filter_test_csv():
    return "".join(
        [
            "Product,Type,MAC,Pairing Code,Description,QR\n",
            "Alice Plug,Switch,00:11:22:33:44:01,12345678901,alice office,test-qr-1\n",
            "Bob Plug,Switch,00:11:22:33:44:02,12345678902,Kitchen Potlights,test-qr-2\n",
            "Carol Plug,Switch,00:11:22:33:44:03,12345678903,carol hallway,test-qr-3\n",
        ]
    )


def _visible_products(page):
    return page.eval_on_selector_all(
        "#devicesTable tbody tr",
        """
        (rows) => rows
            .filter((row) => row.style.display !== 'none')
            .map((row) => (row.cells[0]?.innerText || '').trim())
        """,
    )


def _apply_filter_and_get_visible_products(page, query):
    page.fill("#globalFilter", query)
    page.wait_for_timeout(200)
    return _visible_products(page)


def test_global_filter_not_with_bare_term_works_in_ui(live_server, page):
    base_url = live_server(_build_filter_test_csv())
    page.goto(f"{base_url}/", wait_until="networkidle")

    scenarios = [
        ("NOT alice", ["Bob Plug", "Carol Plug"]),
        ("light", ["Bob Plug"]),
        ('"light"', []),
        ("light*", []),
        ("*light*", ["Bob Plug"]),
        ("K", ["Bob Plug"]),
        ("K*", ["Bob Plug"]),
        ("*K*", ["Bob Plug"]),
        ("*K", ["Bob Plug"]),
        ('"*K"', ["Bob Plug"]),
    ]

    for query, expected_products in scenarios:
        assert _apply_filter_and_get_visible_products(page, query) == expected_products