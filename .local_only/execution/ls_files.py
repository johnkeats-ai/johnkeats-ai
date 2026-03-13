import os
import subprocess

def list_files():
    """Lists files in the current directory using `ls -R`."""
    print("Listing workspace files...")
    try:
        result = subprocess.run(["ls", "-R"], capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"Error listing files: {e}")

if __name__ == "__main__":
    list_files()
