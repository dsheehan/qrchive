import csv
import io
import os

def export_to_csv(data, headers):
    """
    Export data to a CSV string.
    :param data: List of dictionaries representing the records.
    :param headers: List of strings for the CSV headers.
    :return: CSV content as a string.
    """
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()

def import_from_csv(file_stream):
    """
    Import data from a CSV file stream.
    :param file_stream: File-like object (e.g., from request.files['file'].stream).
    :return: List of dictionaries representing the imported records.
    """
    # Ensure we are at the beginning of the stream if possible
    if hasattr(file_stream, 'seek'):
        file_stream.seek(0)
    
    # Handle both binary and text streams
    content = file_stream.read()
    if isinstance(content, bytes):
        content = content.decode('utf-8')
    
    stream = io.StringIO(content)
    reader = csv.DictReader(stream)
    return [row for row in reader]

def read_csv_file(file_path):
    """
    Read a CSV file and return the data and headers.
    :param file_path: Path to the CSV file.
    :return: Tuple of (data, headers).
    """
    data = []
    headers = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            data = [row for row in reader]
    except FileNotFoundError:
        pass
    return data, headers

def write_csv_file(file_path, data, headers):
    """
    Write data to a CSV file.
    :param file_path: Path to the CSV file.
    :param data: List of dictionaries.
    :param headers: List of headers.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
