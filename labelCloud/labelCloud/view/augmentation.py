import logging
from PyQt5.QtWidgets import QMainWindow, QPushButton, QTextEdit,  QLineEdit, QFileDialog, QMessageBox, QProgressBar, QDoubleSpinBox, QSpinBox

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
        self.initialize_hyperparameters()

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
    
    def initialize_hyperparameters(self):
        """Initialize the hyperparameter widgets."""
        self.displacement_range_min = self.view.findChild(QDoubleSpinBox, 'spinBox_displacement_range_min')
        self.displacement_range_max = self.view.findChild(QDoubleSpinBox, 'spinBox_displacement_range_max')
        self.rotation_range_min = self.view.findChild(QDoubleSpinBox, 'spinBox_rotation_range_min')
        self.rotation_range_max = self.view.findChild(QDoubleSpinBox, 'spinBox_rotation_range_max')
        self.augment_per_file = self.view.findChild(QSpinBox, 'spinBox_augment_per_file')
        self.wires_to_remove = self.view.findChild(QSpinBox, 'spinBox_wires_to_remove')
        self.wires_to_keep = self.view.findChild(QSpinBox, 'spinBox_wires_to_keep')
        
        # Initialize directory paths
        current_dir = os.getcwd()  # Get the current working directory
        parent_dir = os.path.dirname(os.path.dirname(current_dir))  # Go up two levels

        # Set the default paths for ply_dir_edit and label_dir_edit
        ply_dir = os.path.join(parent_dir, "modified_data")
        label_dir = os.path.join(parent_dir, "modified_labels")


        # Set these paths in the QLineEdit widgets
        if self.ply_dir_edit:
            self.ply_dir_edit.setText(ply_dir)
        if self.label_dir_edit:
            self.label_dir_edit.setText(label_dir)



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
        
        # Validate hyperparameters
        if not (0 <= self.displacement_range_min.value() <= 1):
            QMessageBox.critical(self.view, "Error", "Displacement range minimum must be between 0 and 1.")
            return
        if not (0 <= self.displacement_range_max.value() <= 1):
            QMessageBox.critical(self.view, "Error", "Displacement range maximum must be between 0 and 1.")
            return
        if not (0 <= self.rotation_range_min.value() <= 2):
            QMessageBox.critical(self.view, "Error", "Rotation range minimum must be between 0 and 2.")
            return
        if not (0 <= self.rotation_range_max.value() <= 2):
            QMessageBox.critical(self.view, "Error", "Rotation range maximum must be between 0 and 2.")
            return
        if not (2 <= self.augment_per_file.value() <= 3):
            QMessageBox.critical(self.view, "Error", "Augment per file must be between 2 and 3.")
            return
        if not (0 <= self.wires_to_remove.value() <= 5):
            QMessageBox.critical(self.view, "Error", "Wires to remove must be between 0 and 5.")
            return
        if not (5 <= self.wires_to_keep.value() <= 6):
            QMessageBox.critical(self.view, "Error", "Wires to keep must be between 5 and 6.")
            return
            
      

        # Create and start the augmentation thread
        self.augmentation_thread = AugmentationThread(ply_directory, label_directory, displacement_range=(self.displacement_range_min.value(), self.displacement_range_max.value()), rotation_range=(self.rotation_range_min.value(), self.rotation_range_max.value()), augment_per_file=self.augment_per_file.value(), legs_to_remove=self.wires_to_remove.value(), legs_to_keep=self.wires_to_keep.value())
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
