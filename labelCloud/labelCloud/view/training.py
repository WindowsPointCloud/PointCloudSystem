import logging
from PyQt5.QtWidgets import QMainWindow, QPushButton, QMessageBox, QLineEdit, QFileDialog
from PyQt5 import uic
from PyQt5.QtCore import QSize, QSettings
import pkg_resources
import sys
from pathlib import Path
import platform
import os
import subprocess
from tools.batch_train import TrainingThread



class TrainingController:
    def __init__(self):
        self.view = None

    def startup(self, view):
        """Sets the view and initializes the controller."""
        self.view = view
        self.setup_connections()

    def setup_connections(self):
        """Connect buttons and other widgets to their handlers."""
        start_button = self.view.findChild(QPushButton, 'startTrainingButton')
        cancel_button = self.view.findChild(QPushButton, 'cancelButton')
        reset_button = self.view.findChild(QPushButton, 'resetButton')
        
        # Find the browse buttons
        browse_training_data_button = self.view.findChild(QPushButton, 'browseTrainingDataButton')
        browse_label_data_button = self.view.findChild(QPushButton, 'browseLabelDataButton')

        
        # Find the QLineEdit widgets for displaying the selected directories
        self.training_data_line_edit = self.view.findChild(QLineEdit, 'trainingDataLineEdit')
        self.label_data_line_edit = self.view.findChild(QLineEdit, 'labelDataLineEdit')
        
        # Connect the browse buttons to the corresponding methods
        if browse_training_data_button:
            logging.info("Browse Training Data button connected")
            browse_training_data_button.clicked.connect(self.browse_training_data)

        if browse_label_data_button:
            logging.info("Browse Label Data button connected")
            browse_label_data_button.clicked.connect(self.browse_label_data)


        if start_button:
            logging.info("Start button connected")
            start_button.clicked.connect(self.start_training)
        if reset_button:
            logging.info("Reset button connected")
            reset_button.clicked.connect(self.reset_hyperparameters)
        if cancel_button:
            logging.info("Cancel button connected")
            cancel_button.clicked.connect(self.cancel_training)

    def browse_training_data(self):
        """Open a file dialog to browse for the training data directory."""
        training_data_dir = QFileDialog.getExistingDirectory(self.view, 'Select Training Data Directory')
        if training_data_dir:
            self.training_data_line_edit.setText(training_data_dir)
            logging.info(f"Training data directory set to: {training_data_dir}")

    def browse_label_data(self):
        """Open a file dialog to browse for the label data directory."""
        label_data_dir = QFileDialog.getExistingDirectory(self.view, 'Select Label Data Directory')
        if label_data_dir:
            self.label_data_line_edit.setText(label_data_dir)
            logging.info(f"Label data directory set to: {label_data_dir}")

    def start_training(self):
        logging.info("Starting training...")
        
        training_data_dir = self.training_data_line_edit.text()
        label_data_dir = self.label_data_line_edit.text()
        logging.info(f"Training data from: {training_data_dir}, Labels from: {label_data_dir}")
        
        # Check if the directories are valid
        if not training_data_dir or not os.path.isdir(training_data_dir):
            logging.error("Invalid or empty training data directory.")
            self.show_error_message("Training Data Directory Error", "The training data directory is either empty or invalid. Please select a valid directory.")
            return

        if not label_data_dir or not os.path.isdir(label_data_dir):
            logging.error("Invalid or empty label data directory.")
            self.show_error_message("Label Data Directory Error", "The label data directory is either empty or invalid. Please select a valid directory.")
            return
 
        # Create the training thread and pass the command and directories
        self.training_thread = TrainingThread(training_data_dir, label_data_dir)
        
        # Connect signals to handle completion and errors
        self.training_thread.finished.connect(self.on_training_finished)
        self.training_thread.error.connect(self.on_training_error)

        # Start the training thread
        self.training_thread.start()
        
    def on_training_finished(self):
        """Handle training completion."""
        logging.info("Training finished successfully!")
        QMessageBox.information(self.view, "Training Complete", "Training finished successfully!", QMessageBox.Ok)

    def on_training_error(self, error_message):
        """Handle training errors."""
        logging.error(f"Training failed: {error_message}")
        QMessageBox.critical(self.view, "Training Error", f"An error occurred during training:\n{error_message}", QMessageBox.Ok)

    def reset_hyperparameters(self):
        logging.info("Resetting training hyperparameters...")
        # Add logic to reset the augmentation process
        # Clear progress bar and charts as needed




    def cancel_training(self):
        reply = QMessageBox.question(self.view, 'Cancel Training',
                                     'Are you sure you want to cancel the training?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            logging.info("Cancelling training...")
            # Add logic to cancel the augmentation process and clean up resources
            self.view.close()
            
    def show_error_message(self, title, message):
        """Display an error message using QMessageBox."""
        msg_box = QMessageBox(self.view)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()




class TrainingWindow(QMainWindow):
    def __init__(self, control: TrainingController):
        super(TrainingWindow, self).__init__()
        ui_path = self._get_ui_path("training_interface.ui")
        uic.loadUi(ui_path, self)
        self.setWindowTitle("3D Object Detection Model Training")
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
