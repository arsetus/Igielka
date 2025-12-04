import requests
import os
import sys
import importlib.util

# Imports to ensure PyInstaller bundles these dependencies
if False:
    import PyQt5
    import PyQt5.QtWidgets
    import PyQt5.QtCore
    import PyQt5.QtGui
    import win32gui
    import win32process
    import win32api
    import win32con
    import numpy
    import cv2
    import PIL
    import bs4

REPO_OWNER = "arsetus"
REPO_NAME = "Igielka"
BRANCH = "main"

def update_from_github():
    print("Checking for updates...")
    try:
        # Get the file tree
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/trees/{BRANCH}?recursive=1"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to get file list: {response.status_code}")
            return

        tree = response.json().get("tree", [])
        
        for item in tree:
            path = item["path"]
            type_ = item["type"]
            
            # Skip directories we don't want to overwrite or that are system/build related
            if path.startswith("Save") or path.startswith(".git") or path.startswith("__pycache__") or path.startswith("build") or path.startswith("dist") or path.endswith(".spec"):
                continue
            
            # Map Igielka.py from repo to MainApp.py locally
            if path == "Igielka.py":
                local_path = "MainApp.py"
            else:
                local_path = path

            if type_ == "blob": # It's a file
                download_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/{path}"
                
                # Ensure directory exists
                dir_name = os.path.dirname(local_path)
                if dir_name and not os.path.exists(dir_name):
                    os.makedirs(dir_name, exist_ok=True)
                
                print(f"Downloading {path} as {local_path}...")
                file_response = requests.get(download_url)
                if file_response.status_code == 200:
                    with open(local_path, "wb") as f:
                        f.write(file_response.content)
                else:
                    print(f"Failed to download {path}")
                    
    except Exception as e:
        print(f"Update failed: {e}")
        print("Continuing with existing files...")

def main():
    # Run update
    update_from_github()
    
    # Add current directory to sys.path to ensure we load the downloaded files
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())
    
    print("Starting application...")
    
    # Dynamic import of MainApp to avoid bundling it at build time (if possible) 
    # and to ensure we load the fresh version from disk.
    try:
        spec = importlib.util.spec_from_file_location("MainApp", os.path.join(os.getcwd(), "MainApp.py"))
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules["MainApp"] = module
            spec.loader.exec_module(module)
            module.main()
        else:
            print("Could not find MainApp.py")
            input("Press Enter to exit...")
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
