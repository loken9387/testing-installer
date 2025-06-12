#!/bin/bash

# Install Python (assuming a Debian-based system)
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install -y python3
sudo apt-get install -y python3-pip
sudo apt-get reinstall libxcb-cursor0
sudo apt-get reinstall xcb
pip3 install pyqt6
python3 /home/xmmgr/git/trexinstaller/gui/install_gui.py
