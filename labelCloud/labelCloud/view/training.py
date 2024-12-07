import logging
from PyQt5.QtWidgets import QMainWindow, QPushButton, QMessageBox, QLineEdit, QFileDialog, QSpinBox, QComboBox, QCheckBox
from PyQt5 import uic
from PyQt5.QtCore import QSize, QSettings
import pkg_resources
import sys
from pathlib import Path
import platform
import os
import subprocess
from tools.batch_train import TrainingThread
import yaml 



class TrainingController:
    def __init__(self):
        self.view = None

    def startup(self, view):
        """Sets the view and initializes the controller."""
        self.view = view
        self.setup_connections()
        self.initialize_hyperparameters()

    def setup_connections(self):
        """Connect buttons and other widgets to their handlers."""
        start_button = self.view.findChild(QPushButton, 'startTrainingButton')
        cancel_button = self.view.findChild(QPushButton, 'cancelButton')
        reset_button = self.view.findChild(QPushButton, 'resetButton')
        open_config_button = self.view.findChild(QPushButton, 'openConfigButton')
        
        # Find the browse buttons
        browse_training_data_button = self.view.findChild(QPushButton, 'browseTrainingDataButton')
        browse_label_data_button = self.view.findChild(QPushButton, 'browseLabelDataButton')

        
        # Find the QLineEdit widgets for displaying the selected directories
        self.training_data_line_edit = self.view.findChild(QLineEdit, 'trainingDataLineEdit')
        self.label_data_line_edit = self.view.findChild(QLineEdit, 'labelDataLineEdit')
        self.venv_line_edit = self.view.findChild(QLineEdit, 'virtualEnvLineEdit')
        
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
            
        if open_config_button:
            logging.info("Open Config File button connected")
            open_config_button.clicked.connect(self.open_config_file)

            
    def initialize_hyperparameters(self):
        """Initialize the hyperparameter values in the UI."""
        # Set default values for hyperparameter widgets
        self.view.findChild(QSpinBox, 'batchSizeSpinBox').setValue(4)
        self.view.findChild(QLineEdit, 'learningRateLineEdit').setText("0.003")
        self.view.findChild(QSpinBox, 'epochSpinBox').setValue(100)
        self.view.findChild(QComboBox, 'backboneComboBox').setCurrentIndex(0)  # Default to first backbone option
        self.view.findChild(QLineEdit, 'pointCloudMagnificationLineEdit').setText("20")
        self.view.findChild(QLineEdit, 'labelMagnificationLineEdit').setText("0.85")
        
        # Initialize include augmented data checkbox
        self.include_augmented_data_checkbox = self.view.findChild(QCheckBox, 'includeAugmentedDataCheckbox')
        if self.include_augmented_data_checkbox:
            self.include_augmented_data_checkbox.setChecked(True)
            
        self.debug_mode_checkbox = self.view.findChild(QCheckBox, 'debugModeCheckbox')
        if self.debug_mode_checkbox:
            self.debug_mode_checkbox.setChecked(False)
        
        # Initialize directory paths
        current_dir = os.getcwd()  # Get the current working directory
        parent_dir = os.path.dirname(os.path.dirname(current_dir))  # Go up two levels

        # Set the default paths for ply_dir_edit and label_dir_edit
        ply_dir = os.path.join(parent_dir, "modified_data")
        label_dir = os.path.join(parent_dir, "modified_labels")


        # Set these paths in the QLineEdit widgets
        if self.training_data_line_edit:
            self.training_data_line_edit.setText(ply_dir)
        if self.label_data_line_edit:
            self.label_data_line_edit.setText(label_dir)
        if self.venv_line_edit:
            self.venv_line_edit.setText("windowspointcloud")

    def conda_env_exists(self, env_name):
        try:
            # Run 'conda env list' command
            result = subprocess.run(['conda', 'env', 'list'], stdout=subprocess.PIPE, text=True, check=True)
            # Check if the environment name exists in the output
            env_list = result.stdout
            return env_name in env_list
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while checking Conda environments: {e}")
            logging.error(f"Error occurred while checking Conda environments: {e}")
            return False
       
    def open_config_file(self):
        """Open the configuration file based on the selected backbone."""
        # Get the currently selected backbone architecture
        backbone_combo_box = self.view.findChild(QComboBox, 'backboneComboBox')
        selected_backbone = backbone_combo_box.currentText()

     
        # Get the current directory and go to its parent directory
        current_dir = os.getcwd()
        parent_dir = os.path.dirname(current_dir)  # Go to the parent directory

        # Now go to tools/cfgs/custom_models from the parent directory
        config_dir = os.path.join(parent_dir, 'tools', 'cfgs', 'custom_models')

        # Mapping backbone architecture to config file names
        config_file_mapping = {
            'PointPillar': 'pointpillar.yaml',
            'PV-RCNN': 'pv_rcnn.yaml'
        }

        # Get the corresponding config file name
        config_file_name = config_file_mapping.get(selected_backbone, None)

        if config_file_name:
            # Combine the directory path with the file name
            config_file_path = os.path.join(config_dir, config_file_name)

            # Use QFileDialog to allow the user to choose the file or open the default config
            selected_file, _ = QFileDialog.getOpenFileName(
                self.view,
                "Open Config File",
                config_file_path,
                "YAML Files (*.yaml);;All Files (*)"
            )
            if selected_file:
                logging.info(f"Config file selected: {selected_file}")
                # Load or display the selected config file
                # Step 6: Open the selected config file in Notepad (or default system editor)
                try:
                    # On Windows, open with Notepad
                    if os.name == 'nt':  # Windows
                        os.system(f'notepad.exe "{selected_file}"')
                    else:  # macOS or Linux
                        subprocess.run(['open', selected_file] if os.name == 'posix' else ['xdg-open', selected_file])
                    
                except Exception as e:
                    logging.error(f"Failed to open config file in editor: {e}")
                    QMessageBox.critical(self.view, "Error", f"Could not open config file in editor: {e}")
            else:
                logging.warning("No config file selected.")
        else:
            logging.error(f"No config file mapped for backbone: {selected_backbone}")
            
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
        
        virtual_env = self.venv_line_edit.text()
        logging.info(f"Virtual environment: {virtual_env}")
        
        if not self.conda_env_exists(virtual_env):
            print(f"Conda environment '{virtual_env}' does not exist.")
            logging.error(f"Conda environment '{virtual_env}' does not exist.")
            self.show_error_message(f"Conda environment '{virtual_env}' does not exist.", "Please make sure to conda create the virtual environment before proceeding!")
            self.venv_line_edit.setText(" ")
            return
                
        # Check if the directories are valid
        if not training_data_dir or not os.path.isdir(training_data_dir):
            logging.error("Invalid or empty training data directory.")
            self.show_error_message("Training Data Directory Error", "The training data directory is either empty or invalid. Please select a valid directory.")
            return

        if not label_data_dir or not os.path.isdir(label_data_dir):
            logging.error("Invalid or empty label data directory.")
            self.show_error_message("Label Data Directory Error", "The label data directory is either empty or invalid. Please select a valid directory.")
            return
            
        # Retrieve hyperparameter values from the UI
        batch_size = self.view.findChild(QSpinBox, 'batchSizeSpinBox').value()
        learning_rate = float(self.view.findChild(QLineEdit, 'learningRateLineEdit').text())
        epochs = self.view.findChild(QSpinBox, 'epochSpinBox').value()
        backbone = self.view.findChild(QComboBox, 'backboneComboBox').currentText()
        point_cloud_magnification = float(self.view.findChild(QLineEdit, 'pointCloudMagnificationLineEdit').text())
        label_magnification = float(self.view.findChild(QLineEdit, 'labelMagnificationLineEdit').text())
        
        # Retrieve the value of the include augmented data checkbox
        include_augmented_data = self.include_augmented_data_checkbox.isChecked()
        
        if include_augmented_data:
            logging.info("Val/Test set include augmented data (Method A)")
            
        # Retrieve the value of debug mode
        if self.debug_mode_checkbox.isChecked():
            exit_cmd = False
            logging.info("Debug mode set to True")
        else:
            exit_cmd = True
            logging.info("Debug mode set to False")
        
  
 
        # Create the training thread and pass the command and directories
        self.training_thread = TrainingThread(training_data_dir, label_data_dir, batch_size, learning_rate, epochs, backbone, point_cloud_magnification, label_magnification, virtual_env, include_augmented_data, exit_cmd)
        
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
        # Reset hyperparameters to default values
        self.initialize_hyperparameters()




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
