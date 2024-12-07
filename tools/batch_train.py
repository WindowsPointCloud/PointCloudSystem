import open3d as o3d
import numpy as np
import os
import shutil
from PyQt5.QtCore import QThread, pyqtSignal
import json
import copy
import logging
import subprocess
import sys
import os
from ruamel.yaml import YAML



from tools.batch_preprocess import read_all_json_files


def check_and_update_base_config(config_file_path):
    # Get the absolute path of the desired _BASE_CONFIG_ value
    cfg_file_abs = os.path.abspath(os.path.join('..', 'tools', 'cfgs', 'dataset_configs', 'custom_dataset.yaml'))

    # Initialize ruamel.yaml for round-trip loading and dumping
    yaml = YAML()
    yaml.preserve_quotes = True  # Preserve quotes if any
    yaml.width = 1000  # Prevent line wrapping

    # Open and read the YAML configuration file
    with open(config_file_path, 'r') as file:
        config_data = yaml.load(file)

    # Extract the _BASE_CONFIG_ value
    data_config = config_data.get('DATA_CONFIG')
    if data_config is None:
        raise KeyError("'DATA_CONFIG' section is missing in the configuration file.")

    base_config = data_config.get('_BASE_CONFIG_')

    # Normalize paths for comparison
    normalized_base_config = os.path.normpath(base_config) if base_config else None
    normalized_cfg_file_abs = os.path.normpath(cfg_file_abs)

    # Compare and update if necessary
    if normalized_base_config != normalized_cfg_file_abs:
        print(f"Updating _BASE_CONFIG_ from {normalized_base_config} to {normalized_cfg_file_abs}")
        logging.info(f"Updating _BASE_CONFIG_ from {normalized_base_config} to {normalized_cfg_file_abs}")
        # Update _BASE_CONFIG_ to match CFG_FILE_ABS
        data_config['_BASE_CONFIG_'] = cfg_file_abs

        # Write back to the YAML file
        with open(config_file_path, 'w') as file:
            yaml.dump(config_data, file)
    else:
        print("_BASE_CONFIG_ is already up to date.")
        logging.info("_BASE_CONFIG_ is already up to date.")


class TrainingThread(QThread):
    # Define signals to communicate back to the main thread
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, training_data_dir, label_data_dir, batch_size, learning_rate, epochs, backbone, point_cloud_magnification, label_magnification, virtual_env, include_augmented_data = True, exit_cmd=True):
        super().__init__()
        self.training_data_dir = training_data_dir
        self.label_data_dir = label_data_dir
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.backbone = backbone
        self.point_cloud_magnification = point_cloud_magnification
        self.label_magnification = label_magnification
        self.include_augmented_data = include_augmented_data
        self.virtual_env = virtual_env
        self.exit_cmd = exit_cmd

    def run(self):
        try:
            if self.backbone == 'PointPillar':
                config_file_name = 'pointpillar.yaml'
            elif self.backbone == 'Point-RCNN':
                config_file_name = 'pointrcnn.yaml'  
            elif self.backbone == 'PV-RCNN':
                config_file_name = 'pv_rcnn.yaml'
                
                
            read_all_json_files(self.label_data_dir, self.training_data_dir)
            #PC_MF=20
            #DXDY_MF=0.85
            NAME='custom'
            CFG_FILE_ABS = os.path.abspath(os.path.join('..', 'tools', 'cfgs', 'custom_models', config_file_name))
            print(CFG_FILE_ABS)
            
            check_and_update_base_config(CFG_FILE_ABS)
            
            cmd = f'python convert_raw_data.py --name "{NAME}"  --dir "{self.label_data_dir}" --cfg_file "{CFG_FILE_ABS}" --pc_mf "{self.point_cloud_magnification}" --dxdy_mf "{self.label_magnification}"'
            if self.include_augmented_data:
                cmd += " --val_aug"   
            target_subdirectory = os.path.join('..', 'tools')
            self.run_command(self.virtual_env, cmd, target_subdirectory, exit_cmd = self.exit_cmd)
            
            DATASET_CFG_FILE_ABS = os.path.abspath(os.path.join('..', 'tools', 'cfgs', 'dataset_configs', 'custom_dataset.yaml'))
            print(DATASET_CFG_FILE_ABS)
            cmd = f'set CUDA_LAUNCH_BLOCKING=1 && python -m pcdet.datasets.custom.custom_dataset create_custom_infos {DATASET_CFG_FILE_ABS}'
            self.run_command(self.virtual_env, cmd, exit_cmd = self.exit_cmd)
            
            #EPOCH = 100
            #BATCH_SIZE = 4
            WORKER = 1
            cmd = f'set CUDA_LAUNCH_BLOCKING=1 && python train.py --cfg_file "{CFG_FILE_ABS}" --lr "{self.learning_rate}" --epochs "{self.epochs}" --batch_size "{self.batch_size}" --workers "{WORKER}"'
            self.run_command(self.virtual_env, cmd, target_subdirectory)
            
            self.finished.emit()  # Emit the finished signal when done
        except Exception as e:
            logging.error(f"An error occurred during training: {e}", exc_info=True)
            self.error.emit(str(e))  # Emit an error signal with the exception message

    def run_command(self, virtual_env, command, target_subdirectory=None, exit_cmd = False):
        """
        Execute a command in the shell.
        """
        try:
            # switch to the target subdirectory
            if target_subdirectory is not None:
                cwd = os.getcwd()
                os.chdir(target_subdirectory)
                print(f"Original directory: {cwd}")
                print(f"Target directory: {target_subdirectory}")
                print(f"Current directory after change: {os.getcwd()}")
                print(f"Executing command: {command}")

            # run the command in a new cmd window and activate the conda environment
            if exit_cmd:
                process = subprocess.Popen(f'start /wait cmd /c "conda activate {virtual_env} && {command} && exit"', shell=True)
            else:
                process = subprocess.Popen(f'start /wait cmd /k "conda activate {virtual_env} && {command}"', shell=True)
                
            
            # Wait for the process to finish, which will happen when the user closes the cmd window
   
            process.wait()  # Blocks until the process is finished or closed by the user
            logging.info("Command finished execution.")

            # switch back to the original directory
            if target_subdirectory is not None:
                os.chdir(cwd)
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.strip()
            print(f"Error executing command: {e}")
            raise e
