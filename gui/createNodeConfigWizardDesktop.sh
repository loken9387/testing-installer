#!/bin/bash

NODE_WIZARD_USER="${NODE_WIZARD_USER:-xmmgr}"
HOME="/home/$NODE_WIZARD_USER"

node_config_wizard="$HOME/launch/nodeConfigWizard"
desktop_file="/usr/share/applications/nodeConfigWizard.desktop"

sudo tee "$desktop_file" > /dev/null <<EOT
[Desktop Entry]
Version=1.0
Type=Application
Name=Node Config Wizard
Exec="$node_config_wizard"
Icon="$HOME/launch/nodeConfigWizard.png"
Terminal=false
EOT

sudo chmod +x "$desktop_file"

for user_home in /home/*; do
    desktop_dir="$user_home/Desktop"
    if [ -d "$desktop_dir" ]; then
        sudo ln -sf "$desktop_file" "$desktop_dir/nodeConfigWizard.desktop"
    fi
done
