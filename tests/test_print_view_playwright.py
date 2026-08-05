import re
import os
import tempfile
from pathlib import Path

import pypdf


_JS_DIR = Path(__file__).parent / "js"


def _load_js(script_name):
    return (_JS_DIR / script_name).read_text(encoding="utf-8")


def _build_test_csv(total_rows):
    header = "Product,Type,MAC,Pairing Code,Description,QR\n"
    rows = [header]
    for i in range(total_rows):
        rows.append(
            f"Product {i},Switch,00:11:22:33:44:{i:02X},{10000000000 + i},Device {i},test-qr-{i}\n"
        )
    return "".join(rows)


def _extract_grid_layout_from_dom(page):
    return page.evaluate(_load_js("extract_grid_layout_from_dom.js"))


def _extract_physical_print_pages_from_dom(page):
    return page.evaluate(_load_js("extract_physical_print_pages_from_dom.js"))


def _extract_pdf_page_device_counts(pdf_path):
    reader = pypdf.PdfReader(pdf_path)
    device_counts = []

    for pdf_page in reader.pages:
        text = pdf_page.extract_text() or ""
        device_counts.append(len(re.findall(r"\bDevice\s+\d+\b", text)))

    return device_counts


def test_print_view_has_4x4_grid_layout_for_full_pages(live_server, page):
    base_url = live_server(_build_test_csv(36))
    page.goto(f"{base_url}/", wait_until="networkidle")
    page.evaluate("window.setView('grid')")
    page.wait_for_timeout(500)
    page.emulate_media(media="print")
    layout = _extract_grid_layout_from_dom(page)
    fd, pdf_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    try:
        page.pdf(path=pdf_path, print_background=True, format="Letter")
        physical_page_device_counts = _extract_pdf_page_device_counts(pdf_path)
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    assert layout == [[4, 4, 4, 4], [4, 4, 4, 4], [4]]
    assert physical_page_device_counts, "Expected at least one physical print page"
    assert physical_page_device_counts == [16, 16, 4]
