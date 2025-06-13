#!/bin/bash

# Define the desktop entry content
desktop_entry="[Desktop Entry]
Version=1.0
Type=Application
Name=TREX
Exec=/opt/google/chrome/google-chrome --profile-directory=Default --ignore-profile-directory-if-not-exists http://localhost:8080
Icon="$HOME/git/launch/nodeConfigWizard.png"
URL=http://localhost:8080
Comment=Open http://localhost:8080/map in a new tab in Google Chrome.
Terminal=false"

# Create the .desktop file on the desktop
echo "$desktop_entry" > ~/Desktop/localhost.desktop

# Make the .desktop file executable
chmod +x ~/Desktop/localhost.desktop

echo "Desktop icon created successfully."
