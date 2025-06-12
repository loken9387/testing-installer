import sys
import time
import os
import threading
import tempfile
import subprocess
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QProgressBar, QLabel, QInputDialog, QDialog, QLineEdit
from PyQt6.QtCore import Qt, QThread, pyqtSignal

class InstallThread(QThread):
    progress = pyqtSignal(int)
    message = pyqtSignal(str)
    request_cred = pyqtSignal(str)
    request_bitbucket = pyqtSignal(str)
    cred_rec = False
    bitbucket_rec = False
    arti_cred = ''
    pause_event = threading.Event()
    user_input = None
    username = ''
    password = ''
    branch_name = 'release/v2.4.1-baseline'
    bitbucket_user = ''
    bitbucket_password = ''

    def run(self):
        install_commands = [
            ('updating', 'sudo apt-get update -y'), # Updating apt package index
            ('upgrading', 'sudo apt-get upgrade -y'), # Upgrading packages
            ('installing openssh', 'sudo apt install openssh-server -y'), # Installing openssh-server
            ('starting ssh', 'sudo systemctl start ssh'), # Starting ssh
            ('enabling ssh', 'sudo systemctl enable ssh --now'), # Enabling ssh now
            ('enabling ssh', 'sudo systemctl enable ssh'), # Enabling ssh
            ('disabling firewall', 'sudo ufw disable'), # Disabling firewall
            ('allowing port 22 to be used', 'sudo ufw allow ssh'), # Allowing port 22 to be used
            ('installing vim', 'sudo apt install vim -y'), # Installing vim
            ('installing locate', 'sudo apt install mlocate -y'), # Installing locate
            ('installing find', 'sudo apt install find'), # Installing find
            ('installing Tigervncserver', 'sudo apt install tigervnc-standalone-server -y'), # Installing Tigervncserver
            ('installing Tigervncviewer', 'sudo apt install tigervnc-viewer -y'), # Installing Tigervncviewer
            ('installing docker-compose', 'sudo apt install docker-compose -y'), # Installing docker-compose
            ('installing net-tools', 'sudo apt install net-tools -y'), # Installing net-tools
            ('installing selinux-utils', 'sudo apt install selinux-utils -y'), # Installing selinux-utils
            ('installing gcc', 'sudo apt install gcc -y'), # Installing gcc
            ('installing package needed to change gedit color scheme', 'sudo apt install dbus-x11 -y'), # Installing package needed to change gedit color scheme
            ('installing xrdp', 'sudo apt install xrdp -y'), # Installing xrdp
            ('starting xrdp', 'sudo systemctl start xrdp'), # Starting xrdp
            ('enabling xrdp', 'sudo systemctl enable xrdp'), # Enabling xrdp
            ('installing minicom to look at hoover stack', 'sudo apt install minicom -y'), # Installing minicom to look at hoover stack
            ('installing screen to look at gps', 'sudo apt install screen -y'), # Installing screen to look at gps
            ('installing dos2unix for cpu testing to convert windows file to linux', 'sudo apt install dos2unix'), # Installing dos2unix for cpu testing to convert windows file to linux
            ('installing sensors for cpu testing', 'sudo apt install lm-sensors -y'), # Installing sensors for cpu testing
            ('setting correct performance mode', 'echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor'), # Setting correct performance mode
            ('allowing connections from any host', 'xhost +'), # Allowing connections from any host
            ('installing docker', 'sudo apt install docker -y'), # Installing docker
            ('installing google-chrome', 'sudo apt install ./google-chrome-stable_current_amd64.deb -y'), # Installing google-chrome
            ('making usrp.sh executable', 'chmod +x usrp.sh'), # Making usrp.sh executable
            ('making resizeusrp.sh executable', 'chmod +x resizeusrp.sh'), # Making resizeusrp.sh executable
            ('making pullinglaunch.sh executable', 'chmod +x pullinglaunch.sh'), # Making pullinglaunch.sh executable
            ('making hosts.sh executable', 'chmod +x hosts.sh'), # Making hosts.sh executable
            ('running hosts.sh', 'sudo ./hosts.sh'), # Running hosts.sh
            ('adding docker group', 'sudo groupadd docker'), # Adding docker group
            ('forcing adding docker group if it doesn\'t exist', 'sudo groupadd -f docker'), # Forcing adding docker group if it doesn't exist
            ('adding user xmmgr to docker group', 'sudo usermod -aG docker xmmgr'), # Adding user xmmgr to docker group
            ('making daemon.sh executable', 'chmod +x daemon.sh'), # Making daemon.sh executable
            ('running daemon.sh', 'sudo ./daemon.sh'), # Running daemon.sh
            ('restarting docker', 'sudo systemctl restart docker'), # Restarting docker
            ('enabling docker', 'sudo systemctl enable docker'), # Enabling docker
            ('checking docker status', 'sudo systemctl status docker'), # Checking docker status
            ('setting rmem_max for usrp', 'sudo sysctl -w net.core.rmem_max=24912805'), # Setting rmem_max for usrp
            ('setting wmem_max for usrp', 'sudo sysctl -w net.core.wmem_max=24912805'), # Setting wmem_max for usrp
            ('making usrp.sh executable in recordings', 'sudo chmod +x /home/xmmgr/recordings/usrp.sh'), # Making usrp.sh executable in recordings
            ('running hosts.sh again', 'sudo ./hosts.sh'), # Running hosts.sh again
            ('generating SSH keys', 'ssh-keygen'), # Generating SSH keys
            ('creating git directory', 'mkdir /home/xmmgr/git'), # Creating git directory
            ('changing group of git directory to xmmgr', 'sudo chgrp -R xmmgr /home/xmmgr/git'), # Changing group of git directory to xmmgr
            ('changing owner of git directory to xmmgr', 'sudo chown -R xmmgr /home/xmmgr/git'), # Changing owner of git directory to xmmgr
            ('logging into Docker', f'docker login docker-trex.artifactory.parsons.us --u {self.username} --p {self.password}'), # Logging into Docker
            ('cloning launch repository', f'cd ~/git | https://{self.bitbucket_user}@bitbucket.parsons.us/scm/trex/launch.git --branch {self.branch_name}'), # Cloning launch repository
            ('removing existing launch directory', 'sudo rm -r /home/xmmgr/git/launch'), # Removing existing launch directory
            ('moving launch to git directory', 'sudo mv launch /home/xmmgr/git/'), # Moving launch to git directory
            ('creating recordings directory', 'mkdir /home/xmmgr/recordings'), # Creating recordings directory
            ('creating dc_calibration directory', 'mkdir /home/xmmgr/recordings/dc_calibration'), # Creating dc_calibration directory
            ('changing group of launch directory to xmmgr', 'sudo chgrp -R xmmgr /home/xmmgr/git/launch'), # Changing group of launch directory to xmmgr
            ('changing owner of launch directory to xmmgr', 'sudo chown -R xmmgr /home/xmmgr/git/launch'), # Changing owner of launch directory to xmmgr
            ('changing group of recordings directory to xmmgr', 'sudo chgrp -R xmmgr /home/xmmgr/recordings'), # Changing group of recordings directory to xmmgr
            ('changing owner of recordings directory to xmmgr', 'sudo chown -R xmmgr /home/xmmgr/recordings'), # Changing owner of recordings directory to xmmgr
            ('changing group of dc_calibration directory to xmmgr', 'sudo chgrp -R xmmgr /home/xmmgr/recordings/dc_calibration'), # Changing group of dc_calibration directory to xmmgr
            ('changing owner of dc_calibration directory to xmmgr', 'sudo chown -R xmmgr /home/xmmgr/recordings/dc_calibration'), # Changing owner of dc_calibration directory to xmmgr
            ('copying dc_calibration.sh to recordings', 'sudo cp /home/xmmgr/installer/dc_calibration.sh /home/xmmgr/recordings/dc_calibration/'), # Copying dc_calibration.sh to recordings
            ('running hosts.sh again', 'sudo ./hosts.sh'), # Running hosts.sh again
            ('copying monitors.xml to config', 'sudo cp /home/xmmgr/installer/monitors.xml /home/xmmgr/.config/'), # Copying monitors.xml to config
            ('copying monitors.xml to gdm3 config', 'sudo cp -i /home/xmmgr/.config/monitors.xml /var/lib/gdm3/.config/'), # Copying monitors.xml to gdm3 config
            ('changing directory to launch', 'cd /home/xmmgr/git/launch'), # Changing directory to launch
            ('sourcing trex_environment.sh', 'cd /home/xmmgr/git/launch/ | source trex_environment.sh'), # Sourcing trex_environment.sh
            ('sleeping for 2 seconds', 'sleep 2'), # Sleeping for 2 seconds
            ('changing directory to launch scripts', 'cd /home/xmmgr/git/launch/scripts/'), # Changing directory to launch scripts 
        ]
        total_commands = len(install_commands)
        for i, (msg, cmd) in enumerate(install_commands):
            self.message.emit(msg)
            if msg == "logging into Docker":
                self.request_cred.emit('request') 
                while not self.cred_rec:
                    time.sleep(1)                        
                print(f'Username: {self.username}')
            if msg == "cloning launch repository":
                self.request_bitbucket.emit('request')
                while not self.bitbucket_rec:
                    time.sleep(1)
                print(f'bitbucket user: {self.bitbucket_user}')
            result = subprocess.run(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.stderr:
                print('ERROR: ', result.stderr)
            if 'Password for' in result.stderr:
                print("Requesting a password!")
                process = subprocess.run(self.bitbucket_password, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if "overwrite" in result.stderr:
                # Handle overwrite prompt:
                process = subprocess.run('y', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(cmd)
            self.progress.emit(int(i / total_commands * 100))
        self.progress.emit(100)
        time.sleep(0.25)
        self.progress.emit(0)
        
        # Define the command
        cmd = "cd /home/xmmgr/git/launch && source trex_environment.sh && sleep 2 && /home/xmmgr/git/launch/scripts/launchCompose.sh"
        print(cmd)
        # Run the command using bash
        result = subprocess.run(cmd, shell=True, executable='/bin/bash', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
        print(result.stderr)
        self.progress.emit(100)
        self.quit()    

    def set_user_input(self, username, password):
       self.username = username
       self.password = password
       self.cred_rec = True 

    def set_bitbucket(self, username, password):
        self.bitbucket_user = username
        self.bitbucket_password = password
        self.bitbucket_rec = True 

class LaunchThread(QThread):
    progress = pyqtSignal(int)
    message = pyqtSignal(str)

    def run(self):
        print("Launching TReX Thread")
        # Create a temporary shell script
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.sh') as temp_script:
            temp_script.write("""
            #!/bin/bash
            cd /home/xmmgr/git/launch/
            source trex_environment.sh
            ./scripts/launchCompose.sh
            """)
            temp_script_path = temp_script.name

        # Make the temporary script executable
        os.chmod(temp_script_path, 0o755)

        # Run the temporary script
        process = subprocess.Popen(f"bash {temp_script_path}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # Print the output and error (if any)
        print(stdout.decode('utf-8'))
        if process.returncode != 0:
            print(f"Error: {stderr.decode('utf-8')}")

        # Clean up the temporary script
        os.remove(temp_script_path)

class InputDialog(QDialog):
    def __init__(self, title):
        super().__init__()
        self.init_ui(title)

    def init_ui(self, title):
        self.setWindowTitle(title)
        self.layout = QVBoxLayout()

        self.label1 = QLabel("Username")
        self.input1 = QLineEdit()
        self.layout.addWidget(self.label1)
        self.layout.addWidget(self.input1)

        self.label2 = QLabel("Password")
        self.input2 = QLineEdit()
        self.input2.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.label2)
        self.layout.addWidget(self.input2)

        self.button = QPushButton("Submit")
        self.button.clicked.connect(self.accept)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

    def get_inputs(self):
        return self.input1.text(), self.input2.text()

class InstallerGUI(QWidget):
    def __init__(self):
        super().__init__()
        print("Init")
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Installer')
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        self.label = QLabel('Click "Start Installation" to begin.')
        layout.addWidget(self.label)

        self.progressBar = QProgressBar(self)
        self.progressBar.setVisible(False)
        self.progressBar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progressBar)

        self.startButton = QPushButton('Start Installation', self)
        self.startButton.clicked.connect(self.startInstallation)
        layout.addWidget(self.startButton)
        
        self.exitButton = QPushButton('Exit', self)
        self.exitButton.clicked.connect(self.close)
        self.exitButton.clicked.connect(self.quitWindow)
        self.exitButton.setVisible(False)
        layout.addWidget(self.exitButton)

        self.setLayout(layout)

    def startInstallation(self):
        self.startButton.setEnabled(False)
        self.startButton.setVisible(False)
        self.progressBar.setVisible(True)
        self.install_thread = InstallThread()
        self.install_thread.progress.connect(self.updateProgress)
        self.install_thread.message.connect(self.updateMessage)

        self.install_thread.request_cred.connect(self.request_user_input)
        self.install_thread.request_bitbucket.connect(self.request_bitbucket)
        self.install_thread.finished.connect(self.onFinished)
        self.install_thread.start()


    def updateProgress(self, value):
        self.progressBar.setValue(value)

    def updateMessage(self, message):
        self.label.setText(message)

    def onFinished(self):
        self.label.setText('Installation completed.')
        self.startButton.setVisible(False)
        self.exitButton.setVisible(True)

    def quitWindow(self):
        QApplication.instance().quit()

    def onReset(self, input):
        self.label.setText("Next step: ", input)
        self.startButton.setVisible(False)
        self.exitButton.setVisible(False)
 
    def request_user_input(self):
        dialog = InputDialog("Docker Login")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            username, password = dialog.get_inputs()
            self.install_thread.set_user_input(username, password)
            print(f'username entered: {username}, password: {password}')

    def request_bitbucket(self):
        dialog = InputDialog("Bitbucket Login")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            username, password = dialog.get_inputs()
            self.install_thread.set_bitbucket(username, password)
            print(f'username entered: {username}')
            
    commands = [
        ('updating','sudo apt-get update -y'), # Updates apt package index
        ('upgrading','sudo apt-get upgrade -y'),
        ('installing openssh', 'sudo apt install openssh-server -y'), # Installs openssh-server,
        ('starting ssh', 'sudo systemctl start ssh'), # Starts ssh
        ('enabling ssh','sudo systemctl enable ssh --now') # Enables ssh now
    ]
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = InstallerGUI()
    ex.show()
    sys.exit(app.exec())