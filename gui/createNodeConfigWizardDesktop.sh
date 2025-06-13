#!/bin/bash

node_config_wizard="$HOME/launch/nodeConfigWizard"

cat <<EOT > "$HOME/Desktop/nodeConfigWizard.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=Node Config Wizard
Exec="$node_config_wizard"
Icon="$HOME/launch/nodeConfigWizard.png"
Terminal=false
EOT

chmod +x "$HOME/Desktop/nodeConfigWizard.desktop"
