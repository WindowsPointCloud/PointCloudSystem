import logging
from PyQt5.QtWidgets import QMainWindow, QPushButton
from PyQt5 import uic
from PyQt5.QtCore import QSize, QSettings
import pkg_resources
import platform
import sys
from pathlib import Path

class InferenceController:
    def __init__(self):
        self.view = None

    def startup(self, viewimport logging
from PyQt5.QtWidgets import QMainWindow, QPushButton, QMessageBox
from PyQt5 import uic
from PyQt5.QtCore import QSize, QSettings

import pkg_resources
import platform
import sys
from pathlib import Path

from tools.demo_2 import run_demo

class InferenceController:
    def __init__(self):
        self.view = None

    def startup(self, view):
        """Sets the view and initializes the controller."""
        self.view = view
        self.setup_connections()

    def setup_connections(self):
        """Connect buttons and other widgets to their handlers."""
        visualization_button = self.view.findChild(QPushButton, 'visualizationButton')
        reset_button = self.view.findChild(QPushButton, 'button_reset')
        save_button = self.view.findChild(QPushButton, 'button_save')
        cancel_button = self.view.findChild(QPushButton, 'button_cancel')

        if visualization_button:
            visualization_button.clicked.connect(self.start_visualization)
        if reset_button:
            reset_button.clicked.connect(self.reset_augmentation)
        if save_button:
            save_button.clicked.connect(self.save_augmentation)
        if cancel_button:
            cancel_button.clicked.connect(self.cancel_augmentation)

    def start_visualization(self):
        logging.info("Starting visualization...")
        
        try:
            logging.info("Starting demo...")
            run_demo()  # Replace with the actual demo function or logic
            logging.info("Ending demo...")
            
        except Exception as e:
            # Log the error
            logging.error(f"An error occurred during visualization: {e}", exc_info=True)
            
            # Provide user feedback through GUI
            QMessageBox.critical(
                self.view,
                "Visualization Error",
                f"An error occurred while starting the visualization:\n{str(e)}",
                QMessageBox.Ok
            )
        

    def reset_augmentation(self):
        logging.info("Resetting augmentation...")
        # Add logic to reset the augmentation process
        # Clear progress bar and charts as needed

    def save_augmentation(self):
        logging.info("Saving augmentation...")
        # Add logic to save the augmented data
        # Show confirmation message if needed
        self.save()
        self.view.close()

    def cancel_augmentation(self):
        logging.info("Cancelling augmentation...")
        # Add logic to cancel the augmentation process and close the window
        self.view.close()

    def save(self):
        logging.info("Saving state...")
        # Add logic to save the current state if needed



class InferenceWindow(QMainWindow):
    def __init__(self, control: InferenceController):
        super(InferenceWindow, self).__init__()
        ui_path = self._get_ui_path("inference_interface.ui")
        uic.loadUi( ui_path,self)
        self.setWindowTitle("3D Object Detection Model Inference")
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
        self.controller.save()
        event.accept()

        """Sets the view and initializes the controller."""
        self.view = view
        self.setup_connections()

    def setup_connections(self):
        """Connect buttons and other widgets to their handlers."""
        start_button = self.view.findChild(QPushButton, 'button_start')
        reset_button = self.view.findChild(QPushButton, 'button_reset')
        save_button = self.view.findChild(QPushButton, 'button_save')
        cancel_button = self.view.findChild(QPushButton, 'button_cancel')

        if start_button:
            start_button.clicked.connect(self.start_augmentation)
        if reset_button:
            reset_button.clicked.connect(self.reset_augmentation)
        if save_button:
            save_button.clicked.connect(self.save_augmentation)
        if cancel_button:
            cancel_button.clicked.connect(self.cancel_augmentation)

    def start_augmentation(self):
        logging.info("Starting augmentation...")
        # Add logic to start the augmentation process
        # Update progress bar and charts as needed

    def reset_augmentation(self):
        logging.info("Resetting augmentation...")
        # Add logic to reset the augmentation process
        # Clear progress bar and charts as needed

    def save_augmentation(self):
        logging.info("Saving augmentation...")
        # Add logic to save the augmented data
        # Show confirmation message if needed
        self.save()
        self.view.close()

    def cancel_augmentation(self):
        logging.info("Cancelling augmentation...")
        # Add logic to cancel the augmentation process and close the window
        self.view.close()

    def save(self):
        logging.info("Saving state...")
        # Add logic to save the current state if needed



class InferenceWindow(QMainWindow):
    def __init__(self, control: InferenceController):
        super(InferenceWindow, self).__init__()
        ui_path = self._get_ui_path("inference_interface.ui")
        uic.loadUi( ui_path,self)
        self.setWindowTitle("3D Object Detection Model Inference")
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
        self.controller.save()
        event.accept()
