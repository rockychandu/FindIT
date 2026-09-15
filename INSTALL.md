# FindIT - Installation & Setup Guide

## System Requirements
- Python 3.8+
- Node.js 16+ (optional, for asset tooling)
- Git

## Dependency Manifests & Lockfiles
This project provides full dependency specifications and lockfiles:
- `requirements.txt` (Python Pip Manifest)
- `package.json` (Node Manifest)
- `poetry.lock` (Poetry Lockfile)
- `package-lock.json` (npm Lockfile)
- `Pipfile` & `Pipfile.lock` (Pipenv Lockfile)

## Quick Start Installation

1. **Clone Repository**
```bash
git clone https://github.com/rockychandu/FindIT.git
cd FindIT
```

2. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

3. **Run Application**
```bash
python app.py
```
Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your web browser.

4. **Run Automated Test Suite**
```bash
pytest -v
```
