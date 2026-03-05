<div align="center">

# ⚡ QRchive

[![Python Version](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.1.2-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![GitHub Release](https://img.shields.io/github/v/release/dsheehan/qrchive)](https://github.com/dsheehan/qrchive/releases)
[![Docker Image CI](https://github.com/dsheehan/qrchive/actions/workflows/docker-image.yml/badge.svg)](https://github.com/dsheehan/qrchive/actions/workflows/docker-image.yml)

**The ultimate open-source dashboard for managing Matter devices and their QR codes.**

[Features](#-features) • [Quick Start](#-quick-start-recommended) • [Docker](#-quick-start-recommended) • [Tech Stack](#-tech-stack)

</div>

---

### 🚀 Overview

**QRchive** is a sleek, modern, and lightweight web application designed to help you manage your Matter connectivity devices. Whether you're tracking MAC addresses, pairing codes, or generating/scanning QR data, QRchive provides a clean interface to keep your smart home hardware organized.

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

### 🚀 Quick Start (Recommended)

Deploy QRchive in seconds using Docker.

#### 🐳 Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'
services:
  qrchive:
    image: ghcr.io/dsheehan/qrchive:latest
    container_name: qrchive
    ports:
      - "5000:5000"
    volumes:
      - /path/to/qrchive/data:/data
    restart: unless-stopped

volumes:
  qrchive-data:
```

Run with: `docker-compose up -d`

#### 🛠 Docker CLI

```bash
docker pull ghcr.io/dsheehan/qrchive:latest
docker run -d \
  -p 5000:5000 \
  -v /path/to/qrchive/data:/data \
  --name qrchive \
  ghcr.io/dsheehan/qrchive:latest
```

---

### 🛠 Development

Interested in contributing or building from source? See our [Development Guide](DEVELOPMENT.md).

### 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

<div align="center">
Made with ❤️ for the Smart Home Community
</div>
