import subprocess
import os

def play_sound(file_path):
    """
    Play a sound file using ffplay.
    """
    if not os.path.exists(file_path):
        print(f"Error: Sound file '{file_path}' not found.")
        return

    try:
        subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", file_path],
            stdout=subprocess.DEVNULL,  # Suppress standard output
            stderr=subprocess.DEVNULL   # Suppress error output
        )
        print("playing sound")
    except FileNotFoundError:
        print("Error: 'ffplay' is not installed or not found in PATH.")