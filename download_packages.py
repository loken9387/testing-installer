import csv
import os
import subprocess
import shutil

packages = []
packages_file = "packages.csv"
with open(packages_file, "r", newline="") as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        if not row:
            continue
        packages.append(row[0].strip())

download_dir = os.path.expanduser("~/git/trexinstaller/offline/debFiles/")

os.makedirs(download_dir, exist_ok=True)

for package in packages:
    try:
        subprocess.run(f"apt-get download {package}", shell=True, check=True, cwd=download_dir)
    except subprocess.CalledProcessError as e:
        print(f"Failed to download package: {package}. Error: {e}")
        
# Create a compressed archive of the downloaded packages
archive_name = "packages.tar.gz"
subprocess.run(f"tar -czvf {archive_name} -C {download_dir} .", shell=True, check=True)
