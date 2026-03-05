# 🛠 Development Guide

This guide is for developers who want to contribute to **QRchive** or run it from source.

### 🏁 Quick Start for Developers

#### Using `uv` (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/dsheehan/qrchive.git
   cd qrchive
   ```

2. **Install dependencies and run:**
   ```bash
   uv run flask run
   ```

3. **Access the dashboard:**
   Open `http://localhost:5000` in your browser.

#### Using Docker (Local Build)

If you want to build and run the container locally:

```bash
docker build -t qrchive .
docker run -p 5000:5000 -v qrchive-data:/data qrchive
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

### 📦 Maintenance & Releases

To ensure consistency in project maintenance, we use AI agent prompts located in `Agents.md`.

#### Preparing a Release
Use the **"Increase Project Version Prompt"** in `Agents.md` to:
- Bump the version in `pyproject.toml` and `package.json`.
- Update the `CHANGELOG.md` (renaming `[Unreleased]` to the new version).
- Create a Git tag and push it.

#### Updating the Changelog
Use the **"Update CHANGELOG.md Prompt"** after completing a feature or fix to:
- Automatically summarize recent changes into the `[Unreleased]` section.

---

### 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to help improve QRchive.
