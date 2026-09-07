import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QFileDialog,
    QMessageBox,
    QHeaderView
)
# For multithreading and receiving signals.
from PySide6.QtCore import QThread, Slot

from utilities.logger import setup_logger
from core.scanner import export_to_csv
from workers.scan_worker import ScanWorker
from utilities.logger import setup_logger

# Initialize logger instance.
logger = setup_logger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Configure primary window properties.
        self.setWindowTitle("CSV Manifest Generator")
        self.resize(900, 650)

        # In-memory storage for scanned file metadata dictionaries.
        self.scanned_data = []

        # Thread management variables to hold background execution objects.
        self.scan_thread = None
        self.scan_worker = None

        # Build and layout all visual components.
        self.init_ui()

        # Connect custom GuiHandler to the log display widget.
        self.attach_gui_logger()

#===========================================================================================

    def init_ui(self):
        """ Creates and organizes GUI layouts and widgets."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # ------Directory selection------
        folder_layout = QHBoxLayout()
        folder_label = QLabel("Select Directory:")
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Click 'Browse' to select a folder.")
        folder_btn = QPushButton("Browse")

        # Connect Browse button.
        folder_btn.clicked.connect(self.browse_directory)


        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(folder_btn)
        main_layout.addLayout(folder_layout)

        # ------File extension filter------
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Select Extension (Optional):")
        self.filter_input = QLineEdit()
        self.folder_input.setPlaceholderText("e.g: py, jpg, json. (Leave blank for all files)")


        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_input)
        main_layout.addLayout(filter_layout)

        #------Control action buttons------
        button_layout = QHBoxLayout()
        self.scan_button = QPushButton("Start Scan")
        self.scan_button.clicked.connect(self.start_scan)

        self.cancel_button = QPushButton("Cansel Scan")
        self.cancel_button.setEnabled(False) # Set disabled utill scan starts.
        self.cancel_button.clicked.connect(self.cancel_scan)

        self.export_button = QPushButton("Export to CSV")
        self.export_button.setEnabled(False)  # Set Disabled utill results are available.
        self.export_button.clicked.connect(self.export_csv)


        button_layout.addWidget(self.scan_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.export_button)
        main_layout.addLayout(button_layout)

        # ----Real time operation status label----
        self.status_label = QLabel("Status: Idle")
        main_layout.addWidget(self.status_label)

        

