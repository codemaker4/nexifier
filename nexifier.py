# Look at the downloads folder, and wait for a new file to appear.
# When it does, unzip it in place and look for a .htlm file.

import os
import time
import shutil
import subprocess
import sys

# Path to the downloads folder and a temporary folder to unzip the files
if os.name == "nt":
    downloads = os.path.expanduser("~\\Downloads")
    unzipped = os.path.expanduser("~\\Downloads\\nexifier_temp")
elif os.name == "posix":
    downloads = os.path.expanduser("~/Downloads")
    unzipped = os.path.expanduser("~/Downloads/nexifier_temp")
else:
    print("Unsupported operating system")


# wait for a new file to appear in the downloads folder
def wait_for_new_file():
    current_files = set(os.listdir(downloads))
    while True:
        time.sleep(0.1)
        new_files = set(os.listdir(downloads))
        diff = new_files - current_files
        if diff:
            new_file = diff.pop()
            # Check if the new file has a .part extension
            if new_file.endswith('.part') or new_file.endswith('.crdownload'):
                print(f"Waiting for {new_file} to finish downloading...")
                continue  # Continue waiting if the file is still downloading
            else:
                # Wait for the file to be completely written to disk
                time.sleep(0.1)
                return new_file


# cross platform general file opener
def open_file(file):
    print("Opening file:", file)
    if os.name == "posix":
        if sys.platform == "darwin":
            subprocess.run(["open", file])
        else:
            subprocess.run(["xdg-open", file])
    elif os.name == "nt":
        os.startfile(file)
    else:
        print("Unsupported operating system")


# process a downloaded zip file
def process_file(file):
    filetypes = [".html", ".txt", ".blend"]
    try:
        if file.endswith(".zip"):
            print("Removing old unzipped files...")
            shutil.rmtree(unzipped, ignore_errors=True)
            print("Unzipping...")
            shutil.unpack_archive(os.path.join(downloads, file), unzipped)
            print("Looking for known filetypes...")
            for root, dirs, files in os.walk(unzipped):
                for file in files:
                    for filetype in filetypes:
                        if file.endswith(filetype):
                            open_file(os.path.join(root, file))
                            return
            print("No known filetypes found, opening folder...")
            # open the folder
            open_file(unzipped)
        else:
            print("Looking for known filetypes...")
            for filetype in filetypes:
                if file.endswith(filetype):
                    open_file(os.path.join(downloads, file))
                    return
            print("The file is not a zip file or a known filetype. It won't be opened.")
    except Exception as e:
        print("Error in processing file:", e)


while True:
    print("Waiting for a new file...")
    new_file = wait_for_new_file()
    print("New file:", new_file)
    process_file(new_file)
