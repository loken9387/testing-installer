import csv
import os
import subprocess
import shutil

packages = []
with open('../trexinstaller/packages.csv', 'r') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        packages.append(row)

download_dir = "~/git/trexinstaller/offline/debFiles/"

os.makedirs(download_dir, exist_ok=True)

for package in packages:
    try:
        subprocess.run(f"apt-get download {package}", shell=True, check=True, cwd=download_dir)
    except subprocess.CalledProcessError as e:
        print(f"Failed to download package: {package}. Error: {e}")
        
# Create a compressed archive of the downloaded packages
archive_name = "packages.tar.gz"
subprocess.run(f"tar -czvf {archive_name} -C {download-dir} .", shell=True, check=True)
