#!/bin/bash

# Check if the machine has openssh server
# ssh -V

# Add sudoers
# ./add_sudoers.sh
docker_username=$1
docker_password=$2

echo "COMMAND: Updating package index"
sudo apt-get update -y # Updates apt package index
echo "COMMAND_DONE"


echo "COMMAND: Upgrading packages"
sudo apt-get upgrade -y
echo "COMMAND_DONE"

echo "COMMAND: Installing openssh-server"
sudo apt install openssh-server -y # Installs openssh-server
echo "COMMAND_DONE"

echo "COMMAND: Starting ssh"
sudo systemctl start ssh # Starts ssh
echo "COMMAND_DONE"

echo "COMMAND: Enabling ssh"
sudo systemctl enable ssh --now # Enables ssh now
echo "COMMAND_DONE"

# Check status of ssh
# sudo systemctl status ssh

# TODO: Provide logic to check ssh status

echo "COMMAND: Enabling ssh"
sudo systemctl enable ssh # Enables ssh
echo "COMMAND_DONE"

echo "COMMAND: Disabling firewall"
sudo ufw disable # Disables firewall
echo "COMMAND_DONE"


echo "COMMAND: Allowing ssh through firewall"
sudo ufw allow ssh # Allows port 22 to be used
echo "COMMAND_DONE"

echo "COMMAND: Installing vim"
sudo apt install vim -y # Installs vim
echo "COMMAND_DONE"

echo "COMMAND: Installing mlocate"
sudo apt install mlocate -y # Installs locate
echo "COMMAND_DONE"

echo "COMMAND: Installing find"
sudo apt install find # Installs find
echo "COMMAND_DONE"

echo "COMMAND: Installing tigervnc-standalone-server"
sudo apt install tigervnc-standalone-server -y # Installs Tigervncserver
echo "COMMAND_DONE"

echo "COMMAND: Installing tigervnc-viewer"
sudo apt install tigervnc-viewer -y # Installs Tigervncviewer
echo "COMMAND_DONE"

echo "COMMAND: Installing docker-compose"
sudo apt install docker-compose -y
echo "COMMAND_DONE"

echo "COMMAND: Installing net-tools"
sudo apt install net-tools -y # Installs net-tools
echo "COMMAND_DONE"

echo "COMMAND: Installing selinux-utils"
sudo apt install selinux-utils -y # Installs selinux-utils
echo "COMMAND_DONE"

echo "COMMAND: Installing gcc"
sudo apt install gcc -y # Installs gcc
echo "COMMAND_DONE"

echo "COMMAND: Installing dbus-x11"
sudo apt install dbus-x11 -y # Installs package needed to change gedit color scheme
echo "COMMAND_DONE"

echo "COMMAND: Installing xrdp"
sudo apt install xrdp -y # Installs xrdp
echo "COMMAND_DONE"

echo "COMMAND: Starting xrdp"
sudo systemctl start xrdp # Starts xrdp
echo "COMMAND_DONE"

echo "COMMAND: Enabling xrdp"
sudo systemctl enable xrdp # Enables xrdp
echo "COMMAND_DONE"

echo "COMMAND: Installing minicom"
sudo apt install minicom -y # Installs minicom to look at hoover stack
echo "COMMAND_DONE"

echo "COMMAND: Installing screen"
sudo apt install screen -y # Installs screen to look at gps
echo "COMMAND_DONE"

echo "COMMAND: Installing dos2unix"
sudo apt install dos2unix # Used for CPU testing to convert Windows file to Linux
echo "COMMAND_DONE"

echo "COMMAND: Installing lm-sensors"
sudo apt install lm-sensors -y # Installs sensors for CPU testing
echo "COMMAND_DONE"

echo "COMMAND: Setting performance mode"
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor # Sets correct performance mode
echo "COMMAND_DONE"

echo "COMMAND: Allowing connections from any host"
xhost +
echo "COMMAND_DONE"

# Install docker-ce
# sudo apt install docker-ce


echo "COMMAND: Installing docker"
sudo apt install docker -y # Installs docker
echo "COMMAND_DONE"

echo "COMMAND: Installing Google Chrome"
sudo apt install ./google-chrome-stable_current_amd64.deb -y # Installs Google Chrome
echo "COMMAND_DONE"

echo "COMMAND: Making usrp.sh executable"
chmod +x usrp.sh
echo "COMMAND_DONE"

echo "COMMAND: Making resizeusrp.sh executable"
chmod +x resizeusrp.sh
echo "COMMAND_DONE"

echo "COMMAND: Making pullinglaunch.sh executable"
chmod +x pullinglaunch.sh
echo "COMMAND_DONE"

echo "COMMAND: Making hosts.sh executable"
chmod +x hosts.sh
echo "COMMAND_DONE"

echo "COMMAND: Running hosts.sh"
sudo ./hosts.sh
echo "COMMAND_DONE"

Display /etc/hosts
cat /etc/hosts



Copy recordings
sudo cp -r /home/xmmgr/ubuntu/recordings /home/xmmgr

echo "COMMAND: Adding docker group"
sudo groupadd docker
echo "COMMAND_DONE"

echo "COMMAND: Forcing creation of docker group"
sudo groupadd -f docker
echo "COMMAND_DONE"

# Switch to docker group
# sudo newgrp docker

echo "COMMAND: Adding user xmmgr to docker group"
sudo usermod -aG docker xmmgr
echo "COMMAND_DONE"

echo "COMMAND: Making daemon.sh executable"
chmod +x daemon.sh
echo "COMMAND_DONE"
echo "COMMAND: Running daemon.sh"
sudo ./daemon.sh
echo "COMMAND_DONE"

# Display /etc/docker/daemon.json
# cat /etc/docker/daemon.json
echo "COMMAND: Restarting docker"
sudo systemctl restart docker
echo "COMMAND_DONE"

echo "COMMAND: Enabling docker"
sudo systemctl enable docker
echo "COMMAND_DONE"

echo "COMMAND: Restarting docker"
sudo systemctl restart docker
echo "COMMAND_DONE"

echo "COMMAND: Enabling docker"
sudo systemctl enable docker
echo "COMMAND_DONE"

echo "COMMAND: Checking docker status"
sudo systemctl status docker
echo "COMMAND_DONE"

# Install chrony
# sudo apt-get install chrony -y

# Copy chrony configuration
# sudo cp chrony.conf /etc/chrony/chrony.conf

# Restart chrony service
# service chrony rest

echo "COMMAND: Changing rmem and wmem for usrp"
sudo sysctl -w net.core.rmem_max=24912805
sudo sysctl -w net.core.wmem_max=24912805
echo "COMMAND_DONE"

# Copy recordings
# sudo cp -r /home/xmmgr/ubuntu/recordings /home/xmmgr

echo "COMMAND: Making usrp.sh executable"
sudo chmod +x /home/xmmgr/recordings/usrp.sh
echo "COMMAND_DONE"

echo "COMMAND: Running hosts.sh"
sudo ./hosts.sh
echo "COMMAND_DONE"

# Go into home directory
# Make a new directory called git

# echo "COMMAND: Changing to home directory"
# cd
# echo "COMMAND_DONE"

echo "COMMAND: Creating git directory"
mkdir /home/xmmgr/git
echo "COMMAND_DONE"

echo "COMMAND: Changing group of git directory"
sudo chgrp -R xmmgr /home/xmmgr/git
echo "COMMAND_DONE"

echo "COMMAND: Changing owner of git directory"
sudo chown -R xmmgr /home/xmmgr/git
echo "COMMAND_DONE"

echo "COMMAND: Logging into Docker registry"
docker login docker-trex.artifactory.parsons.us/trex -u $docker_username -p $docker_password
echo "COMMAND_DONE"

# Go into the git directory and Clone launch
# echo "cd to ~/git"
# cd ~/git
# echo "COMMAND: Cloning launch repository"
# echo "COMMAND_DONE"

# Clone specific branches
# cd git | git clone ssh://git@git.parsons.us:7999/trex/launch.git --branch release/v2.3.3
# cd git | git clone http://10.107.65.5/trex2/launch.git --branch release/v2.3.0
# cd git | git clone https://bitbucket.parsons.us/scm/trex/launch.git --branch release/v2.3.0
# ssh://git@git.parsons.us:7999/trex/launch.git

# Restarting docker can sometimes create a luanch directory befor the new one is moved,
#   so we need to remove it
echo "COMMAND: Removing old launch directory"
sudo rm -rf /home/xmmgr/git/launch
echo "COMMAND_DONE"

echo "COMMAND: Moving launch directory"
sudo mv launch /home/xmmgr/git/ # Move launch to correct area
echo "COMMAND_DONE"

echo "COMMAND: Creating recordings directory"
mkdir /home/xmmgr/recordings
echo "COMMAND_DONE"

echo "COMMAND: Creating dc_calibration directory"
mkdir /home/xmmgr/recordings/dc_calibration
echo "COMMAND_DONE"

# Changing Permissions
echo "COMMAND: Changing group of launch directory"
sudo chgrp -R xmmgr /home/xmmgr/git/launch
echo "COMMAND_DONE"

echo "COMMAND: Changing owner of launch directory"
sudo chown -R xmmgr /home/xmmgr/git/launch
echo "COMMAND_DONE"

echo "COMMAND: Changing group of recordings directory"
sudo chgrp -R xmmgr /home/xmmgr/recordings
echo "COMMAND_DONE"

echo "COMMAND: Changing owner of recordings directory"
sudo chown -R xmmgr /home/xmmgr/recordings
echo "COMMAND_DONE"

echo "COMMAND: Changing group of dc_calibration directory"
sudo chgrp -R xmmgr /home/xmmgr/recordings/dc_calibration
echo "COMMAND_DONE"

echo "COMMAND: Changing owner of dc_calibration directory"
sudo chown -R xmmgr /home/xmmgr/recordings/dc_calibration
echo "COMMAND_DONE"

echo "COMMAND: Copying dc_calibration.sh to recordings directory"
sudo cp /home/xmmgr/installer/dc_calibration.sh /home/xmmgr/recordings/dc_calibration/
echo "COMMAND_DONE"

echo "COMMAND: Running hosts.sh"
sudo ./hosts.sh
echo "COMMAND_DONE"

# Display /etc/hosts
cat /etc/hosts

echo "COMMAND: Copying monitors.xml to config directory"
sudo cp -f /home/xmmgr/installer/monitors.xml /home/xmmgr/.config/
echo "COMMAND_DONE"

echo "COMMAND: Copying monitors.xml to gdm3 config directory"
sudo cp -f -i /home/xmmgr/.config/monitors.xml /var/lib/gdm3/.config/
echo "COMMAND_DONE"

echo "COMMAND: Changing to launch directory"
cd /home/xmmgr/git/launch
echo "COMMAND_DONE"

echo "COMMAND: Sleeping for 2 seconds"
sleep 2
echo "COMMAND_DONE"

echo "COMMAND: Sourcing trex_environment.sh"
source trex_environment.sh
echo "COMMAND_DONE"

echo "COMMAND: Changing to scripts directory"
cd /home/xmmgr/git/launch/scripts/
echo "COMMAND_DONE"

echo "COMMAND: Clearing existing postgres installation"
sudo pkill postgres
echo "COMMAND_DONE"

echo "COMMAND: Running launchCompose.sh"
./launchCompose.sh
echo "COMMAND_DONE"
