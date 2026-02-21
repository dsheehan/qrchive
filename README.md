<div align="center">

# ⚡ QRCodex

[![Python Version](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.1.2-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

**The ultimate open-source dashboard for managing Matter devices and their QR codes.**

[Features](#-features) • [Quick Start](#-quick-start) • [Docker](#-docker-deployment) • [Tech Stack](#-tech-stack)

</div>

---

### 🚀 Overview

**QRCodex** is a sleek, modern, and lightweight web application designed to help you manage your Matter connectivity devices. Whether you're tracking MAC addresses, pairing codes, or generating/scanning QR data, QRCodex provides a clean interface to keep your smart home hardware organized.

### ✨ Features

- 📱 **Matter-Ready**: Built specifically for tracking Matter-compatible devices.
- 🔍 **QR Scanner**: Integrated camera-based and image-upload QR code readers.
- 📊 **CSV Management**: Seamlessly import and export your device lists.
- 🎨 **Modern UI**: Clean, responsive dashboard with **Dark Mode** support.
- 🛠️ **Full CRUD**: Add, edit, and delete devices with ease.
- 📦 **Docker Support**: Containerized for instant deployment.

### 🛠 Tech Stack

- **Backend:** [Python 3.14+](https://www.python.org/) + [Flask](https://flask.palletsprojects.com/)
- **Frontend:** HTML5, CSS3, JavaScript (Bootstrap 5 + FontAwesome)
- **Package Manager:** [uv](https://github.com/astral-sh/uv)
- **Containerization:** [Docker](https://www.docker.com/)

---

### 🏁 Quick Start

#### Using `uv` (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/dsheehan/qrcodex_dev.git
   cd qrcodex
   ```

2. **Install dependencies and run:**
   ```bash
   uv run flask run
   ```

3. **Access the dashboard:**
   Open `http://localhost:5000` in your browser.

#### Using Docker

Deploy QRCodex in seconds using Docker:

```bash
docker build -t qrcodex .
docker run -p 5000:5000 -v qrcodex-data:/data qrcodex
```

---

### 📁 Project Structure

```text
├── src/
│   ├── app.py           # Flask application core
│   ├── repositories.py  # Data persistence logic
│   ├── static/          # Styles, scripts, and images
│   └── templates/       # Jinja2 HTML templates
├── data/                # Default CSV storage
├── tests/               # Pytest suite
└── Dockerfile           # Container definition
```

---

### 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to help improve QRCodex.

### 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

<div align="center">
Made with ❤️ for the Smart Home Community
</div>
