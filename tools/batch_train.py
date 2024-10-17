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

from tools.batch_preprocess import read_all_json_files

class TrainingThread(QThread):
    # Define signals to communicate back to the main thread
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, training_data_dir, label_data_dir, batch_size, learning_rate, epochs, backbone, point_cloud_magnification, label_magnification):
        super().__init__()
        self.training_data_dir = training_data_dir
        self.label_data_dir = label_data_dir
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.backbone = backbone
        self.point_cloud_magnification = point_cloud_magnification
        self.label_magnification = label_magnification

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
            cmd = f'python convert_raw_data.py --name "{NAME}" --dir "{self.label_data_dir}" --cfg_file "{CFG_FILE_ABS}" --pc_mf "{self.point_cloud_magnification}" --dxdy_mf "{self.label_magnification}"'
            target_subdirectory = os.path.join('..', 'tools')
            self.run_command(cmd, target_subdirectory, exit_cmd = True)
            
            DATASET_CFG_FILE_ABS = os.path.abspath(os.path.join('..', 'tools', 'cfgs', 'dataset_configs', 'custom_dataset.yaml'))
            print(DATASET_CFG_FILE_ABS)
            cmd = f'set CUDA_LAUNCH_BLOCKING=1 && python -m pcdet.datasets.custom.custom_dataset create_custom_infos {DATASET_CFG_FILE_ABS}'
            self.run_command(cmd, exit_cmd = True)
            
            #EPOCH = 100
            #BATCH_SIZE = 4
            WORKER = 1
            cmd = f'set CUDA_LAUNCH_BLOCKING=1 && python train.py --cfg_file "{CFG_FILE_ABS}" --lr "{self.learning_rate}" --epochs "{self.epochs}" --batch_size "{self.batch_size}" --workers "{WORKER}"'
            self.run_command(cmd, target_subdirectory)
            
            self.finished.emit()  # Emit the finished signal when done
        except Exception as e:
            logging.error(f"An error occurred during training: {e}", exc_info=True)
            self.error.emit(str(e))  # Emit an error signal with the exception message

    def run_command(self, command, target_subdirectory=None, exit_cmd = False):
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
                process = subprocess.Popen(f'start /wait cmd /c "conda activate windowspointcloud && {command} && exit"', shell=True)
            else:
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
