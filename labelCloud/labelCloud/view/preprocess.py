import logging
from PyQt5.QtWidgets import QMainWindow, QPushButton, QFileDialog, QTextEdit, QLineEdit, QMessageBox
from PyQt5 import uic
from PyQt5.QtCore import QSize, QSettings
import platform
import sys
from pathlib import Path
import os


from tools.batch_preprocess import DataPreprocessor


class PreprocessController:
    def __init__(self):
        self.view = None

    def startup(self, view):
        """Sets the view and initializes the controller."""
        self.view = view
        self.setup_connections()

    def setup_connections(self):
        """Connect buttons and other widgets to their handlers."""
        
        start_button = self.view.findChild(QPushButton, 'button_start')
        finish_button = self.view.findChild(QPushButton, 'button_finish')
        cancel_button = self.view.findChild(QPushButton, 'button_cancel')
        
        raw_data_button = self.view.findChild(QPushButton, 'button_browse_raw_data')
        label_files_button = self.view.findChild(QPushButton, 'button_browse_label_files')
       

        raw_data_input = self.view.findChild(QLineEdit, 'lineEdit_raw_data')
        label_files_input = self.view.findChild(QLineEdit, 'lineEdit_label_files')
       
        
        self.log_output = self.view.findChild(QTextEdit, 'textEdit_log')
        self.log_output.setReadOnly(True)

        if start_button:
            start_button.clicked.connect(lambda: self.start_preprocessing(raw_data_input.text(), label_files_input.text()))
        if cancel_button:
            cancel_button.clicked.connect(self.cancel_preprocessing)
        if finish_button:
            finish_button.clicked.connect(self.finish_preprocessing)
            
        # Connect browse buttons
        if raw_data_button:
            raw_data_button.clicked.connect(lambda: self.browse_folder(raw_data_input))
        if label_files_button:
            label_files_button.clicked.connect(lambda: self.browse_folder(label_files_input))
      
    
    def browse_folder(self, line_edit):
        """Open a dialog to select a folder and set the selected path in the given QLineEdit."""
        folder = QFileDialog.getExistingDirectory(self.view, "Select Folder")
        if folder:
            line_edit.setText(folder)
            
    def start_preprocessing(self, raw_data_folder, label_files_folder):
        # Check for validity of raw_data_folder
        if not raw_data_folder or not os.path.isdir(raw_data_folder):
            QMessageBox.critical(
                self.view,
                "Invalid Input Directory",
                "The specified raw data folder is invalid or does not exist.",
                QMessageBox.Ok
            )
            return  # Exit the function if the folder is invalid
            
        # Check for validity of label_files_folder
        if not label_files_folder or not os.path.isdir(label_files_folder):
            QMessageBox.critical(
                self.view,
                "Invalid Label Directory",
                "The specified label files folder is invalid or does not exist.",
                QMessageBox.Ok
            )
            return  # Exit the function if the folder is invalid
            
       
            
       
        self.log_output.clear()
        self.log_output.append("Starting preprocessing...")
        self.log_output.append(f"Raw data folder: {raw_data_folder}")
        self.log_output.append(f"Label files folder: {label_files_folder}")
        

        self.thread = DataPreprocessor(raw_data_folder, label_files_folder)
        self.thread.progress.connect(self.update_progress)
        self.thread.start()

    def update_progress(self, message):
        self.log_output.append(message)
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())  # Scroll to bottom  
    
    def cancel_preprocessing(self):
        logging.info("Cancelling preprocessing...")
        if hasattr(self, 'thread'):
            self.thread.stop()
        self.log_output.append("Preprocessing cancelled.")
        self.view.close()

    def finish_preprocessing(self):
        logging.info("Finishing preprocessing...")
        # Add logic to finalize preprocessing
        self.view.close()

class PreprocessWindow(QMainWindow):
    def __init__(self, control: PreprocessController):
        super(PreprocessWindow, self).__init__()
        ui_path = self._get_ui_path("preprocess_interface.ui")
        uic.loadUi(ui_path, self)
        self.setWindowTitle("Point Cloud Preprocessing Module")
        self.setMinimumSize(QSize(500, 500))

        self.controller = control

        # Apply dark mode stylesheet if in dark mode
        if self.is_dark_mode():
            self.apply_dark_mode_stylesheet()

        # Connect with controller
        self.controller.startup(self)

    def _get_ui_path(self, ui_filename):
        """Get the path to the UI file, considering whether running in PyInstaller bundle or not."""
        if getattr(sys, 'frozen', False):
            # Running in a PyInstaller bundle
            base_path = Path(sys._MEIPASS)
        else:
            # Running in a development environment
            base_path = Path(__file__).resolve().parent.parent
        
        return base_path / "resources" / "interfaces" / ui_filename
            
    def apply_dark_mode_stylesheet(self):
        dark_mode_stylesheet = """
        QMainWindow {
            background-color: #2E2E2E;
            color: white;
        }
        QLabel {
            color: white;
        }
        QLineEdit {
            background-color: #3E3E3E;
            color: white;
            border: 1px solid #5E5E5E;
        }
        QPushButton {
            background-color: #4E4E4E;
            color: white;
            border: 1px solid #6E6E6E;
        }
        QComboBox {
            background-color: #3E3E3E;
            color: white;
            border: 1px solid #5E5E5E;
        }
        """
        self.setStyleSheet(dark_mode_stylesheet)

    def is_dark_mode(self):
        if platform.system() == "Darwin":  # macOS
            os_theme = QSettings().value("AppleInterfaceStyle", "Light")
            return os_theme == "Dark"
        return False

    def closeEvent(self, event) -> None:
        logging.info("Closing window...")
        self.controller.cancel_preprocessing()  # Ensure preprocessing is stopped
        event.accept()
