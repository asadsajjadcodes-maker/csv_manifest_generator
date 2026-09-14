import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QTextEdit, QFileDialog, QMessageBox, QHeaderView
)
from PySide6.QtCore import QThread, Slot

# Import project-level logger setup, worker, logger handler, and CSV exporter
from utilities.logger import setup_logger, gui_handler
from core.scanner import export_to_csv
from workers.scan_worker import ScanWorker


# Initialize module-level logger instance
logger = setup_logger(__name__)


class MainWindow(QMainWindow):
    """
    Main application window that manages the PySide6 user interface,
    controls background worker thread execution, and displays results.
    """
    def __init__(self):
        super().__init__()
        # Configure primary window properties
        self.setWindowTitle("CSV Manifest Generator")
        self.resize(900, 650)

        # In-memory storage for scanned file metadata dictionaries
        self.scanned_data = []

        # Thread management variables to hold background execution objects
        self.scan_thread = None
        self.scan_worker = None

        # Build and layout all visual components
        self.init_ui()
        
       
        

    def init_ui(self):
        """Creates and organizes GUI layouts and widgets."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Directory Selection Row ---
        folder_layout = QHBoxLayout()
        folder_label = QLabel("Target Directory:")
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Select directory to scan...")
        browse_btn = QPushButton("Browse")
        
        # Connect browse button to file dialog modal
        browse_btn.clicked.connect(self.browse_directory)

        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(browse_btn)
        main_layout.addLayout(folder_layout)

        # --- File Extension Filter Row ---
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Extension Filter (Optional):")
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("e.g. py, png, json (Leave blank for all files)")
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_input)
        main_layout.addLayout(filter_layout)

        # --- Control Action Buttons ---
        btn_layout = QHBoxLayout()
        self.scan_btn = QPushButton("Start Scan")
        self.scan_btn.clicked.connect(self.start_scan)
        
        self.cancel_btn = QPushButton("Cancel Scan")
        self.cancel_btn.setEnabled(False) # Disabled by default until scan starts
        self.cancel_btn.clicked.connect(self.cancel_scan)

        self.export_btn = QPushButton("Export to CSV")
        self.export_btn.setEnabled(False) # Disabled until results are available
        self.export_btn.clicked.connect(self.export_csv)

        btn_layout.addWidget(self.scan_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.export_btn)
        main_layout.addLayout(btn_layout)

        # --- Real-time Operation Status Label ---
        self.status_label = QLabel("Status: Idle")
        main_layout.addWidget(self.status_label)

        # --- Metadata Results Table ---
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Filename", "Extension", "Parent Folder", "Size (MB)", "Last Modified", "Full Path"
        ])
        # Auto-adjust column width based on text content
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        main_layout.addWidget(self.results_table)

        # --- Interactive Logging Console Output Widget ---
        log_label = QLabel("Application Logs:")
        main_layout.addWidget(log_label)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True) # Prevent user editing inside log view
        self.log_output.setMaximumHeight(150)
        main_layout.addWidget(self.log_output)

        gui_handler.log_message.connect(self.show_log)
        logger.info("tripple logging is working")

    

    
    def show_log(self, message: str):
        self.log_output.append(message)
        

    def browse_directory(self):
        # opens file selection window  
        selected_folder = QFileDialog.getExistingDirectory(
            self,
            "Choose a folder to scan"
        )

        # if user selects the folder 
        if selected_folder:
            self.folder_input.setText(selected_folder) # put the selected folder path in the folder input line


    def start_scan(self):
       target_path_str = self.folder_input.text().strip() # takes the text from inside the QLineEdit

       # Check if the input box is empty
       if not target_path_str:
           QMessageBox.warning(self, "Input Error", "Please select a directory to scan") # pop up warning
           return

       target_path = Path(target_path_str)
       if not target_path.exists() or not target_path.is_dir():
           QMessageBox.critical(self, "Path Error", f"The directory does not exist: \n{target_path}")
           return
       
       # Clear old data and set button states before starting scan. 
       self.scanned_data.clear()
       self.results_table.setRowCount(0)
       self.scan_btn.setEnabled(False)
       self.cancel_btn.setEnabled(True)
       self.export_btn.setEnabled(False)

       ext_filter = self.filter_input.text().strip() or None

       # Instantiate background thread and worker instance 
       self.scan_thread = QThread()
       self.scan_worker = ScanWorker(target_path, extension_filter=ext_filter)

       # Move worker thread to background to keep UI responsive.
       self.scan_worker.moveToThread(self.scan_thread)

       # Connect thread startup signal to worker entry method
       self.scan_thread.started.connect(self.scan_worker.run) # this will call the run method of the ScanWorker class when the thread starts


       # Connect worker signals to GUI update slots for real-time feedback
       self.scan_worker.status_updated.connect(self.update_status)
       self.scan_worker.progress_updated.connect(self.update_status)
       self.scan_worker.finished.connect(self.on_scan_finished)
       self.scan_worker.error_occurred.connect(self.on_scan_error)

       # Connect worker completion signals to thread cleanup methods to avoid memory leaks 
       self.scan_worker.finished.connect(self.scan_thread.quit) # QThread.quit() will stop the thread's event loop and allow it to finish gracefully
       self.scan_worker.finished.connect(self.scan_worker.deleteLater) # deleteLater() will schedule the worker object for deletion once all pending events have been processed
       self.scan_worker.finished.connect(self.scan_thread.deleteLater) # deleteLater() will schedule the thread object for deletion once all pending events have been processed

       # Start non-blocking thread execution.
       self.scan_thread.start() # This will trigger the run() method of the ScanWorker in a separate thread, allowing the GUI to remain responsive during the scan process.

    
    def cancel_scan(self):
       if self.scan_worker:
           self.scan_worker.cancel()
           self.cancel_btn.setEnabled(False)

    @Slot(str)
    def update_status(self, text: str):
        self.status_label.setText(f"Status: {text}")

    @Slot(int)
    def update_progress(self, count: int):
        self.status_label.setText(f"Status : Scanning..... indexed '{count}' files.")

    @Slot(list)
    def on_scan_finished(self, results: list):
        self.scanned_data = results
        self.populate_table(results)

        self.scan_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.export_btn.setEnabled(len(results) > 0)

        self.status_label.setText(f"Status: Scan completed.  '{len(results)}' files indexed.")

    @Slot(str)
    def on_scan_error(self, err_msg: str):
        self.scan_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)

        self.status_label.setText("Status: Error occured during the scan.")

        QMessageBox.critical(
            self,
            "Execution Error",
            f"Scan failed with error.. \n{err_msg}"
        )

    @Slot(list)
    def populate_table(self, data: list):
        """Populates QTableWidget with metadata extracted from files."""
        self.results_table.setRowCount(len(data)) # Create rows accourding to the len of the data 

        for row_idx, row_data in enumerate(data):
            self.results_table.setItem(row_idx, 0, QTableWidgetItem(str(row_data.get("Filename", ""))))
            self.results_table.setItem(row_idx, 1, QTableWidgetItem(str(row_data.get("Extension", ""))))
            self.results_table.setItem(row_idx, 2, QTableWidgetItem(str(row_data.get("Parent_Folder", ""))))
            self.results_table.setItem(row_idx, 3, QTableWidgetItem(str(row_data.get("Size_MB", ""))))
            self.results_table.setItem(row_idx, 4, QTableWidgetItem(str(row_data.get("Last_Modified", ""))))
            self.results_table.setItem(row_idx, 5, QTableWidgetItem(str(row_data.get("Full_Path", ""))))


    def export_csv(self):
        if not self.scanned_data:
            QMessageBox.warning(
                self,
                "Export Error",
                "No scanned data available to export"
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Manifest CSV",
            "manifest.csv",
            "CSV Files (*.csv)"

        )


        if file_path:
            try:
                out_file = export_to_csv(self.scanned_data, file_path)
                QMessageBox.information(
                       self,
                                "Export Successful",
                                f"Csv file saved to: \n {out_file}"
                            )

            except Exception as e:
                logger.exception(f"Failed to export csv file : {e}")
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    f"Failed to export csv file to : \n {e}"
                )



       


def main():
    """Main program entry point."""
    

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()