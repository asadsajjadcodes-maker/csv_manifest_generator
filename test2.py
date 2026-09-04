import sys
import logging
from pathlib import Path
from PySide6.QtCore import QCoreApplication, QThread
from workers.scan_worker import ScanWorker

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def handle_status(message: str):
    print(f"[THREAD SIGNAL -> STATUS]: {message}")


def handle_progress(count: int):
    print(f"[THREAD SIGNAL -> PROGRESS]: {count} files processed")


def handle_results(data: list):
    print(f"\n[THREAD SIGNAL -> FINISHED]: Received {len(data)} total records!")
    if data:
        print(f"Sample First Record: {data[0]['Filename']} | Size: {data[0]['Size_MB']} MB")
    
    # Exit event loop upon completion
    QCoreApplication.quit()


def handle_error(err_msg: str):
    print(f"[THREAD SIGNAL -> ERROR]: {err_msg}")
    QCoreApplication.quit()


def main():
    # QCoreApplication handles event loop without launching GUI graphics
    app = QCoreApplication(sys.argv)
    
    target_folder = Path.cwd()
    print(f"\n--- Testing Day 2 QThread Worker on: {target_folder} ---\n")

    # 1. Instantiate Thread and Worker
    thread = QThread()
    worker = ScanWorker(target_dir=target_folder)

    # 2. Move Worker to QThread
    worker.moveToThread(thread)

    # 3. Connect Signals and Slots
    thread.started.connect(worker.run)
    worker.status_updated.connect(handle_status)
    worker.progress_updated.connect(handle_progress)
    worker.finished.connect(handle_results)
    worker.error_occurred.connect(handle_error)

    # Clean up thread resources on completion
    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)

    # 4. Start Thread Event Loop
    thread.start()

    sys.exit(app.exec())



main()