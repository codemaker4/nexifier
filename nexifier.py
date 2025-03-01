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
def wait_for_new_file(max_seconds=60*10):
    current_files = set(os.listdir(downloads))
    start_time = time.time()
    while time.time() - start_time < max_seconds:
        time.sleep(0.1)
        new_files = set(os.listdir(downloads))
        diff = new_files - current_files
        if diff:
            new_file = diff.pop()
            # Check if the new file has a temporary extension
            temp_extensions = ['.part', '.crdownload', '.tmp', '.download']
            if any(new_file.endswith(ext) for ext in temp_extensions):
                print(f"Waiting for {new_file} to finish downloading...")
                continue  # Continue waiting if the file is still downloading
            else:
                # Wait for the file to be completely written to disk
                time.sleep(0.1)
                return new_file
    print("No new files found after waiting for", max_seconds, "seconds")
    return None


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
    # List of known filetypes to look for, in order of preference.
    filetypes = ["index.html", ".html",
                 ".blend",
                 ".txt", ".rtf", ".pdf", ".docx", ".doc", ".odt",
                 ".png", ".jpg", ".jpeg", ".mp4", ".mkv", ".llsp3"]
    try:
        if file.endswith(".zip"):
            print("Removing old unzipped files...")
            shutil.rmtree(unzipped, ignore_errors=True)
            print("Unzipping...")
            shutil.unpack_archive(os.path.join(downloads, file), unzipped)
            os.remove(os.path.join(downloads, file))
            print("Looking for known filetypes...")
            best_file = None
            file_niceness = 1e9  # Lower is better
            for root, dirs, files in os.walk(unzipped):
                for file in files:
                    for niceness, filetype in enumerate(filetypes):
                        if file.endswith(filetype) and niceness < file_niceness:
                            best_file = os.path.join(root, file)
                            file_niceness = niceness
            if best_file:
                open_file(os.path.join(root, best_file))
                return
            print("No known filetypes found, opening folder...")
            # open the folder
            open_file(unzipped)
        else:
            print("Looking for known filetypes...")
            for filetype in filetypes:
                if file.endswith(filetype):
                    break
            else:
                print("No known filetypes found")
                return
            print("Putting file in an emptied unzipped folder...")
            shutil.rmtree(unzipped, ignore_errors=True)
            os.makedirs(unzipped, exist_ok=True)
            shutil.move(os.path.join(downloads, file), os.path.join(unzipped, file))
            open_file(os.path.join(unzipped, file))
    except Exception as e:
        print("Error in processing file:", e)


while True:
    print("Waiting for a new file...")
    new_file = wait_for_new_file()
    if not new_file:
        break
    print("New file:", new_file)
    if os.name == "nt": # idk why, but on Windows I have to wait a little extra.
        time.sleep(0.5) # otherwise it throws "not a zip file" errors.
    process_file(new_file)

print("stopping...")
