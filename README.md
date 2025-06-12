# Install GUI

## Instructions:
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

## Notes:
-on linux, you may need to reinstall libxcv-cursor0 if you encounter an erro from xcb
->>>>>>sudo apt-get update
        sudo apt-get install libxcb-cursor0
        sudo apt-get reinstall xcb
-give user xmmgr access to commands normally restricted to sudo:
->>>>>>change /etc/sudoers file with: `username ALL=(ALL) NOPASSWD: command_path`
->>>>>>trex_environment.sh needs to be changed from rc5 to rc6 and from docker-dev to docker-trex

### Offline package directory
The offline installers now look for required `.deb` files in a folder located
next to the installer script. Place your packages inside a directory named
`dependencies` when using `install_gui.py` or `offlineInstall` when running
`offline_install.py` or `offline_install.sh`.
