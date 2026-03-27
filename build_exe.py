import os
import subprocess
import sys

def build_game():
    print("--- Starting Cogni-Quest Build Process ---")
    
    # 1. Install PyInstaller if not present
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 2. Run PyInstaller
    # --onefile: Bundle everything into a single .exe
    # --noconsole: Don't show the command prompt window when running
    # --name: Name of the output file
    # --add-data: Include relevant files (though we don't have many external assets yet)
    
    command = [
        "pyinstaller",
        "--noconsole",
        "--onefile",
        "--name=CogniQuest",
        "main_game.py"
    ]
    
    print(f"Running command: {' '.join(command)}")
    
    try:
        subprocess.check_call(command)
        print("\nSUCCESS! Your standalone executable is in the 'dist' folder.")
        print("File: dist/CogniQuest.exe")
    except subprocess.CalledProcessError as e:
        print(f"\nBUILD FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Check if main_game.py exists
    if not os.path.exists("main_game.py"):
        print("Error: main_game.py not found in the current directory.")
    else:
        build_game()
