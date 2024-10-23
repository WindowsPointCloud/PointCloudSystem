import logging
from PyQt5.QtWidgets import QMainWindow, QPushButton, QTextEdit, QCheckBox, QLineEdit, QFileDialog, QMessageBox, QInputDialog, QComboBox
from PyQt5 import uic
from PyQt5.QtCore import QSize, QSettings
import pkg_resources
import platform
import sys
from pathlib import Path
import pkg_resources
import platform
import sys
from pathlib import Path
import os
from labelCloud.utils.command import run_command

from tools.batch_test import TestingThread

class InferenceController:
    def __init__(self):
        self.view = None

    def startup(self, view):
        """Sets the view and initializes the controller."""
        self.view = view
        self.setup_connections()
        self.initialize_default_save_prediction_directory()

    def setup_connections(self):
        """Connect buttons and other widgets to their handlers."""
        # Connect buttons from the UI to methods
        start_inference_button = self.view.findChild(QPushButton, 'startInferenceButton')
        start_testing_button = self.view.findChild(QPushButton, 'startTestingButton')
        reset_button = self.view.findChild(QPushButton, 'resetButton')
        cancel_button = self.view.findChild(QPushButton, 'cancelButton')


        browse_inference_file_button = self.view.findChild(QPushButton, 'browseInferenceFileButton')
        browse_model_checkpoint_button = self.view.findChild(QPushButton, 'browseModelCheckpointButton')
        browse_save_predictions_button = self.view.findChild(QPushButton, 'browseSavePredictionsButton')
        browse_truth_label_directory_button = self.view.findChild(QPushButton, 'browseTruthLabelDirectoryButton')

        # Connect the buttons to their respective methods
        if start_inference_button:
            start_inference_button.clicked.connect(self.start_model_inference)
        if start_testing_button:
            start_testing_button.clicked.connect(self.start_model_testing)
        if reset_button:
            reset_button.clicked.connect(self.reset_process)
        if cancel_button:
            cancel_button.clicked.connect(self.cancel_process)

      
        if browse_inference_file_button:
            browse_inference_file_button.clicked.connect(self.browse_inference_file)
        if browse_model_checkpoint_button:
            browse_model_checkpoint_button.clicked.connect(self.browse_model_checkpoint)
        if browse_save_predictions_button:
            browse_save_predictions_button.clicked.connect(self.browse_save_predictions_directory)
        if browse_truth_label_directory_button:
            browse_truth_label_directory_button.clicked.connect(self.browse_truth_label_directory)
        
    def initialize_default_save_prediction_directory(self):
        """Initialize the save prediction directory with a default path."""
        # Get current working directory, go to parent, then append "pred_label"
        current_directory = Path(os.getcwd()).parents[1]
        save_prediction_directory = current_directory / "pred_label"

        # If directory exists, remove it and recreate
        if save_prediction_directory.exists():
            logging.info(f"Removing existing save prediction directory: {save_prediction_directory}")
            for item in save_prediction_directory.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    os.rmdir(item)
            save_prediction_directory.rmdir()

        save_prediction_directory.mkdir(parents=True, exist_ok=True)

        # Set the default value in the QLineEdit
        save_predictions_line_edit = self.view.findChild(QLineEdit, 'savePredictionsLineEdit')
        if save_predictions_line_edit:
            save_predictions_line_edit.setText(str(save_prediction_directory))


    def start_model_inference(self):
        logging.info("Starting model inference...")
        # Get the selected backbone architecture
        backbone_combo_box = self.view.findChild(QComboBox, 'backboneComboBox')
        if backbone_combo_box:
            selected_backbone = backbone_combo_box.currentText()
            if selected_backbone == "PointPillar":
                config_file = r"cfgs\custom_models\pointpillar.yaml"
            elif selected_backbone == "PV-RCNN":
                config_file = r"cfgs\custom_models\pv-rcnn.yaml"
            elif selected_backbone == "Point-RCNN":
                config_file = r"cfgs\custom_models\point-rcnn.yaml"
            else:
                logging.error("Unsupported backbone architecture selected.")
                return
                
        print(config_file)
        # Get paths from UI
        inference_file_line_edit = self.view.findChild(QLineEdit, 'inferenceFileLineEdit')
        model_checkpoint_line_edit = self.view.findChild(QLineEdit, 'modelCheckpointLineEdit')
        save_predictions_line_edit = self.view.findChild(QLineEdit, 'savePredictionsLineEdit')
        truth_label_directory_line_edit = self.view.findChild(QLineEdit, 'truthLabelDirectoryLineEdit')
        is_2d_checkbox = self.view.findChild(QCheckBox, 'is2DCheckBox')

        if inference_file_line_edit and model_checkpoint_line_edit and save_predictions_line_edit:
            inference_file_path = inference_file_line_edit.text()
            checkpoint_path = model_checkpoint_line_edit.text()
            save_predictions_path = save_predictions_line_edit.text()
            file_extension = os.path.splitext(inference_file_path)[1]
            truth_label_directory = truth_label_directory_line_edit.text() if truth_label_directory_line_edit else ""
            is_2d = is_2d_checkbox.isChecked() if is_2d_checkbox else False
            print(file_extension)
            print(inference_file_path)
            print(checkpoint_path)
            print(truth_label_directory)
            print(save_predictions_path)
            print(is_2d)
            
            # Check file extension
            if file_extension != '':
                if file_extension not in [".bin", ".npy", ".ply"]:
                    QMessageBox.critical(
                        self.view,
                        "Invalid File Extension",
                        "Only .bin, .npy and .ply files are accepted for inference.",
                        QMessageBox.Ok
                    )
                    inference_file_line_edit.clear()
                    return
                    
            else:
                if os.path.isdir(inference_file_path):
                    files = os.listdir(inference_file_path)
                    if not files:
                        QMessageBox.critical(
                            self.view,
                            "Empty Directory",
                            "The selected directory is empty.",
                            QMessageBox.Ok
                        )
                        return
                    
                    first_file_extension = os.path.splitext(files[0])[1]
                    if first_file_extension not in [".bin", ".npy", ".ply"]:
                        QMessageBox.critical(
                            self.view,
                            "Invalid File Extension",
                            "Only .bin, .npy, or .ply files are accepted for inference.",
                            QMessageBox.Ok
                        )
                        return
                    
                    for file in files:
                        if os.path.splitext(file)[1] != first_file_extension:
                            QMessageBox.critical(
                                self.view,
                                "Inconsistent File Extensions",
                                "All files in the directory must have the same extension.",
                                QMessageBox.Ok
                            )
                            return
                    
                    file_extension = first_file_extension
                else:
                    QMessageBox.critical(
                        self.view,
                        "Invalid Input",
                        "The provided path is neither a file nor a directory.",
                        QMessageBox.Ok
                    )
                    return
                
          
            # Prepare command   
            cmd = f'conda activate windowspointcloud && python demo.py --cfg_file "{config_file}" --ckpt "{checkpoint_path}" --data_path "{inference_file_path}" --ext "{file_extension}" --saved_prediction_label_directory "{save_predictions_path}"'
            
            if truth_label_directory:
                cmd += f' --truth_label_directory "{truth_label_directory}"'
            
            if is_2d:
                cmd += " --visualize_2d"   
            
            subdirectory = '..\\tools'

            # Run the command
            try:
                logging.info("Starting demo...") 
                run_command(cmd, subdirectory)
                logging.info("Ending demo... with virtual env")
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

    def start_model_testing(self):
        logging.info("Starting model testing...")
        
        # Get paths from UI
       
        model_checkpoint_line_edit = self.view.findChild(QLineEdit, 'modelCheckpointLineEdit')

        if model_checkpoint_line_edit:
           
            checkpoint_path = model_checkpoint_line_edit.text()

      
            if not os.path.isfile(checkpoint_path):
                QMessageBox.critical(
                    self.view,
                    "Invalid Checkpoint File",
                    "The specified checkpoint file does not exist.",
                    QMessageBox.Ok
                )
                return

            # Get the selected backbone architecture from UI
            backbone_combo_box = self.view.findChild(QComboBox, 'backboneComboBox')
            if backbone_combo_box:
                selected_backbone = backbone_combo_box.currentText()
                if selected_backbone == "PointPillar":
                    config_file = r"cfgs\custom_models\pointpillar.yaml"
                elif selected_backbone == "PV-RCNN":
                    config_file = r"cfgs\custom_models\pv-rcnn.yaml"
                elif selected_backbone == "Point-RCNN":
                    config_file = r"cfgs\custom_models\point-rcnn.yaml"
                else:
                    logging.error("Unsupported backbone architecture selected.")
                    return

            # Create and start the testing thread
            self.testing_thread = TestingThread( checkpoint_path, config_file)
            self.testing_thread.testing_complete.connect(self.on_testing_complete)
            self.testing_thread.start()

    def on_testing_complete(self, message):
        logging.info(message)
        QMessageBox.information(self.view, "Testing Complete", message, QMessageBox.Ok)


    def reset_process(self):
        logging.info("Resetting process...")
        # Clear all QLineEdit fields
        inference_file_line_edit = self.view.findChild(QLineEdit, 'inferenceFileLineEdit')
        model_checkpoint_line_edit = self.view.findChild(QLineEdit, 'modelCheckpointLineEdit')
        testing_dir_line_edit = self.view.findChild(QLineEdit, 'testingDirLineEdit')
        save_predictions_line_edit = self.view.findChild(QLineEdit, 'savePredictionsLineEdit')

        if inference_file_line_edit:
            inference_file_line_edit.clear()
        if model_checkpoint_line_edit:
            model_checkpoint_line_edit.clear()
        if testing_dir_line_edit:
            testing_dir_line_edit.clear()
        if save_predictions_line_edit:
            save_predictions_line_edit.clear()

    def cancel_process(self):
        logging.info("Cancelling process...")
        # Add logic to cancel the process and close the window
        self.view.close()



    def browse_inference_file(self):
        """Allow the user to either select a file or a directory for inference."""
        # Ask the user if they want to select a file or a directory
        choice, ok = QInputDialog.getItem(self.view, "Select Option", "Choose an option:", ["File", "Directory"], 0, False)
        
        if ok and choice:  # If the user made a selection
            if choice == "File":
                # Open file dialog to select a file
                file_name, _ = QFileDialog.getOpenFileName(self.view, "Select Inference File", "", "All Files (*.*)")
                if file_name:
                    inference_file_line_edit = self.view.findChild(QLineEdit, 'inferenceFileLineEdit')
                    if inference_file_line_edit:
                        inference_file_line_edit.setText(file_name)
            
            elif choice == "Directory":
                # Open directory dialog to select a directory
                dir_name = QFileDialog.getExistingDirectory(self.view, "Select Inference Directory", "")
                if dir_name:
                    inference_file_line_edit = self.view.findChild(QLineEdit, 'inferenceFileLineEdit')
                    if inference_file_line_edit:
                        inference_file_line_edit.setText(dir_name)
        else:
            QMessageBox.warning(self.view, "Selection Cancelled", "No selection was made.")

    def browse_model_checkpoint(self):
        file_name, _ = QFileDialog.getOpenFileName(self.view, "Select Model Checkpoint", "", "All Files (*.*)")
        if file_name:
            model_checkpoint_line_edit = self.view.findChild(QLineEdit, 'modelCheckpointLineEdit')
            if model_checkpoint_line_edit:
                model_checkpoint_line_edit.setText(file_name)

    def browse_save_predictions_directory(self):
        directory = QFileDialog.getExistingDirectory(self.view, "Select Directory to Save Prediction Labels")
        if directory:
            save_predictions_line_edit = self.view.findChild(QLineEdit, 'savePredictionsLineEdit')
            if save_predictions_line_edit:
                save_predictions_line_edit.setText(directory)
                
    def browse_truth_label_directory(self):
        directory = QFileDialog.getExistingDirectory(self.view, "Select Directory for Truth Labels")
        if directory:
            truth_label_directory_line_edit = self.view.findChild(QLineEdit, 'truthLabelDirectoryLineEdit')
            if truth_label_directory_line_edit:
                truth_label_directory_line_edit.setText(directory)





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
        event.accept()
