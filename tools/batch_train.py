import open3d as o3d
import numpy as np
import os
import shutil
from PyQt5.QtCore import QThread, pyqtSignal
import json
import copy
import logging
import subprocess

from tools.batch_preprocess import read_all_json_files

class TrainingThread(QThread):
    # Define signals to communicate back to the main thread
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, training_data_dir, label_data_dir):
        super().__init__()
        self.training_data_dir = training_data_dir
        self.label_data_dir = label_data_dir

    def run(self):
        try:
            read_all_json_files(self.label_data_dir, self.training_data_dir)
            PC_MF=20
            DXDY_MF=0.85
            NAME='custom'
            CFG_FILE_ABS = os.path.abspath(os.path.join('..', 'tools', 'cfgs', 'custom_models', 'pointpillar.yaml'))
            print(CFG_FILE_ABS)
            cmd = f'python convert_raw_data.py --name "{NAME}" --dir "{self.label_data_dir}" --cfg_file "{CFG_FILE_ABS}" --pc_mf "{PC_MF}" --dxdy_mf "{DXDY_MF}"'
            target_subdirectory = os.path.join('..', 'tools')
            self.run_command(cmd, target_subdirectory)
            
            DATASET_CFG_FILE_ABS = os.path.abspath(os.path.join('..', 'tools', 'cfgs', 'dataset_configs', 'custom_dataset.yaml'))
            print(DATASET_CFG_FILE_ABS)
            cmd = f'set CUDA_LAUNCH_BLOCKING=1 && python -m pcdet.datasets.custom.custom_dataset create_custom_infos {DATASET_CFG_FILE_ABS}'
            self.run_command(cmd)
            
            EPOCH = 100
            BATCH_SIZE = 4
            WORKER = 1
            cmd = f'set CUDA_LAUNCH_BLOCKING=1 && python train.py --cfg_file "{CFG_FILE_ABS}" --epochs "{EPOCH}" --batch_size "{BATCH_SIZE}" --workers "{WORKER}"'
            self.run_command(cmd, target_subdirectory)
            
            self.finished.emit()  # Emit the finished signal when done
        except Exception as e:
            logging.error(f"An error occurred during training: {e}", exc_info=True)
            self.error.emit(str(e))  # Emit an error signal with the exception message

    def run_command(self, command, target_subdirectory=None):
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
            process = subprocess.Popen(f'start /wait cmd /k "conda activate windowspointcloud && {command}"', shell=True)
            
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

