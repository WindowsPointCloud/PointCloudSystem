import subprocess
import os

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
        subprocess.run(command, shell=True, check=True)
        
        # switch back to original directory
        if target_subdirectory is not None:
            os.chdir(cwd)
            
        import torch
        torch.cuda.empty_cache()
        
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
