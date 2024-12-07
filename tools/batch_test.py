
import numpy as np
import os
import shutil
from PyQt5.QtCore import QThread, pyqtSignal
import logging
import subprocess



class TestingThread(QThread):
    testing_complete = pyqtSignal(str)

    def __init__(self, checkpoint_path, config_file, virtual_env):
        super().__init__()

        self.checkpoint_path = checkpoint_path
        self.config_file = config_file
        self.virtual_env = virtual_env

    def run(self):
        logging.info("Running model testing in a separate thread...")
        try:

            print(self.checkpoint_path)
            print(self.config_file)
            # Prepare the command for testing
            cmd = f'set CUDA_LAUNCH_BLOCKING=1 && python test.py --cfg_file "{self.config_file}" --ckpt "{self.checkpoint_path}"'
            target_subdirectory = os.path.join('..', 'tools')
            
            # Run the command
            self.run_command(self.virtual_env, cmd, target_subdirectory)
            
            # Emit signal when testing is complete
            self.testing_complete.emit("Testing completed successfully.")
        except Exception as e:
            logging.error(f"An error occurred during testing: {e}", exc_info=True)
            self.testing_complete.emit(f"An error occurred during testing: {str(e)}")
            
    def run_command(self, virtual_env, command, target_subdirectory=None):
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
