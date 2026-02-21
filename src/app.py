import os
import csv
from flask import Flask, render_template, jsonify, request, send_file
import io
from repositories import MatterRepository
import tomllib
import requests

app = Flask(__name__)

def get_project_metadata():
    try:
        with open("pyproject.toml", "rb") as f:
            return tomllib.load(f)
    except Exception:
        return {}

metadata = get_project_metadata()
VERSION = metadata.get("project", {}).get("version", "0.0.0")
GITHUB_URL = metadata.get("project", {}).get("urls", {}).get("Repository", "https://github.com/dsheehan/qrcodex_dev")

def get_github_repo():
    if "github.com/" in GITHUB_URL:
        return GITHUB_URL.split("github.com/")[1].strip("/")
    return "dsheehan/qrcodex_dev" # Fallback

GITHUB_REPO = get_github_repo()

@app.context_processor
def inject_metadata():
    return dict(version=VERSION, github_url=GITHUB_URL)

# Ensure the app knows where to find the CSV file
# Use an environment variable for flexibility (especially for Docker mounts)
def get_data_path():
    return os.getenv('MATTER_DATA_PATH', os.path.join(os.getcwd(), 'data', 'matter.csv'))

def get_repo():
    return MatterRepository(get_data_path())


@app.route('/')
def index():
    repo = get_repo()
    data, headers = repo.get_all()
    if not headers:
        return "File not found or empty", 404
    return render_template('matter.html', data=data, headers=headers)


def is_newer_version(latest, current):
    try:
        l = [int(x) for x in latest.lstrip('v').split('.')]
        c = [int(x) for x in current.lstrip('v').split('.')]
        for i in range(max(len(l), len(c))):
            lv = l[i] if i < len(l) else 0
            cv = c[i] if i < len(c) else 0
            if lv > cv:
                return True
            if lv < cv:
                return False
        return False
    except Exception:
        return False

@app.route('/api/latest-release')
def get_latest_release():
    try:
        response = requests.get(f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest", timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest_tag = data.get("tag_name", "0.0.0")
            return jsonify({
                "current_version": VERSION,
                "latest_version": latest_tag,
                "is_newer": is_newer_version(latest_tag, VERSION),
                "release_notes": data.get("body"),
                "html_url": data.get("html_url")
            })
        return jsonify({"error": "Failed to fetch release info"}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/qrcode')
def qrcode():
    return render_template('qrcode.html')


@app.route('/licenses')
def licenses():
    return render_template('licenses.html')


@app.route('/matter', methods=['GET'])
def get_matter():
    repo = get_repo()
    data, _ = repo.get_all()
    if not data and not os.path.exists(get_data_path()):
        return jsonify({"error": "File not found"}), 404
    return jsonify(data)


@app.route('/matter', methods=['POST'])
def add_matter():
    new_device = request.json
    repo = get_repo()
    try:
        saved_device = repo.add(new_device)
        return jsonify(saved_device), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route('/matter/<mac>', methods=['PUT'])
def update_matter(mac):
    updated_device = request.json
    repo = get_repo()
    result = repo.update(mac, updated_device)
    
    if result is None:
        return jsonify({"error": "Device not found"}), 404
        
    return jsonify(result)


@app.route('/matter/<mac>', methods=['DELETE'])
def delete_matter(mac):
    repo = get_repo()
    if repo.delete(mac):
        return jsonify({"success": True}), 200
    else:
        return jsonify({"error": "Device not found"}), 404


@app.route('/matter/export', methods=['GET'])
def export_matter():
    return send_file(get_data_path(), as_attachment=True, download_name='matter.csv', mimetype='text/csv')


@app.route('/matter/import', methods=['POST'])
def import_matter():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)
        new_records = [row for row in csv_input]
        repo = get_repo()
        added_count = repo.bulk_add(new_records)
        return jsonify({"success": True, "added_count": added_count}), 200


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "version": VERSION
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
