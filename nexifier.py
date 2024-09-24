# Look at the downloads folder, and wait for a new file to appear.
# When it does, unzip it in place and look for a .htlm file.

import os
import time
import shutil
import subprocess
import sys

# Path to the downloads folder
downloads = os.path.expanduser("~/Downloads")

# Path to the folder where the unzipped files will be stored
unzipped = os.path.expanduser("~/Downloads/nexifier_temp")


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
            if new_file.endswith('.part'):
                print(f"Waiting for {new_file} to finish downloading...")
                continue  # Continue waiting if the file is still downloading
            else:
                # Wait for the file to be completely written to disk
                time.sleep(0.1)
                return new_file


# cross platform general file opener
def open_file(file):
    if os.name == "posix":
        if sys.platform == "darwin":
            subprocess.run(["open", file])
        else:
            subprocess.run(["xdg-open", file])
    elif os.name == "nt":
        subprocess.run(["start", file])
    else:
        print("Unsupported operating system")


# process a downloaded zip file
def process_file(file):
    try:
        if file.endswith(".zip"):
            print("Removing old unzipped files...")
            shutil.rmtree(unzipped, ignore_errors=True)
            print("Unzipping...")
            shutil.unpack_archive(os.path.join(downloads, file), unzipped)
            for root, dirs, files in os.walk(unzipped):
                for file in files:
                    if file.endswith(".html"):
                        open_file(os.path.join(root, file))
                        return
            print("No .html file found")
            # open the folder
            open_file(unzipped)
        else:
            print("Not a zip file")
    except Exception as e:
        print("Error in processing file:", e)


while True:
    print("Waiting for a new file...")
    new_file = wait_for_new_file()
    print("New file:", new_file)
    process_file(new_file)
