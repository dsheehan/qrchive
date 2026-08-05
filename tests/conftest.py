import pytest
import os
import tempfile
import contextlib
import threading
from app import app
from werkzeug.serving import make_server


def _write(csv_content):
    fd, temp_path = tempfile.mkstemp(suffix='.csv')
    os.close(fd)

    with open(temp_path, 'w', encoding='utf-8', newline='') as f:
        if isinstance(csv_content, str):
            f.write(csv_content)
        elif isinstance(csv_content, (list, tuple)):
            f.writelines(
                f"{str(line).rstrip(chr(10))}\n" for line in csv_content
            )
        else:
            raise TypeError(
                'csv_content must be a string or an array of rows'
            )

    return temp_path

@pytest.fixture
def matter_data_path():
    """
    Factory fixture that creates a temporary CSV, points MATTER_DATA_PATH to it,
    and restores environment on teardown.
    """
    old_path = os.getenv('MATTER_DATA_PATH')
    created_paths = []

    def _create(csv_content):
        temp_path = _write(csv_content)
        created_paths.append(temp_path)
        os.environ['MATTER_DATA_PATH'] = temp_path
        return temp_path

    yield _create

    if old_path is None:
        os.environ.pop('MATTER_DATA_PATH', None)
    else:
        os.environ['MATTER_DATA_PATH'] = old_path

    for path in created_paths:
        if os.path.exists(path):
            os.remove(path)


@pytest.fixture
def client(matter_data_path):
    # Setup: use a temporary file for the data
    matter_data_path(
        "Product,Type,MAC,Pairing Code,Description,QR\n"
        "Tapo S505D,Switch,00:11:22:33:44:55,12345678901,Bedroom Switch,test-qr-data\n"
    )
    
    app.testing = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def live_server(matter_data_path):
    servers = []

    def _start(csv_content):
        matter_data_path(csv_content)
        server = make_server("127.0.0.1", 0, app)
        port = server.socket.getsockname()[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        servers.append((server, thread))
        return f"http://127.0.0.1:{port}"

    yield _start

    for server, thread in servers:
        server.shutdown()
        thread.join(timeout=3)


@pytest.fixture
def playwright_sync_api():
    return pytest.importorskip("playwright.sync_api")


@pytest.fixture
def browser(playwright_sync_api):
    with playwright_sync_api.sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(channel="msedge")
        except Exception as exc:  # pragma: no cover - environment dependent
            pytest.skip(f"Playwright browser is not available: {exc}")

        with contextlib.closing(browser):
            yield browser


@pytest.fixture
def page(browser):
    page = browser.new_page()
    try:
        yield page
    finally:
        page.close()
