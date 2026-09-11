# CSV Manifest Generator

CSV Manifest Generator is a Python desktop project for auditing directory trees and producing structured CSV inventories of the files they contain. It is built with PySide6 and separates the scanning, background-work, logging, and user-interface layers so the application can evolve into a responsive file-auditing tool.

> **Project status:** Active development. The scanning and CSV-export modules are implemented, and the GUI can now select a target folder. Scan lifecycle wiring, cancellation handling, and export interaction are still being completed. See [Development status](#development-status).

## What it does

- Recursively scans a selected directory.
- Optionally limits results to one file extension.
- Captures a file's name, extension, parent folder, size, last-modified timestamp, and absolute path.
- Writes the collected metadata to a CSV file with a consistent column order.
- Uses a `QThread` worker design so scans can run outside the GUI thread.
- Routes application logs to both the console/file logger and the GUI log panel.

## Manifest schema

| Column | Description |
| --- | --- |
| `Filename` | File name, including its extension. |
| `Extension` | Lowercase suffix such as `.pdf`; files with no suffix use `No_extension`. |
| `Parent_Folder` | Absolute path of the file's containing directory. |
| `Size_MB` | File size in megabytes. |
| `Last_Modified` | Local last-modified timestamp in `YYYY-MM-DD HH:MM:SS` format. |
| `Full_Path` | Absolute path to the file. |

## Project structure

```text
csv_manifest_generator/
├── core/
│   └── scanner.py          # Metadata extraction, directory scan, and CSV export
├── workers/
│   └── scan_worker.py      # Background Qt worker and progress signals
├── gui/
│   ├── main.py             # Main PySide6 window
│   └── ui_logger.py        # Logging handler for the GUI console
├── utilities/
│   └── logger.py           # Console, file, and GUI logging configuration
├── logs/                   # Generated sample manifests
├── test.py                 # Manual scanner smoke test
└── test2.py                # Manual worker/signal smoke test
```

## Requirements

- Python 3.10 or later
- [PySide6](https://doc.qt.io/qtforpython-6/)

Create a virtual environment and install the UI dependency:

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
