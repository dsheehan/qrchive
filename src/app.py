import os
from flask import Flask, render_template, jsonify, request, send_file, Response
from services import import_from_csv, export_to_csv
import io
from repositories import MatterRepository
import tomllib
from licenses import get_licenses_data

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
    return dict(version=VERSION, github_url=GITHUB_URL, github_repo=GITHUB_REPO)

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



@app.route('/licenses')
def licenses():
    all_licenses = get_licenses_data()
    return render_template('licenses.html', licenses=all_licenses)


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
    repo = get_repo()
    data, headers = repo.get_all()
    csv_content = export_to_csv(data, headers)
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=matter.csv"}
    )


@app.route('/matter/import', methods=['POST'])
def import_matter():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        new_records = import_from_csv(file.stream)
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
