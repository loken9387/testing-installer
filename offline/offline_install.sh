#!/bin/bash

# sudo apt-get update -y # Updates apt package index
sudo apt-get upgrade -y

# Path to the thumb drive (replace with the actual path where your thumb drive is mounted)
THUMB_DRIVE_PATH="/home/xmmgr/Documents/installWizard/offlineInstall/"

# Check if the thumb drive path exists
if [ ! -d "$THUMB_DRIVE_PATH" ]; then
  echo "The thumb drive path $THUMB_DRIVE_PATH does not exist."
  exit 1
fi

# declare -a packages=(
# "lm-sensors"
# ,"vim"
# ,"openssh-server"
# ,"gcc"
# ,"xrdp"
# ,"minicom"
# ,"screen"
# ,"dos2unix"
# ,"find"
# ,"mlocate"
# ,"docker"
# ,"./google-chrome-stable_current_amd64.deb"
# ,"tigervnc-viewer"
# ,"docker-compose"
# ,"tigervnc-standalone-server"
# ,"dbus-x11"
# ,"net-tools"
# ,"selinux-utils"
# )

# Find all .deb files in the thumb drive directory
DEB_FILES=$(find "$THUMB_DRIVE_PATH" -name "*.deb")

if [ -z "$DEB_FILES" ]; then
  echo "No .deb files found on the thumb drive."
  exit 0
fi

# Install each .deb file
for DEB_FILE in $DEB_FILES;
do
  echo "Installing $DEB_FILE..."
  sudo dpkg -i "$DEB_FILE"
  if [ $? -eq 0 ]; then
    echo "Successfully installed $DEB_FILE"
  else
    echo "Failed to install $DEB_FILE"
  fi
done


# dpkg -i $DEB_FILe lm-sensors
# dpkg -i vim
# dpkg -i openssh-server
# dpkg -i gcc
# dpkg -i xrdp
# dpkg -i minicom
# dpkg -i screen
# dpkg -i dos2unix
# dpkg -i find
# dpkg -i mlocate
# dpkg -i docker
# dpkg -i ./google-chrome-stable_current_amd64.deb
# dpkg -i tigervnc-viewer
# dpkg -i docker-compose
# dpkg -i tigervnc-standalone-server
# dpkg -i dbus-x11
# dpkg -i net-tools
# dpkg -i selinux-utils

echo "Installation process completed."
# sudo dpkg -i apt install openssh-server -y # Installs openssh-server
sudo systemctl start ssh # Starts ssh
sudo systemctl enable ssh --now # Enables ssh now
# # sudo systemctl status ssh # Checks status of ssh
# # TODO: Provide logic to check ssh status
# sudo systemctl enable ssh # Enables ssh
sudo ufw disable # Disbales firewall
sudo ufw allow ssh # Allows port 22 to be used
# sudo apt install vim -y # Installs vim
# sudo apt install mlocate -y # Installs locate 
# sudo apt install find # Installs find
# sudo apt install tigervnc-standalone-server -y # Installs Tigervncserver
# sudo apt install tigervnc-viewer -y # Installs Tigervncviewer
# sudo apt install docker-compose -y
# sudo apt install net-tools -y # Installs net-tools
# sudo apt install selinux-utils -y # Installs selinux-utils
# sudo apt install gcc -y # Installs gcc
# sudo apt install dbus-x11 -y #Installs package needed to change gedit color scheme
# sudo apt install xrdp -y #Installs xrdp
# sudo systemctl start xrdp #Starts xrdp
sudo systemctl enable xrdp #Enables xrdp
# sudo apt install minicom -y #installs minicom to look at hoover stack
# sudo apt install screen -y #installs screen to look at gps
# sudo apt install dos2unix # used for cpu testing to convert windows file to linux
# sudo apt install lm-sensors -y #install senors for cpu testing
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor #sets correct performance mode
xhost +
#sudo apt install docker-ce # Installs docker-ce
# sudo apt install docker -y # Installs docker
# sudo apt install ./google-chrome-stable_current_amd64.deb -y # Installs google-chrome
chmod +x usrp.sh
chmod +x resizeusrp.sh
chmod +x pullinglaunch.sh
chmod +x hosts.sh
sudo ./hosts.sh
# cat /etc/hosts
sudo cp -r /home/xmmgr/ubuntu/recordings /home/xmmgr
sudo groupadd docker
sudo groupadd -f docker
# #sudo newgrp docker
sudo usermod -aG docker xmmgr
chmod +x daemon.sh
sudo ./daemon.sh
# #cat /etc/docker/daemon.json
sudo systemctl restart docker
sudo systemctl enable docker
sudo systemctl restart docker
sudo systemctl enable docker
sudo systemctl status docker
# #sudo apt-get install chrony -y
# #sudo cp chrony.conf /etc/chrony/chrony.conf
# #service chrony rest
# #Changing rmem  and wmem for usrp to work properly
sudo sysctl -w net.core.rmem_max=24912805
sudo sysctl -w net.core.wmem_max=24912805
# #sudo cp -r /home/xmmgr/ubuntu/recordings /home/xmmgr
sudo chmod +x /home/xmmgr/recordings/usrp.sh
sudo ./hosts.sh
ssh-keygen
# # Go into home directory
# # Make a new directory called git
cd
mkdir /home/xmmgr/git
sudo chgrp -R xmmgr /home/xmmgr/git
sudo chown -R xmmgr /home/xmmgr/git
# docker login docker-dev.artifactory.parsons.us
# # Go into the git directory and Clone launch
# read -p "Enter the branch name you want to clone: " branch_name
# cd git | git clone ssh://git@git.parsons.us:7999/trex/launch.git --branch "$branch_name"
tar -xvzf launchRepo.tar.gz
# #cd git | #git clone ssh://git@git.parsons.us:7999/trex/launch.git --branch release/v2.3.3
# #cd git | #git clone http://10.107.65.5/trex2/launch.git --branch release/v2.3.0
# #cd git | #git clone https://bitbucket.parsons.us/scm/trex/launch.git --branch release/v2.3.0
# #ssh://git@git.parsons.us:7999/trex/launch.git
sudo rm -r /home/xmmgr/git/launch
sudo mv launch /home/xmmgr/git/ #Move launch to correct area
mkdir /home/xmmgr/recordings
mkdir /home/xmmgr/recordings/dc_calibration
# # Changing Permissions
sudo chgrp -R xmmgr /home/xmmgr/git/launch
sudo chown -R xmmgr /home/xmmgr/git/launch
sudo chgrp -R xmmgr /home/xmmgr/recordings
sudo chown -R xmmgr /home/xmmgr/recordings
sudo chgrp -R xmmgr /home/xmmgr/recordings/dc_calibration
sudo chown -R xmmgr /home/xmmgr/recordings/dc_calibration
sudo cp /home/xmmgr/installer/dc_calibration.sh /home/xmmgr/recordings/dc_calibration/
sudo ./hosts.sh
# #cat /etc/hosts
sudo cp /home/xmmgr/installer/monitors.xml /home/xmmgr/.config/
sudo cp -i /home/xmmgr/.config/monitors.xml /var/lib/gdm3/.config/
cd /home/xmmgr/git/launch
cd /home/xmmgr/git/launch/ | source trex_environment.sh
sleep 2
cd /home/xmmgr/git/launch/scripts/
./launchCompose.sh
