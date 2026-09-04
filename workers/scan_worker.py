from utilities.logger import setup_logger
from pathlib import Path
from core.scanner import scan_directory, export_to_csv, get_file_metadata
from PySide6.QtCore import QObject, Signal, Slot
from typing import List, Dict, Optional, Any

# setup logging 
logger = setup_logger(__name__)

class ScanWorker(QObject):
    """
    Background worker that runs directory scanning on a saparate QThread.
    Emits signals to communicate progress and results safely to the UI.
    """
    # Signals for cross thread communication 
    status_updated = Signal(str)     # Current operation status
    progress_updated = Signal(int)   # Number of processed files
    finished = Signal(list)         # Metadata results
    error_occurred = Signal(str)     # Error message


    def __init__(self, target_dir: str | Path, extension_filter: Optional[str] = None):
        super().__init__()
        self.target_dir = Path(target_dir).resolve()
        self.extension_filter = extension_filter
        self._is_cancelled = False

    @Slot()
    def run(self):
        # Execute the file system scan on the background thread.

        try:
            if not self.target_dir.exists() and not self.target_dir.is_dir():
                self.error_occurred.emit(f"Invalid directory path: {self.target_dir}")
                return

            self.status_updated.emit(f"Starting scan in : {self.target_dir}")

            # Normalize extension filter 
            target_ext = self.extension_filter.lower().strip() if self.extension_filter else None
            # make extension lower and remove spaces from start and end if extension is given else None 

            if target_ext and not target_ext.startswith("."):
                target_ext = f".{target_ext}"

            manifest_data : List[Dict[str, Any]] = []
            file_count = 0

            for path in self.target_dir.rglob("*"):
                if self._is_cancelled:
                    self.status_updated.emit("Scan cancelled by user.")
                    break

                if path.is_file():
                    if target_ext and path.suffix.lower() != target_ext:
                        continue
                    metadata = get_file_metadata(path)
                    if metadata:
                        manifest_data.append(metadata)
                        file_count += 1


                        # Emit status update every 50 files to keep gui responsive without spamming
                        if file_count % 50 == 0:
                            self.progress_updated.emit(file_count)
                            self.status_updated.emit(f"Scanned {file_count} files.......")


            if not self._is_cancelled:
                self.progress_updated.emit(file_count)
                self.status_updated.emit(f"Completed! Total files indexed: {len(manifest_data)}")
                self.finished.emit(manifest_data)

        except Exception as err:
            logger.exception("Unexpected error during thread scan execution.")
            self.error_occurred.emit(str(err))

    def cancel(self):
        # Flag the worker thread to stop scanning gracefully.
        self._is_cancelled = True