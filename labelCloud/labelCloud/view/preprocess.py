import logging
from PyQt5.QtWidgets import QMainWindow, QPushButton, QFileDialog, QTextEdit, QLineEdit, QMessageBox, QCheckBox, QDoubleSpinBox, QSpinBox
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
        self.thread = None


    def startup(self, view):
        """Sets the view and initializes the controller."""
        self.view = view
        self.setup_connections()
        self.initialize_hyperparameters()

    def setup_connections(self):
        """Connect buttons and other widgets to their handlers."""
        
        self.view.start_button = self.view.findChild(QPushButton, 'button_start')
        self.view.finish_button = self.view.findChild(QPushButton, 'button_finish')
        self.view.reset_button = self.view.findChild(QPushButton, 'button_reset')
        
        start_button = self.view.button_start
        finish_button = self.view.button_finish
        reset_button = self.view.button_reset
        
        raw_data_button = self.view.findChild(QPushButton, 'button_browse_raw_data')
        label_files_button = self.view.findChild(QPushButton, 'button_browse_label_files')
       

        self.raw_data_input = self.view.findChild(QLineEdit, 'lineEdit_raw_data')
        self.label_files_input = self.view.findChild(QLineEdit, 'lineEdit_label_files')
       
        
        self.log_output = self.view.findChild(QTextEdit, 'textEdit_log')
        self.log_output.setReadOnly(True)
        



        if start_button:
            start_button.clicked.connect(lambda: self.start_preprocessing(self.raw_data_input.text(), self.label_files_input.text()))
        if reset_button:
            reset_button.clicked.connect(self.reset_preprocessing)
        if finish_button:
            finish_button.clicked.connect(self.finish_preprocessing)
            
        # Connect browse buttons
        if raw_data_button:
            raw_data_button.clicked.connect(lambda: self.browse_folder(self.raw_data_input))
        if label_files_button:
            label_files_button.clicked.connect(lambda: self.browse_folder(self.label_files_input))
    
    def initialize_hyperparameters(self):
        """Initialize the hyperparameter widgets."""
        # Preprocessing elements
        self.downsample_checkbox = self.view.findChild(QCheckBox, 'downsampleCheckBox')
        self.downsample_spinbox = self.view.findChild(QSpinBox, 'downsampleSpinBox')
        self.remove_outlier_checkbox = self.view.findChild(QCheckBox, 'removeOutlierCheckBox')
        self.nb_neighbors_spinbox = self.view.findChild(QSpinBox, 'nbNeighborsSpinBox')
        self.std_ratio_spinbox = self.view.findChild(QDoubleSpinBox, 'stdRatioDoubleSpinBox')
        self.roi_cropping_checkbox = self.view.findChild(QCheckBox, 'roiCroppingCheckBox')
        self.roi_cropping_spinbox = self.view.findChild(QDoubleSpinBox, 'roiCroppingSpinBox')

        #Set default values
        if self.downsample_checkbox:
            self.downsample_checkbox.setChecked(True)
        if self.remove_outlier_checkbox:
            self.remove_outlier_checkbox.setChecked(True)
        if self.roi_cropping_checkbox:
            self.roi_cropping_checkbox.setChecked(True)
        if self.downsample_spinbox:
            self.downsample_spinbox.setValue(8)
        if self.nb_neighbors_spinbox:
            self.nb_neighbors_spinbox.setValue(5)
        if self.std_ratio_spinbox:
            self.std_ratio_spinbox.setValue(1.0)
        if self.roi_cropping_spinbox:
            self.roi_cropping_spinbox.setValue(5.13)
        
    
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
            
        # Validate raw data folder contents
        valid_raw_extensions = {'.bin', '.ply', '.npy'}
        raw_files = os.listdir(raw_data_folder)
        if not raw_files:
            QMessageBox.critical(
                self.view,
                "Empty Raw Data Folder",
                "The raw data folder is empty. Please select a folder containing point cloud files.",
                QMessageBox.Ok
            )
            return

        invalid_raw_files = [f for f in raw_files if not os.path.splitext(f)[1].lower() in valid_raw_extensions]
        if invalid_raw_files:
            QMessageBox.critical(
                self.view,
                "Invalid Raw Data Files",
                f"The raw data folder contains invalid file types. Only .bin, .ply, or .npy files are allowed.\nInvalid files: {', '.join(invalid_raw_files)}",
                QMessageBox.Ok
            )
            return

        # Validate label files folder contents
        label_files = os.listdir(label_files_folder)
        if not label_files:
            QMessageBox.critical(
                self.view,
                "Empty Label Files Folder",
                "The label files folder is empty. Please select a folder containing .json files.",
                QMessageBox.Ok
            )
            return

        invalid_label_files = [f for f in label_files if not f.lower().endswith('.json')]
        if invalid_label_files:
            QMessageBox.critical(
                self.view,
                "Invalid Label Files",
                f"The label files folder contains invalid file types. Only .json files are allowed.\nInvalid files: {', '.join(invalid_label_files)}",
                QMessageBox.Ok
            )
            return
     
        
        # Validate and log preprocessing module settings
        downsample_value, nb_neighbors, std_ratio, roi_range = None, None, None, None
        
        # Downsample validation
        if self.downsample_checkbox and self.downsample_checkbox.isChecked():
            downsample_value = self.downsample_spinbox.value()
            if downsample_value < 1 or downsample_value > 10:
                QMessageBox.critical(
                    self.view,
                    "Invalid Downsample Value",
                    "Downsample value must be between 1 and 10.",
                    QMessageBox.Ok
                )
                return
            self.log_output.append(f"Downsample Point Cloud: Every {downsample_value} points")
        
        # Remove outliers validation
        if self.remove_outlier_checkbox and self.remove_outlier_checkbox.isChecked():
            nb_neighbors = self.nb_neighbors_spinbox.value()
            std_ratio = self.std_ratio_spinbox.value()
            if nb_neighbors < 1 or nb_neighbors > 8:
                QMessageBox.critical(
                    self.view,
                    "Invalid Neighbors Value",
                    "Number of neighbors must be between 1 and 8.",
                    QMessageBox.Ok
                )
                return
            if std_ratio < 0 or std_ratio > 1.5:
                QMessageBox.critical(
                    self.view,
                    "Invalid Std Ratio",
                    "Standard deviation ratio must be between 0 and 1.5.",
                    QMessageBox.Ok
                )
                return
            self.log_output.append(f"Remove Statistical Outlier: Neighbors={nb_neighbors}, Std Ratio={std_ratio}")
        
        # ROI cropping validation
        if self.roi_cropping_checkbox and self.roi_cropping_checkbox.isChecked():
            roi_range = self.roi_cropping_spinbox.value()
            if roi_range < 0 or roi_range > 10.0:
                QMessageBox.critical(
                    self.view,
                    "Invalid ROI Range",
                    "ROI range must be between 0 and 10.0.",
                    QMessageBox.Ok
                )
                return
            self.log_output.append(f"ROI Cropping: X Range={roi_range}")
            
        self.log_output.clear()
        self.log_output.append("Starting preprocessing...")
        self.log_output.append(f"Raw data folder: {raw_data_folder}")
        self.log_output.append(f"Label files folder: {label_files_folder}")
        

        self.thread = DataPreprocessor(raw_data_folder, label_files_folder, downsample_value, nb_neighbors, std_ratio, roi_range)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.on_preprocessing_finished)
        self.thread.start()

    def update_progress(self, message):
        self.log_output.append(message)
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())  # Scroll to bottom  
    
    def reset_preprocessing(self):
        logging.info("Reset preprocessing...")
        self.initialize_hyperparameters()
        self.raw_data_input.clear()
        self.label_files_input.clear()
        self.log_output.clear()
        
    def on_preprocessing_finished(self):
        """Handler when preprocessing is complete."""
        self.log_output.append("Preprocessing complete.")
        QMessageBox.information(self.view, "Process Complete", "Data preprocessing is finished.")
        self.view.button_start.setEnabled(True)  # Enable the start button after completion
  

    def finish_preprocessing(self):
        if self.thread and self.thread.isRunning():
                self.thread.stop()  # Signal the thread to stop
                self.thread.wait()  # Wait for the thread to finish
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
        try:
            if self.controller.thread is not None and self.controller.thread.isRunning():
                reply = QMessageBox.warning(
                    self,
                    "Process Running",
                    "The preprocessing task is still running. Do you really want to exit?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.controller.thread.terminate()  # Force terminate the thread if user confirms
                    event.accept()  # Close the window
                else:
                    event.ignore()  # Prevent the window from closing
            else:
                event.accept()  # Close the window if no background task is running
        except Exception as e:
            logging.error("Exception in closeEvent: %s", str(e), exc_info=True)
            event.accept()  # Close the window to prevent further issues
