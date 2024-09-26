import logging
from PyQt5.QtWidgets import QMainWindow, QPushButton, QTextEdit,  QLineEdit, QFileDialog, QMessageBox, QProgressBar

from PyQt5 import uic
from PyQt5.QtCore import QSize, QSettings, QTimer
import pkg_resources
import platform
import sys
from pathlib import Path
from tools.batch_augment import AugmentationThread
import os

class AugmentationController:
    def __init__(self):
        self.view = None
        self.augmentation_thread = None
        self.timer = None

    def startup(self, view):
        """Sets the view and initializes the controller."""
        self.view = view
        self.setup_connections()

    def setup_connections(self):
        """Connect buttons and other widgets to their handlers."""
        start_button = self.view.findChild(QPushButton, 'button_start')
        cancel_button = self.view.findChild(QPushButton, 'button_cancel')
        
        self.log_output = self.view.findChild(QTextEdit, 'textEdit_progress')
        self.log_output.setReadOnly(True)
        
        self.ply_dir_edit = self.view.findChild(QLineEdit, 'lineEdit_ply_dir')
        self.label_dir_edit = self.view.findChild(QLineEdit, 'lineEdit_label_dir')

        browse_ply_button = self.view.findChild(QPushButton, 'button_browse_ply')
        browse_label_button = self.view.findChild(QPushButton, 'button_browse_label')
        
        #self.progress_bar = self.view.findChild(QProgressBar, 'progressBar')
        #self.progress_bar.setRange(0, 0) 
        


        if start_button:
            start_button.clicked.connect(self.start_augmentation)
        if cancel_button:
            cancel_button.clicked.connect(self.cancel_augmentation)
        if browse_ply_button:
            browse_ply_button.clicked.connect(self.browse_ply_directory)
        if browse_label_button:
            browse_label_button.clicked.connect(self.browse_label_directory)

    def start_augmentation(self):
        logging.info("Starting augmentation...")
        self.log_output.clear()  # Clear previous logs
  
        ply_directory = self.ply_dir_edit.text()
        label_directory = self.label_dir_edit.text()
        
        # Check if directories exist and are not empty
        if not os.path.exists(ply_directory) or not os.path.isdir(ply_directory):
            QMessageBox.critical(self.view, "Error", "PLY Directory does not exist or is not a directory.")
            return
        if not os.listdir(ply_directory):
            QMessageBox.critical(self.view, "Error", "PLY Directory is empty.")
            return
            
        # Check for existing augmented files
        for filename in os.listdir(ply_directory):
            if "augmented" in filename:
                QMessageBox.critical(self.view, "Error", "Augmentation has already been done. Please check the PLY directory.")
                return
        
        if not os.path.exists(label_directory) or not os.path.isdir(label_directory):
            QMessageBox.critical(self.view, "Error", "Label Directory does not exist or is not a directory.")
            return
        if not os.listdir(label_directory):
            QMessageBox.critical(self.view, "Error", "Label Directory is empty.")
            return
        
        # Log the directories for debugging
        logging.info(f"PLY Directory: {ply_directory}")
        logging.info(f"Label Directory: {label_directory}")
        

        # Create and start the augmentation thread
        self.augmentation_thread = AugmentationThread(ply_directory, label_directory)
        self.augmentation_thread.progress_signal.connect(self.update_log_output)
        self.augmentation_thread.error_signal.connect(self.show_error_message)
        self.augmentation_thread.finished.connect(self.on_augmentation_finished)
        
        # Start the progress bar timer
        self.start_progress_bar()

        # Start the thread
        self.augmentation_thread.start()
        
        
        
    def browse_ply_directory(self):
        """Open a dialog to select the PLY directory."""
        directory = QFileDialog.getExistingDirectory(self.view, "Select PLY Directory")
        if directory:
            self.ply_dir_edit.setText(directory)
            logging.info(f"Selected PLY Directory: {directory}")

    def browse_label_directory(self):
        """Open a dialog to select the label directory."""
        directory = QFileDialog.getExistingDirectory(self.view, "Select Label Directory")
        if directory:
            self.label_dir_edit.setText(directory)
            logging.info(f"Selected Label Directory: {directory}")
            
    def start_progress_bar(self):
        """Start the timer for the indeterminate progress bar."""
        self.view.findChild(QProgressBar, 'progressBar').setRange(0, 0)  # Indeterminate state (moving)
        self.view.findChild(QProgressBar, 'progressBar').setVisible(True)
        
    def update_progress_bar(self):
        """Update the progress bar visually."""
        # This is where you can animate or update the bar if needed
        # However, in indeterminate mode, it is not necessary

        # If using a determinate mode, you'd update the value here
        # self.progress_bar.setValue(new_value)

        # Here we keep it simple since it's indeterminate

    def on_augmentation_finished(self):
        """Cleanup when the augmentation thread is finished."""
        self.view.findChild(QProgressBar, 'progressBar').setVisible(False)  
        
    def update_log_output(self, message):
        self.log_output.append(message)

    def show_error_message(self, message):
        QMessageBox.critical(self.view, "Error", f"An error occurred: {message}")
        logging.error(f"Error message displayed to user: {message}")

    def cancel_augmentation(self):
        logging.info("Cancelling augmentation...")
        if self.augmentation_thread and self.augmentation_thread.isRunning():
            self.augmentation_thread.terminate()  # Use carefully; ideally implement a safe stop mechanism
        self.view.close()





class AugmentationWindow(QMainWindow):
    def __init__(self, control: AugmentationController):
        super(AugmentationWindow, self).__init__()
        ui_path = self._get_ui_path("augmentation_interface.ui")
        uic.loadUi(ui_path, self)
        self.setWindowTitle("Point Cloud Augmentation")
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
        event.accept()
