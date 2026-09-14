# CSV Manifest Generator

A desktop file-system auditing and inventory tool built with **Python** and **PySide6**.

CSV Manifest Generator recursively scans a selected directory, collects useful file metadata, presents the results in a responsive desktop interface, and exports the collected inventory to a structured CSV manifest.

It is designed as a practical automation utility as well as a clean example of separating **core file-system logic**, **background execution**, **GUI presentation**, and **logging**.

## Overview

Managing large directories manually makes it difficult to answer simple questions:

* What files are actually inside this directory tree?
* Which file types are present?
* How large are the files?
* Where are they located?
* When were they last modified?
* Can the inventory be exported into a format that can be searched, filtered, or processed elsewhere?

This application automates that workflow.

The application follows a simple pipeline:

```text
Select Directory
       ↓
Validate Input
       ↓
Recursive Scan
       ↓
Apply Extension Filter
       ↓
Extract File Metadata
       ↓
Display Results in GUI
       ↓
Export CSV Manifest
```

For larger directory trees, the scan runs through a background `QThread`, keeping the PySide6 interface responsive while the file system is being inspected.

## Key Features

### Recursive file-system scanning

Scans a target directory recursively using Python's `pathlib` and discovers files throughout nested folders.

### Extension filtering

The scanner can process every file or restrict the scan to a specific extension such as:

```text
py
pdf
json
png
```

The scanner normalizes the filter so both `pdf` and `.pdf` are accepted.

### File metadata extraction

Each successfully inspected file produces a structured metadata record containing:

| Field           | Description                                            |
| --------------- | ------------------------------------------------------ |
| `Filename`      | File name including extension                          |
| `Extension`     | Lowercase extension, or `No_extension`                 |
| `Parent_Folder` | Absolute path to the containing directory              |
| `Size_MB`       | File size in megabytes, rounded to four decimal places |
| `Last_Modified` | Last modification time as `YYYY-MM-DD HH:MM:SS`        |
| `Full_Path`     | Absolute path to the file                              |

### Responsive PySide6 interface

The GUI provides:

* Directory selection through a folder browser
* Optional extension filtering
* Start Scan control
* Cancel Scan control
* Results table for discovered files
* Live status updates
* Integrated application log output
* CSV export through a save-file dialog

### Background scanning

The GUI uses a `ScanWorker` object moved to a `QThread` so the potentially slow file-system operation does not run directly on the main GUI thread.

The worker communicates with the interface through Qt signals for:

* Status updates
* Progress updates
* Completed scan results
* Errors

### Cancellation support

The worker maintains a cancellation flag that is checked during scanning. When cancellation is requested, the scanner stops processing additional paths and records the cancellation event through the logging system.

### Multi-layer logging

Logging is centralized and routed to three destinations:

```text
Application code
      ├── Console handler
      ├── File handler → logs/app.log
      └── GUI handler → PySide6 log panel
```

This makes runtime activity visible both to the user and to the developer.

### CSV export

Scan results are exported with a stable column order using Python's `csv.DictWriter`.

Parent directories for the requested output file are created automatically when necessary.

### Error handling

The scanner handles common file-system problems such as:

* Invalid target directories
* Permission errors
* Files disappearing during a scan
* CSV export failures

Unreadable files are logged and skipped rather than terminating the entire scan.

## Technology Stack

| Technology                     | Purpose                                    |
| ------------------------------ | ------------------------------------------ |
| **Python 3.10+**               | Application language                       |
| **PySide6**                    | Desktop GUI and Qt integration             |
| **pathlib**                    | File-system traversal and path management  |
| **csv**                        | CSV manifest generation                    |
| **logging**                    | Application and diagnostic logging         |
| **QThread / QObject / Signal** | Background execution and GUI communication |

The project uses only the Python standard library plus **PySide6** for the desktop interface.

## Project Structure

```text
csv_manifest_generator/
│
├── core/
│   └── scanner.py
│       ├── get_file_metadata()
│       ├── scan_directory()
│       └── export_to_csv()
│
├── workers/
│   └── scan_worker.py
│       └── ScanWorker
│
├── gui/
│   ├── main.py
│   │   └── MainWindow
│   │
│   └── ui_logger.py
│       └── GuiHandler
│
├── utilities/
│   └── logger.py
│       └── setup_logger()
│
├── logs/
│   └── Generated logs and test/output artifacts
│
├── manifest.csv
├── requirements.txt
├── test.py
├── test2.py
├── .gitignore
└── README.md
```

## Architecture

The project is intentionally divided by responsibility.

### 1. Core scanner

`core/scanner.py` contains the application-independent file-system logic.

Its main responsibilities are:

```text
get_file_metadata()
        ↓
scan_directory()
        ↓
export_to_csv()
```

`get_file_metadata()` inspects one file and converts its native file-system information into a dictionary.

`scan_directory()` validates the target directory, recursively walks it, optionally filters by extension, collects metadata, and returns a list of dictionaries.

`export_to_csv()` takes those dictionaries and serializes them into a predictable CSV structure.

### 2. Background worker

`workers/scan_worker.py` contains `ScanWorker`, a `QObject` designed to run inside a `QThread`.

The worker owns the long-running scan operation while the GUI remains responsible for presentation and user interaction.

This separation prevents the interface from being tightly coupled to the scanning implementation.

### 3. GUI layer

`gui/main.py` contains the main PySide6 window and connects the user interface to the worker and core scanner.

The main window handles:

* Input validation
* Folder selection
* Worker/thread creation
* Signal connections
* Table population
* Status messages
* Cancellation requests
* CSV export

### 4. GUI logging bridge

`gui/ui_logger.py` provides `GuiHandler`, a custom logging handler that converts normal Python log records into a Qt signal.

That allows the same logging system to feed the desktop log panel without duplicating logging logic.

### 5. Centralized logging

`utilities/logger.py` configures application loggers and attaches console, file, and GUI handlers.

The file logger writes detailed diagnostic information to:

```text
logs/app.log
```

## Installation

### Requirements

* Python 3.10 or newer
* `pip`
* A supported desktop environment for PySide6

### Clone the repository

```bash
git clone https://github.com/asadsajjadcodes-maker/csv_manifest_generator.git
cd csv_manifest_generator
```

### Create a virtual environment

#### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Run the Application

From the repository root:

```bash
python -m gui.main
```

The application opens a desktop window where you can select a directory, optionally specify a file extension, run the scan, review the results, and export the manifest.

You can also launch the module directly:

```bash
python gui/main.py
```

## Using the Application

### 1. Choose a directory

Click **Browse** and select the directory that should be audited.

### 2. Add an optional extension filter

Examples:

```text
py
pdf
json
```

Leave the field empty to include all files.

### 3. Start the scan

Click **Start Scan**.

The scanner recursively inspects the selected directory and the GUI updates its status while the worker is running in the background.

### 4. Review the manifest

Discovered files appear in the results table with their metadata.

### 5. Export the report

Click **Export to CSV**, choose the output location, and save the manifest.

## Programmatic Usage

The core scanner can also be used without the GUI.

### Scan a directory

```python
from core.scanner import scan_directory

records = scan_directory(
    target_dir="/path/to/project",
    extension_filter="pdf",
)

for record in records:
    print(record)
```

### Export scan results

```python
from core.scanner import export_to_csv, scan_directory

records = scan_directory("/path/to/project")
output = export_to_csv(records, "output/manifest.csv")

print(f"Created manifest: {output}")
```

### Extension filter behavior

Both forms are accepted:

```python
scan_directory("/path/to/project", extension_filter="pdf")
scan_directory("/path/to/project", extension_filter=".pdf")
```

## CSV Manifest Example

A generated manifest follows a predictable schema:

```csv
Filename,Extension,Parent_Folder,Size_MB,Last_Modified,Full_Path
config.json,.json,/home/user/project,0.0025,2026-09-14 10:32:15,/home/user/project/config.json
```

This structure makes the exported report convenient for:

* Spreadsheet inspection
* Data analysis
* File inventory workflows
* Automation pipelines
* Archival and auditing tasks

## Logging

Application logs are written to:

```text
logs/app.log
```

The logging system provides three views of the same application activity:

| Destination    | Purpose                      |
| -------------- | ---------------------------- |
| Console        | Developer/runtime visibility |
| `logs/app.log` | Persistent diagnostics       |
| GUI log panel  | User-facing live feedback    |

Example log messages include scan start/completion events, skipped unreadable files, and export failures.

## Testing and Verification

The repository includes two manual smoke-test scripts.

### Core scanner test

```bash
python test.py
```

This exercises the scanner and CSV generation path.

### Worker/thread test

```bash
python test2.py
```

This exercises the worker and Qt signal flow used for background execution.

For production expansion, these scripts can serve as a starting point for a more formal automated test suite.

## Design Principles

This project follows several practical software-engineering principles:

### Separation of concerns

File-system logic, background execution, GUI behavior, and logging are separated into different modules.

### Reusable core logic

The scanner does not depend on the GUI. The same scanning and export functions can be imported and used from another Python program.

### Type-aware interfaces

Function signatures use modern Python type hints such as `Path`, `Optional`, lists, dictionaries, and unions.

### Non-blocking desktop UX

Long-running I/O work is moved away from the GUI event loop rather than performing the scan directly inside a button callback.

### Defensive file handling

Individual file failures are handled locally so a single inaccessible or missing file does not necessarily abort an entire directory audit.

## Operational and Privacy Notes

Scanning is recursive. Selecting a very broad directory can significantly increase the number of files processed and may include folders such as virtual environments, source-control metadata, caches, or generated output.

The generated manifest contains **absolute file paths**. Treat exported CSV files and application logs as potentially sensitive when sharing them with other people or publishing them online.

## Typical Use Cases

CSV Manifest Generator is useful for:

* File-system auditing
* Digital asset inventories
* Project directory inspection
* Backup preparation
* Document and media inventory
* Data-cleanup workflows
* Migration planning
* Automation and pipeline tooling

## Why This Project Matters

This project demonstrates more than basic file handling. It combines several real-world desktop-automation concepts into one application:

```text
Python file-system programming
        +
Structured data extraction
        +
CSV serialization
        +
Desktop GUI development
        +
Background threading
        +
Signal-based communication
        +
Logging and diagnostics
        +
Error handling
        ↓
Practical automation software
```

It is a compact example of how a Python script can evolve into a reusable desktop tool with a clear internal architecture.

## Repository

GitHub: https://github.com/asadsajjadcodes-maker/csv_manifest_generator

## Author

**Asad Sajjad**

Python developer focused on automation, desktop tooling, and production-oriented development workflows.
