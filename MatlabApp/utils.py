# MatlabApp/utils.py
import os

#Path to File
COMMAND_FILE = os.path.join(os.path.dirname(__file__), 'commands.csv')

def save_command_to_file(command):
    """Append a command to the CSV file for MATLAB to read."""
    with open(COMMAND_FILE, 'a') as f:
        f.write(f"{command}\n")
