import os # Import os for file path and directory operations
import subprocess # Import subprocess to run external commands like pip and pyinstaller
import sys # Import sys for system-specific parameters and functions

def build_game(): # Function to handle the PyInstaller build steps
    print("--- Starting Cogni-Quest Build Process ---") # Log start of the build process to the console
    
    # 1. Install PyInstaller if not present
    try: # Begin a try block to check for PyInstaller availability
        import PyInstaller # Attempt to import PyInstaller module
    except ImportError: # Catch error if PyInstaller is not installed
        print("Installing PyInstaller...") # Log that an installation is required
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"]) # Execute pip install via subprocess

    # 2. Run PyInstaller
    # --onefile: Bundles all dependencies and code into a single executable file
    # --noconsole: Prevents a black terminal/command prompt window from appearing when the game is launched
    # --name: Specifies the final filename of the generated executable
    # --add-data: Can be used to include images/fonts (not used yet as we use procedural assets)
    
    command = [ # Define the list of command arguments for PyInstaller
        "pyinstaller", # The main command to execute
        "--noconsole", # Flag to hide the console window
        "--onefile", # Flag to produce a single .exe file
        "--name=CogniQuest", # Flag to set the output name
        "main_game.py" # The entry point script to compile
    ]
    
    print(f"Running command: {' '.join(command)}") # Log the full command string for debugging
    
    try: # Begin a try block to execute the build command
        subprocess.check_call(command) # Run PyInstaller and wait for it to finish
        print("\nSUCCESS! Your standalone executable is in the 'dist' folder.") # Log success
        print("File: dist/CogniQuest.exe") # Log the exact location of the output
    except subprocess.CalledProcessError as e: # Catch error if the command fails (e.g., syntax errors in main_game.py)
        print(f"\nBUILD FAILED: {e}") # Log the specific error message
        sys.exit(1) # Exit the script with a failure code

if __name__ == "__main__": # Standard Python entry point check
    # Check if main_game.py exists
    if not os.path.exists("main_game.py"): # Ensure the script to be built is actually present
        print("Error: main_game.py not found in the current directory.") # Log error if missing
    else: # If the entry point exists
        build_game() # Proceed to call the build function
