import sys
import time
import os
import csv

import subprocess
import tempfile

import threading
from PyQt6.QtCore import QSize, Qt, QThread, pyqtSignal, QProcess
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, \
    QInputDialog, QLineEdit, QProgressBar, QVBoxLayout, QWidget, QDialog, \
    QLabel, QHBoxLayout, QSizePolicy, QTextEdit, QTextBrowser, QCheckBox
from PyQt6.QtGui import QGuiApplication, QColor, QPalette
import pexpect

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TReX Installation")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.vbox = QVBoxLayout(central_widget)
        self.show()
        self.installWidget = InstallerGUI()
        self.vbox.addWidget(self.installWidget) 
        width = 800
        height = 500
        self.resize(width, height)
        screen = QGuiApplication.primaryScreen().geometry()
        x = int((screen.width() - width) / 2)
        y = int((screen.height() - height) / 2)
        self.move(x, y)

# class Thread(QThread):
#     _signal = pyqtSignal(int)
#     def __init__(self):
#         super(Thread, self).__init__()
#     def __del__(self):
#         self.wait()
#     def run(self):
#         for i in range(100):
#             time.sleep(0.1)
#             self._signal.emit(i)

# class InstallThread(QThread):
#     progress = pyqtSignal(int)
#     message = pyqtSignal(str)
#     request_cred = pyqtSignal(str)
#     request_bitbucket = pyqtSignal(str)
#     cred_rec = False
#     bitbucket_rec = False
#     arti_cred = ''
#     pause_event = threading.Event()
#     user_input = None
#     username = ''
#     password = ''
#     branch_name = 'release/v2.4.1-baseline'
#     bitbucket_user = ''
#     bitbucket_password = ''
    
#     def run(self):
#         install_commands = [
#             ('updating', 'sudo apt-get update -y'), # Updating apt package index
#             ('upgrading', 'sudo apt-get upgrade -y'), # Upgrading packages
#             ('installing openssh', 'sudo apt install openssh-server -y'), # Installing openssh-server
#             ('starting ssh', 'sudo systemctl start ssh'), # Starting ssh
#             ('enabling ssh', 'sudo systemctl enable ssh --now'), # Enabling ssh now
#             ('enabling ssh', 'sudo systemctl enable ssh'), # Enabling ssh
#             ('disabling firewall', 'sudo ufw disable'), # Disabling firewall
#             ('allowing port 22 to be used', 'sudo ufw allow ssh'), # Allowing port 22 to be used
#             ('installing vim', 'sudo apt install vim -y'), # Installing vim
#             ('installing locate', 'sudo apt install mlocate -y'), # Installing locate
#             ('installing find', 'sudo apt install find'), # Installing find
#             ('installing Tigervncserver', 'sudo apt install tigervnc-standalone-server -y'), # Installing Tigervncserver
#             ('installing Tigervncviewer', 'sudo apt install tigervnc-viewer -y'), # Installing Tigervncviewer
#             ('installing docker-compose', 'sudo apt install docker-compose -y'), # Installing docker-compose
#             ('installing net-tools', 'sudo apt install net-tools -y'), # Installing net-tools
#             ('installing selinux-utils', 'sudo apt install selinux-utils -y'), # Installing selinux-utils
#             ('installing gcc', 'sudo apt install gcc -y'), # Installing gcc
#             ('installing package needed to change gedit color scheme', 'sudo apt install dbus-x11 -y'), # Installing package needed to change gedit color scheme
#             ('installing xrdp', 'sudo apt install xrdp -y'), # Installing xrdp
#             ('starting xrdp', 'sudo systemctl start xrdp'), # Starting xrdp
#             ('enabling xrdp', 'sudo systemctl enable xrdp'), # Enabling xrdp
#             ('installing minicom to look at hoover stack', 'sudo apt install minicom -y'), # Installing minicom to look at hoover stack
#             ('installing screen to look at gps', 'sudo apt install screen -y'), # Installing screen to look at gps
#             ('installing dos2unix for cpu testing to convert windows file to linux', 'sudo apt install dos2unix'), # Installing dos2unix for cpu testing to convert windows file to linux
#             ('installing sensors for cpu testing', 'sudo apt install lm-sensors -y'), # Installing sensors for cpu testing
#             ('setting correct performance mode', 'echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor'), # Setting correct performance mode
#             ('allowing connections from any host', 'xhost +'), # Allowing connections from any host
#             ('installing docker', 'sudo apt install docker -y'), # Installing docker
#             ('downloading chrome .deb file','wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb'),
#             ('installing google-chrome', 'sudo apt install ./google-chrome-stable_current_amd64.deb -y'), # Installing google-chrome
#             ('making usrp.sh executable', 'chmod +x usrp.sh'), # Making usrp.sh executable
#             ('making resizeusrp.sh executable', 'chmod +x resizeusrp.sh'), # Making resizeusrp.sh executable
#             ('making pullinglaunch.sh executable', 'chmod +x pullinglaunch.sh'), # Making pullinglaunch.sh executable
#             ('making hosts.sh executable', 'chmod +x hosts.sh'), # Making hosts.sh executable
#             ('running hosts.sh', 'sudo ./hosts.sh'), # Running hosts.sh
#             ('adding docker group', 'sudo groupadd docker'), # Adding docker group
#             ('forcing adding docker group if it doesn\'t exist', 'sudo groupadd -f docker'), # Forcing adding docker group if it doesn't exist
#             ('adding user xmmgr to docker group', 'sudo usermod -aG docker xmmgr'), # Adding user xmmgr to docker group
#             ('making daemon.sh executable', 'chmod +x daemon.sh'), # Making daemon.sh executable
#             ('running daemon.sh', 'sudo ./daemon.sh'), # Running daemon.sh
#             ('restarting docker', 'sudo systemctl restart docker'), # Restarting docker
#             ('enabling docker', 'sudo systemctl enable docker'), # Enabling docker
#             ('checking docker status', 'sudo systemctl status docker'), # Checking docker status
#             ('setting rmem_max for usrp', 'sudo sysctl -w net.core.rmem_max=24912805'), # Setting rmem_max for usrp
#             ('setting wmem_max for usrp', 'sudo sysctl -w net.core.wmem_max=24912805'), # Setting wmem_max for usrp
#             ('making usrp.sh executable in recordings', 'sudo chmod +x /home/xmmgr/recordings/usrp.sh'), # Making usrp.sh executable in recordings
#             ('running hosts.sh again', 'sudo ./hosts.sh'), # Running hosts.sh again
#             ('creating git directory', 'mkdir /home/xmmgr/git'), # Creating git directory
#             ('changing group of git directory to xmmgr', 'sudo chgrp -R xmmgr /home/xmmgr/git'), # Changing group of git directory to xmmgr
#             ('changing owner of git directory to xmmgr', 'sudo chown -R xmmgr /home/xmmgr/git'), # Changing owner of git directory to xmmgr
#             ('logging into Docker', f'docker login -u username -p password'), # Logging into Docker docker-trex.artifactory.parsons.us
#             ('cloning launch repository', f'cd ~/git | git clone https://username:password@bitbucket.parsons.us/scm/trex/launch.git --branch {self.branch_name}'), # Cloning launch repository
#             ('removing existing launch directory', 'sudo rm -r /home/xmmgr/git/launch'), # Removing existing launch directory
#             ('moving launch to git directory', 'sudo mv launch /home/xmmgr/git/'), # Moving launch to git directory
#             ('creating recordings directory', 'mkdir /home/xmmgr/recordings'), # Creating recordings directory
#             ('creating dc_calibration directory', 'mkdir /home/xmmgr/recordings/dc_calibration'), # Creating dc_calibration directory
#             ('changing group of launch directory to xmmgr', 'sudo chgrp -R xmmgr /home/xmmgr/git/launch'), # Changing group of launch directory to xmmgr
#             ('changing owner of launch directory to xmmgr', 'sudo chown -R xmmgr /home/xmmgr/git/launch'), # Changing owner of launch directory to xmmgr
#             ('changing group of recordings directory to xmmgr', 'sudo chgrp -R xmmgr /home/xmmgr/recordings'), # Changing group of recordings directory to xmmgr
#             ('changing owner of recordings directory to xmmgr', 'sudo chown -R xmmgr /home/xmmgr/recordings'), # Changing owner of recordings directory to xmmgr
#             ('changing group of dc_calibration directory to xmmgr', 'sudo chgrp -R xmmgr /home/xmmgr/recordings/dc_calibration'), # Changing group of dc_calibration directory to xmmgr
#             ('changing owner of dc_calibration directory to xmmgr', 'sudo chown -R xmmgr /home/xmmgr/recordings/dc_calibration'), # Changing owner of dc_calibration directory to xmmgr
#             ('copying dc_calibration.sh to recordings', 'sudo cp /home/xmmgr/installer/dc_calibration.sh /home/xmmgr/recordings/dc_calibration/'), # Copying dc_calibration.sh to recordings
#             ('running hosts.sh again', 'sudo ./hosts.sh'), # Running hosts.sh again
#             ('copying monitors.xml to config', 'sudo cp /home/xmmgr/installer/monitors.xml /home/xmmgr/.config/'), # Copying monitors.xml to config
#             ('copying monitors.xml to gdm3 config', 'sudo cp -i /home/xmmgr/.config/monitors.xml /var/lib/gdm3/.config/'), # Copying monitors.xml to gdm3 config
#             ('changing directory to launch', 'cd /home/xmmgr/git/launch'), # Changing directory to launch
#             ('sourcing trex_environment.sh', 'cd /home/xmmgr/git/launch/ | source trex_environment.sh'), # Sourcing trex_environment.sh
#             ('sleeping for 2 seconds', 'sleep 2'), # Sleeping for 2 seconds
#             ('changing directory to launch scripts', 'cd /home/xmmgr/git/launch/scripts/'), # Changing directory to launch scripts 
#             ('Adding map tile','cd /home/xmmgr/map'),
#             ('Adding map tile','docker load -i map-tile-server-leaflet.tar'),
#             ('Adding map tile','docker load -i ubuntu-image.tar.gz'),
#             ('Adding map tile','docker volume create osm-data'),
#             ('Adding map tile','docker volume create osm-style')
#         ]

#         # Extracting package names from the commands
#         packages = []
#         for description, command in install_commands:
#             if 'apt install' in command:
#                 parts = command.split()
#                 try:
#                     package_index = parts.index('install') + 1
#                     package_name = parts[package_index]
#                     packages.append(package_name)
#                 except (ValueError, IndexError):
#                     continue

#         # Removing duplicates
#         packages = list(set(packages))
#         for i in packages:
#             print(i)

#         # Printing the list of packages
#         print("Packages to be installed:")
#         with open('./packages.csv', 'w', newline='') as file:
#             writer = csv.writer(file)
#             for package in packages:
#                 writer.writerow([package])

#         total_commands = len(install_commands)
#         for i, (msg, cmd) in enumerate(install_commands):
#             self.message.emit(msg)
#             if msg == "logging into Docker":
#                 self.request_cred.emit('request') 
#                 while not self.cred_rec:
#                     time.sleep(1)                        
#                 cmd = cmd.replace("username", self.username)
#                 cmd = cmd.replace("password", self.password)
#                 print(f'Username: {self.username}')
#             if msg == "cloning launch repository":
#                 self.request_bitbucket.emit('request')
#                 while not self.bitbucket_rec:
#                     time.sleep(1)
#                 cmd = cmd.replace("username", self.bitbucket_user)
#                 cmd = cmd.replace("password", self.bitbucket_password)
#                 print(f'bitbucket user: {self.bitbucket_user}')
#             result = subprocess.run(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#             if 'Cloning into' in result.stderr:
#                 process = subprocess.run(self.bitbucket_password, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#                 print("Error: ", result.stderr)
#             # if "overwrite" in result.stderr:
#                 # Handle overwrite prompt:
#             print(result.stdout)
#             print(result.stderr)
#                 # process = subprocess.run('y', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#             print(cmd)
#             self.progress.emit(int(i / total_commands * 100))
#         self.progress.emit(100)
#         time.sleep(0.25)
#         self.progress.emit(0)
        
#         # Define the command
#         cmd = "cd /home/xmmgr/git/launch && source trex_environment.sh && sleep 2 && /home/xmmgr/git/launch/scripts/launchCompose.sh"
#         print(cmd)
#         # Run the command using bash
#         result = subprocess.run(cmd, shell=True, executable='/bin/bash', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#         print(result.stdout)
#         print(result.stderr)
#         self.progress.emit(100)
#         self.quit()    

#     def set_user_input(self, username, password):
#        self.username = username
#        self.password = password
#        self.cred_rec = True 

#     def set_bitbucket(self, username, password):
#         self.bitbucket_user = username.replace("@", "%40")
#         self.bitbucket_password = password.replace("@", "%40")
#         self.bitbucket_rec = True 

# class LaunchThread(QThread):
#     progress = pyqtSignal(int)
#     message = pyqtSignal(str)

#     def run(self):
#         print("Launching TReX Thread")
#         # Create a temporary shell script
#         with tempfile.NamedTemporaryFile('w', delete=False, suffix='.sh') as temp_script:
#             temp_script.write("""
#             #!/bin/bash
#             cd /home/xmmgr/git/launch/
#             pkill postgres
#             source trex_environment.sh
#             ./scripts/launchCompose.sh
#             """)
#             temp_script_path = temp_script.name

#         # Make the temporary script executable
#         os.chmod(temp_script_path, 0o755)

#         # Run the temporary script
#         process = subprocess.Popen(f"bash {temp_script_path}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         stdout, stderr = process.communicate()

#         # Print the output and error (if any)
#         print(stdout.decode('utf-8'))
#         if process.returncode != 0:
#             print(f"Error: {stderr.decode('utf-8')}")

#         # Clean up the temporary script
#         os.remove(temp_script_path)

class InputDialog(QDialog):
    def __init__(self, title):
        super().__init__()
        self.init_ui(title)

    def init_ui(self, title):
        self.setAutoFillBackground(True)

        self.setWindowTitle(title)
        self.layout = QVBoxLayout()

        self.label0 = QLabel(title)
        self.label1 = QLabel("Username")
        self.input1 = QLineEdit()
        self.layout.addWidget(self.label0)
        self.layout.addWidget(self.label1)
        self.layout.addWidget(self.input1)

        self.label2 = QLabel("Password")
        self.input2 = QLineEdit()
        self.input2.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.label2)
        self.layout.addWidget(self.input2)

        self.branchLabel = QLabel("Branch Name")
        self.inputBranch = QLineEdit()
        if title == "Bitbucket Login": 
            self.layout.addWidget(self.branchLabel)
            self.layout.addWidget(self.inputBranch)
        self.button = QPushButton("Submit")
        self.button.clicked.connect(self.accept)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)
        self.invisible()

    def invisible(self):
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.hide()

    def visible(self):
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.show()

    def get_inputs(self):
        return self.input1.text(), self.input2.text(), self.inputBranch.text()

class InstallerGUI(QWidget):
    progress = 0
    bitbucket_username = ''
    bitbucket_password = ''
    docker_username = ''
    docker_password = ''
    branch_name = 'release/v2.4.1-baseline'
    processes = [
        ["rm", ["-rf", "launch"], ["Removing old files"]],
        ["rm", ["-rf", "/home/xmmgr/git/launch"], ["Removing old files"]],
        ["git", ["clone", f"https://username:password@bitbucket.parsons.us/scm/trex/launch.git", "--branch", "branch_name", "--progress"], ["Cloning launch"]],
        ["bash", ["/home/xmmgr/git/trexinstaller/install_edit.sh", "username", "password"], "Installing Software Dependencies"]
    ]
    # branch_name = 'release/v2.4.1-baseline'
    def __init__(self):
        super().__init__()
        print("Init")
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Installer')

        self.layout = QVBoxLayout()

        self.label = QLabel('Click "Start Installation" to begin.')
        self.layout.addWidget(self.label)
        self.layout.setAlignment(self.label, Qt.AlignmentFlag.AlignTop)
        self.label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        
        self.layout.addStretch(1)
        self.center_layout = QVBoxLayout()
        self.layout.addLayout(self.center_layout)
        self.layout.setAlignment(self.center_layout, Qt.AlignmentFlag.AlignTop)

        self.dockerDialog = InputDialog("Docker Login")
        self.bitbucketDialog = InputDialog("Bitbucket Login")

        self.layout.addStretch(1)
        self.progressBar = QProgressBar(self)
        self.progressBar.setVisible(False)
        self.progressBar.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.layout.addWidget(self.progressBar)

        self.startButton = QPushButton('Start Installation', self)
        self.startButton.clicked.connect(self.startInstallation)
        self.layout.addWidget(self.startButton)
 
        self.logsText = QTextBrowser()
        self.layout.addWidget(self.logsText)
        self.logsText.setVisible(False)

        self.exitButton = QPushButton('Exit', self)
        self.exitButton.clicked.connect(self.close)
        self.exitButton.clicked.connect(self.quitWindow)
        self.exitButton.setVisible(False)
        self.layout.addWidget(self.exitButton)

        self.logsLayout = QHBoxLayout()
        self.logsChecked = QCheckBox()
        self.logsChecked.stateChanged.connect(self.logs)
        self.logsLabel = QLabel("Show Logs")
        self.logsLayout.addWidget(self.logsLabel)
        self.logsLayout.addWidget(self.logsChecked) 
        self.logsLayout.addStretch(1)
        self.layout.addLayout(self.logsLayout)

        self.setLayout(self.layout)

    def startInstallation(self):
        self.startButton.setEnabled(False)
        self.startButton.setVisible(False)
        self.progressBar.setVisible(True)

        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.readyReadStandardError.connect(self.read_error)
        self.process.finished.connect(self.process_finished)

        self.updateMessage("Enter Docker Credentials")
        self.request_docker()
        self.updateMessage("Enter Bitbucket Credentials")
        self.request_bitbucket()
        self.startProcess()

    def startProcess(self):
        command = self.processes.pop(0)
        if command[1][0] == "clone":
            command[1][1] = command[1][1].replace("username", self.bitbucket_username)
            command[1][1] = command[1][1].replace("password", self.bitbucket_password)
            command[1][3] = self.branch_name
            print("command[1]", command[1])
        elif "install_edit.sh" in command[1][0]:
            print("need to update docker credentials")
            command[1][1] = self.docker_username
            command[1][2] = self.docker_password
        else:
            print("command: ", command[1])
        description = command[0]+" "+" ".join(command[1])
        self.label.setText(description)
        print("Executing command: ", command)
        self.process.start(command[0], command[1])
        self.updateMessage(command[2][0])

    def logs(self, state):
        if state == Qt.CheckState.Checked.value:
            self.logsText.setVisible(True)
        else:
            self.logsText.setVisible(False)

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
 
    def request_docker(self):
        self.center_layout.addWidget(self.dockerDialog)
        self.center_layout.setAlignment(self.dockerDialog, Qt.AlignmentFlag.AlignCenter)
        self.dockerDialog.visible()
        self.dockerDialog.input1.setFocus()
        if self.dockerDialog.exec() == QDialog.DialogCode.Accepted:
            self.docker_username, self.docker_password, nothing = self.dockerDialog.get_inputs()
        self.center_layout.removeWidget(self.dockerDialog)

    def request_bitbucket(self):
        self.center_layout.addWidget(self.bitbucketDialog)
        self.center_layout.setAlignment(self.bitbucketDialog, Qt.AlignmentFlag.AlignCenter)
        self.bitbucketDialog.visible()
        self.bitbucketDialog.input1.setFocus()
        if self.bitbucketDialog.exec() == QDialog.DialogCode.Accepted:
            self.bitbucketDialog.setVisible(False)
            self.bitbucket_username, self.bitbucket_password, self.branch_name = self.bitbucketDialog.get_inputs()
            self.set_bitbucket(self.bitbucket_username, self.bitbucket_password)
            print("updating bitbucket username/password: ", self.bitbucket_username, " ", self.bitbucket_password)
            if self.branch_name == "":
                self.branch_name = 'release/v2.4.1-baseline'
        self.center_layout.removeWidget(self.bitbucketDialog)
            
    def set_bitbucket(self, username, password):
        self.bitbucket_username = username.replace("@", "%40")
        self.bitbucket_password = password.replace("@", "%40")
        # self.branch_name = 

    def read_output(self):
        output = self.process.readAllStandardOutput().data().decode()
        if "error" in output.lower():
            print("Error: ", output)
            self.logsText.append(f"<font color='red'>{output}</font>")
        else:
            if "WARNING: apt does not have a stable CLI interface. Use with caution in scripts." in output:
                output = output.replace("WARNING: apt does not have a stable CLI interface. Use with caution in scripts.", "")    
            if "overwrite" in output:
                self.logsText.append(output)
                print(output)
                self.logsText.append("Saying yes to overwrite")
                # Send 'y' (yes) followed by a newline to confirm overwriting
                self.process.write(b"y\n")
            elif "COMMAND_DONE" in output:
                self.progress += 1
                self.updateProgress(self.progress)
            elif "COMMAND: " in output:
                output = output.replace("COMMAND: ", "")
                self.updateMessage(output)
                self.logsText.append(output)
                print(output)
            else:
                print(output)
                self.logsText.append(output)
        

    def read_error(self):
        error = self.process.readAllStandardError().data().decode()
        if error:
            if "error" in error.lower():
                print("Error", error)
                self.logsText.append(f"<font color='red'>{error}</font>")
            else:
                if "WARNING: apt does not have a stable CLI interface. Use with caution in scripts." in error:
                    error = error.replace("WARNING: apt does not have a stable CLI interface. Use with caution in scripts.", "")
                print(error)
                self.logsText.append(error)
            if "overwrite" in error:
                self.logsText.append("Saying yest to overwrite")
                # Send 'y' (yes) followed by a newline to confirm overwriting
                self.process.write(b"y\n")

    def process_finished(self, exit_code, exit_status):
        self.logsText.append(f"Process finished with exit code {exit_code}")
        if self.processes:
            self.startProcess()
        else:
            self.exitButton.setVisible(True) 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
