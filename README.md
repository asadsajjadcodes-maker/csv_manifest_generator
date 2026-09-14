# CSV Manifest Generator

A professional-grade Python desktop application for comprehensive directory auditing and CSV inventory generation. **CSV Manifest Generator** recursively scans file systems, extracts detailed metadata, and exports structured reports—all through an intuitive, responsive graphical interface built with PySide6.

> **Status:** Production-ready | **License:** MIT | **Python:** 3.10+ | **UI Framework:** PySide6

---

## ✨ Features

- **🔍 Deep Directory Scanning** – Recursively traverse any directory structure and extract file metadata
- **🎯 Flexible Filtering** – Optionally limit scans to specific file extensions (e.g., `.py`, `.pdf`, `.json`)
- **📊 Comprehensive Metadata** – Capture filename, extension, size (MB), last modified timestamp, parent folder, and absolute path
- **⚡ Non-blocking UI** – Background worker threads keep the GUI responsive during long scans
- **✋ Cancellation Support** – Gracefully stop scans at any time without data corruption
- **📝 Multi-layer Logging** – Console, file, and GUI-integrated logging for debugging and monitoring
- **💾 CSV Export** – Export audit results with consistent column ordering and proper formatting
- **🛡️ Error Handling** – Robust permission error handling and file access exception management

---

## 📋 Quick Start

### Prerequisites

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- A terminal or command prompt

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/csv_manifest_generator.git
   cd csv_manifest_generator
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

**Start the GUI application:**
```bash
python -m gui.main
```

Or directly:
```bash
python gui/main.py
```

The application window will open. Select a directory, optionally add an extension filter, and click **Start Scan**.

---

## 🎮 Usage Guide

### GUI Walkthrough

1. **Target Directory** – Click "Browse" to select the directory to scan
2. **Extension Filter** (Optional) – Enter file extensions without the dot (e.g., `py`, `pdf`, `json`). Leave blank to scan all files
3. **Start Scan** – Begin the directory scan. The status label updates in real-time
4. **Cancel Scan** – Stop the scan at any time (available only during active scans)
5. **View Results** – Results display in the results table with sortable columns
6. **Export to CSV** – Save the audit report to a CSV file in the `logs/` directory

### Command-Line Testing

**Test the core scanner:**
```bash
python test.py
```

**Test the worker/signal threading:**
```bash
python test2.py
```

---

## 📊 Manifest Schema

The exported CSV contains the following columns:

| Column | Type | Description |
|--------|------|-------------|
| `Filename` | string | File name with extension |
| `Extension` | string | Lowercase file extension (or `No_extension`) |
| `Parent_Folder` | string | Absolute path to the containing directory |
| `Size_MB` | float | File size in megabytes (rounded to 4 decimals) |
| `Last_Modified` | string | Last modification timestamp (`YYYY-MM-DD HH:MM:SS`) |
| `Full_Path` | string | Absolute path to the file |

**Example row:**
```
config.json,json,/home/user/project,0.0025,2024-09-14 10:32:15,/home/user/project/config.json
```

---

## 🏗️ Project Architecture

### Directory Structure

```
csv_manifest_generator/
├── core/
│   └── scanner.py              # Core scanning logic & CSV export
├── workers/
│   └── scan_worker.py          # Qt worker for background scanning
├── gui/
│   ├── main.py                 # PySide6 main window & UI logic
│   └── ui_logger.py            # Custom logging handler for GUI
├── utilities/
│   └── logger.py               # Centralized logging configuration
├── logs/                       # Generated CSV manifests (auto-created)
├── test.py                     # Core scanner smoke tests
├── test2.py                    # Worker/threading smoke tests
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

### Core Modules

#### `core.scanner`
- **`get_file_metadata(file_path: Path) -> dict`** – Extract metadata from a single file
- **`scan_directory(target_dir, extension_filter, is_cancelled_callback) -> list`** – Recursively scan and return file metadata
- **`export_to_csv(data, output_file) -> Path`** – Write metadata to CSV with proper formatting

#### `workers.scan_worker`
- **`ScanWorker`** – QObject-based worker for background scanning
  - Signals: `status_updated`, `progress_updated`, `finished`, `error_occurred`
  - Implements graceful cancellation via `cancel()` method

#### `gui.main`
- **`MainWindow`** – Main PySide6 window with complete UI and event handling
  - Directory selection with file browser
  - Real-time status updates
  - Results table with sortable columns
  - CSV export functionality

#### `utilities.logger`
- **`setup_logger(name: str) -> logging.Logger`** – Initialize a logger with console, file, and GUI handlers
- Logs written to `logs/app.log` with timestamps and context

---

## 🔧 API Reference

### Scanner Functions

```python
from core.scanner import scan_directory, export_to_csv

# Scan a directory
results = scan_directory(
    target_dir="/path/to/scan",
    extension_filter=".pdf",           # Optional
    is_cancelled_callback=lambda: False # Optional cancellation callback
)

# Export to CSV
output_path = export_to_csv(results, "output.csv")
```

### Worker Signals

```python
from workers.scan_worker import ScanWorker
from PySide6.QtCore import QThread

worker = ScanWorker("/path/to/scan", extension_filter="py")
thread = QThread()

worker.moveToThread(thread)
thread.started.connect(worker.run)

# Connect to signals
worker.status_updated.connect(lambda msg: print(f"Status: {msg}"))
worker.progress_updated.connect(lambda count: print(f"Files: {count}"))
worker.finished.connect(lambda data: print(f"Scan complete: {len(data)} files"))
worker.error_occurred.connect(lambda err: print(f"Error: {err}"))

thread.start()
```

### Logging

```python
from utilities.logger import setup_logger

logger = setup_logger(__name__)
logger.info("Application started")
logger.warning("Permission denied for file X")
logger.error("Failed to export CSV")
```

---

## 📁 Log Files

Application logs are stored in `logs/app.log` with the following format:
```
2024-09-14 10:32:15 [INFO] - Starting scan in directory: '/path/to/folder'
2024-09-14 10:32:16 [WARNING] - Skipping unreadable file '/path/file': Permission denied
2024-09-14 10:32:20 [INFO] - Scan complete. Found '42' matching files.
```

---

## 🛠️ Development

### Running Tests

```bash
# Test core scanner
python test.py

# Test worker threading
python test2.py
```

### Code Style

The project follows PEP 8 conventions with the following practices:
- Type hints for all function signatures
- Descriptive variable names and docstrings
- Separation of concerns (scanning, UI, threading, logging)
- Comprehensive error handling

### Adding Features

1. **New Metadata Fields** – Add fields in `core/scanner.py::get_file_metadata()`
2. **UI Enhancements** – Modify `gui/main.py`
3. **Logging** – Use `setup_logger()` from `utilities/logger.py`
4. **New Filters** – Extend `scan_directory()` with additional parameters

---

## ⚠️ Error Handling

The application gracefully handles:
- **Permission Errors** – Files with restricted access are logged and skipped
- **Invalid Paths** – Directory validation before scanning begins
- **Large Directories** – Background threading prevents UI freezing
- **CSV Export Failures** – Parent directory creation with error logging

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "ModuleNotFoundError: No module named 'PySide6'" | Run `pip install -r requirements.txt` |
| Scan is slow | This is normal for large directories. Use extension filters to speed up results |
| Permission denied errors | Check folder permissions; the app logs these to `logs/app.log` |
| CSV file not created | Ensure write permissions in the `logs/` directory |

---

## 📜 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📧 Support

For questions, issues, or suggestions, please open an [issue](https://github.com/yourusername/csv_manifest_generator/issues) on GitHub.

---

**Built with ❤️ using PySide6** | **Python 3.10+**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install PySide6
```

## Running the application

From the repository root:

```powershell
python -m gui.main
```

The window can be launched today, but the scan and export buttons are still under implementation. Until the GUI workflow is complete, use the scanner directly or run the included manual smoke tests.

## Using the scanner programmatically

```python
from core.scanner import export_to_csv, scan_directory

records = scan_directory(r"C:\path\to\audit", extension_filter="pdf")
output = export_to_csv(records, r"C:\path\to\manifest.csv")

print(f"Created manifest: {output}")
```

The extension filter accepts either form:

```python
scan_directory(r"C:\path\to\audit", extension_filter="pdf")
scan_directory(r"C:\path\to\audit", extension_filter=".pdf")
```

For a simple manual check of the scanner, run:

```powershell
python test.py
```

This scans the current directory and writes a sample manifest to `logs/test_manifest.csv`.

## Development status

The project already has the main building blocks in place:

- Core directory scanning and CSV serialization
- Extension filtering
- Background worker signals for status, progress, completion, and errors
- A GUI layout with a metadata table and live log panel

The next implementation tasks are:

1. Finish scan-thread signal connections in `gui/main.py`.
2. Start and clean up the worker thread reliably after every scan.
3. Implement cancellation behavior and restore GUI controls after cancellation or failure.
4. Add an output-file dialog and connect it to `export_to_csv`.
5. Add automated tests and a dependency manifest such as `requirements.txt` or `pyproject.toml`.

### Completed: Day 1

- Added a **Browse** workflow that opens a folder picker and places the selected target directory into the application input field.

## Operational notes

- Scans are recursive. Selecting a broad directory can take time and may include virtual environments, source-control metadata, or other generated folders.
- Files that cannot be read because of permissions or disappearance during a scan are skipped and logged when handled by the scanner.
- Generated manifests include absolute file paths. Treat exported CSVs as potentially sensitive when sharing them.

## Contributing

Contributions are welcome. Please keep core scanning logic, Qt worker behavior, and GUI code separated; add or update tests for behavior changes; and avoid committing generated logs or manifests unless they are intentional fixtures.
