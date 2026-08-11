<div align="center">

# QRchive

[![Python Version](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.1.2-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/dsheehan/qrchive?tab=MIT-1-ov-file)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![GitHub Release](https://img.shields.io/github/v/release/dsheehan/qrchive)](https://github.com/dsheehan/qrchive/releases)
[![Docker Image CI](https://github.com/dsheehan/qrchive/actions/workflows/docker-image.yml/badge.svg)](https://github.com/dsheehan/qrchive/actions/workflows/docker-image.yml)
[![GitHub last commit](https://img.shields.io/github/last-commit/dsheehan/qrchive)](https://github.com/dsheehan/qrchive/commits/main)

**QRchive** is a dockerized, self-hosted web application to help store your Matter QR codes and device pairing codes. Scan directly from your mobile device or webcam, print them out for physical reference, and keep all your smart home pairing information in one place.

[Features](#-features) • [Screenshots](#-screenshots) • [Quick Start - Docker](#-quick-start-recommended) • [Changelog](CHANGELOG.md) • [Development Guide](DEVELOPMENT.md) • [License](https://github.com/dsheehan/qrchive?tab=MIT-1-ov-file)

</div>

---

### ✨ Features

- 📱 **Matter-Ready**: Built specifically for tracking Matter-compatible devices.
- 🔍 **QR Scanner**: Scan QR codes directly from your mobile device, webcam, or by uploading an image.
- 📊 **CSV Management**: Seamlessly import and export your device lists.
- 🎨 **Modern UI**: Clean, responsive dashboard with **Dark Mode** support.
- 🛠️ **Full CRUD**: Add, edit, and delete devices with ease.
- 🖨️ **Print View**: Print your device QR codes in a tidy grid layout for physical reference.
- 📦 **Docker Support**: Containerized for easy self-hosted deployment.

### 📸 Screenshots

<img src="https://github.com/user-attachments/assets/4916b3c8-52d0-4024-80ca-4df5fc161f47" alt="Homepage" height="200">
<img src="https://github.com/user-attachments/assets/a59855ef-c444-4c83-9bd0-3cf2e3ac1a6b" alt="Grid View" height="200">
<img src="https://github.com/user-attachments/assets/4019255c-6942-4cb2-b424-9d7f055b272d" alt="Print View" height="200">
<img src="https://github.com/user-attachments/assets/baa001ed-1421-4998-9a76-5fcf97fb4664" alt="View QR Code" height="200">
<img src="https://github.com/user-attachments/assets/7fd36e3a-2557-4e05-a6b4-5d52d0184754" alt="Add/Edit Device, with Camera/Image upload" height="200">


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

<div align="center">
Made with ❤️ for the Smart Home Community
</div>
