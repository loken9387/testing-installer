# Install GUI

## Instructions:
The installer GUI installs all required packages from the internet using `apt`.
Ensure the machine running the installer has network access.

### Build the GUI
1. cd ~
2. mkdir git
3. cd git
4. git clone https://bitbucket.parsons.us/scm/trex/trexinstaller.git --branch Automatic-Install-GUI
5. cd trexinstaller
6. cp myscript.desktop ~/Desktop/myscript.desktop
## (Skip if not editing code and just running install script) Build a python executable
1. cd ~/git/trexinstaller/gui
2. sudo apt install python3.10-venv
3. python3 -m venv myenv 
4. source myenv/bin/activate 
5. pip install -r requirements.txt 
6. pip install pyinstaller 
7. pyinstaller --onefile install_gui.py 
8. deactivate
## Launching the script from the desktop
1. right click on desktop icon, select properties, under permissions, select None for "Others Access"
2. right click on desktop icon "Install TReX" and select allow launching
3. double click icon to launch script
4. After installation completes, a `nodeConfigWizard.desktop` file will appear
   on your Desktop. Double-click it to run the Node Config Wizard executable.

## Notes:
-on linux, you may need to reinstall libxcv-cursor0 if you encounter an erro from xcb
->>>>>>sudo apt-get update
        sudo apt-get install libxcb-cursor0
        sudo apt-get reinstall xcb
-give user xmmgr access to commands normally restricted to sudo:
->>>>>>change /etc/sudoers file with: `username ALL=(ALL) NOPASSWD: command_path`
->>>>>>trex_environment.sh needs to be changed from rc5 to rc6 and from docker-dev to docker-trex

### Installing Packages
The file `packages.csv` lists each package the installer will install. Place
this file in the same directory as the `install_gui` executable. During
installation the GUI will run `apt-get install` for every entry in the CSV, so
an internet connection is required.

### Running the Installer
1. Build the GUI on a development machine using PyInstaller:
   ```bash
   cd gui
   pyinstaller --onefile install_gui.py
   ```
   The executable will be placed in `gui/dist/`.
2. Copy `packages.csv`, `launch.tar`, and the Docker image archives
   (`postgres.tar.gz`, `node-webserver.tar.gz`, `services.tar.gz`,
   `signal.tar.gz`, and `client.tar.gz`) next to the executable.
3. Execute the installer and follow the prompts. The script will download and
   install each package before loading the Docker images and extracting
   `launch.tar`.
4. After installation completes the system will automatically shut down so you
   can power cycle the machine.
