import os
import csv
from flask import Flask, render_template, jsonify, request
from repositories import MatterRepository

app = Flask(__name__)

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


if __name__ == '__main__':
    app.run(debug=True)
