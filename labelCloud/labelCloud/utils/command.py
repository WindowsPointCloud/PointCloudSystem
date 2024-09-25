import subprocess
import os
import torch
import logging

def run_command(command, target_subdirectory=None):
    """
    Execute a command in the shell.
    """
    try:
        # switch to the target subdirectory
        if target_subdirectory is not None:
            cwd = os.getcwd()
            os.chdir(target_subdirectory)
            print(cwd)
            print(target_subdirectory)
            print(os.getcwd())
            print(command)

        # run the command
        output = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        
        # switch back to original directory
        if target_subdirectory is not None:
            os.chdir(cwd)
            
        
        torch.cuda.empty_cache()
        
        return output
        
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip()
        print(f"Error executing command: {e}")
        return None, error_message
        

