import pytest
import os
import tempfile
from app import app


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
