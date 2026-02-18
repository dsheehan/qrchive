import os
import csv
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Ensure the app knows where to find the CSV file relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATTER_CSV_PATH = os.path.join(BASE_DIR, 'matter.csv')


@app.route('/')
def index():
    data = []
    try:
        with open(MATTER_CSV_PATH, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            for row in reader:
                data.append(row)
        return render_template('matter.html', data=data, headers=headers)
    except FileNotFoundError:
        return "File not found", 404


@app.route('/qrcode')
def qrcode():
    return render_template('qrcode.html')


@app.route('/matter')
def get_matter():
    data = []
    try:
        with open(MATTER_CSV_PATH, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404


if __name__ == '__main__':
    app.run(debug=True)
