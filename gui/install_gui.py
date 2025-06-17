import sys
import os
import subprocess
import getpass
import csv
import fnmatch
import shutil

if getattr(sys, "frozen", False):
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

from PyQt6.QtCore import Qt, QProcess
import qt_material
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLineEdit,
    QProgressBar,
    QVBoxLayout,
    QWidget,
    QDialog,
    QComboBox,
    QLabel,
    QHBoxLayout,
    QSizePolicy,
    QTextBrowser,
    QCheckBox,
    QFileDialog,
    QMessageBox
)
from PyQt6.QtGui import QGuiApplication

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


class NetworkInfoDialog(QDialog):
    def __init__(self, parent=None):
        super(NetworkInfoDialog, self).__init__(parent)
        
        self.setWindowTitle("Network Information")
        
        # Create a QVBoxLayout to hold the labels
        layout = QVBoxLayout()
        
        # Add the information as QLabel widgets
        info_text = """
        In Network Settings, verify there is a 10000 Mb/s connection enabled with the following:
        """
        layout.addWidget(QLabel(info_text.strip()))
        
        # Bolded IPv4
        ipv4_label = QLabel("IPv4")
        # ipv4_label.setFont(QFont("Arial", weight=QFont))
        layout.addWidget(ipv4_label)
        
        # IPv4 details
        ipv4_details = """
        -Method: Manual
        -IP Address: 192.168.40.1
        -Netmask: 255.255.255.0
        -Gateway: Empty
        """
        for line in ipv4_details.strip().split('\n'):
            label = QLabel(line.strip())
            layout.addWidget(label)
        
        # Bolded Identity
        identity_label = QLabel("Identity")
        # identity_label.setFont(QFont("Arial", weight=QFont.Bold))
        layout.addWidget(identity_label)
        
        # Identity details
        identity_details = """
        -Name: USRP
        -MTU: 9216
        """
        for line in identity_details.strip().split('\n'):
            label = QLabel(line.strip())
            layout.addWidget(label)
        
        self.button = QPushButton("Proceed")
        self.button.clicked.connect(self.accept)
        layout.addWidget(self.button)
        
        # Set the layout for the dialog
        self.setLayout(layout)

class RadioConfigDialog(QDialog):
    """Dialog to configure USRP device type and connection."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Radio Configuration")

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Device Type"))
        self.device_combo = QComboBox()
        self.device_combo.addItems(["x310", "b210"])
        layout.addWidget(self.device_combo)

        layout.addWidget(QLabel("IP Address or Serial Number"))
        self.conn_edit = QLineEdit()
        layout.addWidget(self.conn_edit)

        self.verify_button = QPushButton("Verify Connection")
        self.verify_button.clicked.connect(self.verify_connection)
        layout.addWidget(self.verify_button)

        self.output = QTextBrowser()
        self.output.setVisible(False)
        layout.addWidget(self.output)

        self.button_box = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        self.button_box.addWidget(self.ok_button)
        self.button_box.addWidget(self.cancel_button)
        layout.addLayout(self.button_box)

        self.setLayout(layout)

    def verify_connection(self):
        """Run uhd_find_devices to verify connectivity."""
        device = self.device_combo.currentText()
        addr = self.conn_edit.text().strip()
        args = ["--args"]
        if device == "x310":
            args.append(f"type=x300,addr={addr}")
        else:
            serial_arg = f",serial={addr}" if addr else ""
            args.append(f"type=b200{serial_arg}")
        try:
            result = subprocess.run([
                "uhd_find_devices",
                *args
            ], capture_output=True, text=True, check=False)
            self.output.setVisible(True)
            self.output.setText(result.stdout + "\n" + result.stderr)
        except Exception as exc:
            self.output.setVisible(True)
            self.output.setText(str(exc))

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
        if title != "Sudo Login" and title != "OVPN Profile Number":
            self.layout.addWidget(self.label1)
            self.layout.addWidget(self.input1)
        if title == "OVPN Profile Number":
            self.label1 = QLabel("")

        if title != "OVPN Profile Number":
            self.label2 = QLabel("Password")
            self.input2 = QLineEdit()
            self.input2.setEchoMode(QLineEdit.EchoMode.Password)
        else:
            self.label2 = QLabel()
            self.input2 = QLineEdit()
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
    def __init__(self):
        super().__init__()
        print("Init")
        # Configuration values
        self.progress = 0
        self.sudo_username = getpass.getuser()
        self.sudo_password = ""
        self.root_password = "root"
        self.bitbucket_username = ""
        self.bitbucket_password = ""
        self.docker_username = ""
        self.docker_password = ""
        self.branch_name = 'release/v2.4.1-baseline'
        self.base_url = "http://localhost:8080/api/missions/import/upload"
        self.ovpn_profile = "profile-"
        self.ovpn_number = 0
        self.install_method = "online"
        self.install_commands = []
        self.resource_dir = SCRIPT_DIR
        self.X310_FPGA_PATH = "/usr/local/share/uhd/images/usrp_x310_fpga_XG.bit"
        self.B210_FPGA_PATH = "/usr/local/share/uhd/images/usrp_b210_fpga.bin"

        # Commands run after packages are installed
        self.post_install_commands = [
            ["Starting ssh", "sudo", ["systemctl", "start", "ssh"]],
            ["Enabling ssh now", "sudo", ["systemctl", "enable", "ssh", "--now"]],
            ["Enabling ssh", "sudo", ["systemctl", "enable", "ssh"]],
            ["Disabling firewall", "sudo", ["ufw", "disable"]],
            ["Allowing port 22 to be used", "sudo", ["ufw", "allow", "ssh"]],
            ["Starting xrdp", "sudo", ["systemctl", "start", "xrdp"]],
            ["Enabling xrdp", "sudo", ["systemctl", "enable", "xrdp"]],
            ["Installing minicom to look at hoover stack", "sudo", ["apt", "install", "minicom", "-y"]],
            ["Setting correct performance mode", "echo", ["performance", "|", "sudo", "tee", "/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"]],
            ["Allowing connections from any host", "xhost", ["+"]],
            ["Loading USRP FPGA", "uhd_image_loader", []],
            ["Setting rmem_max for usrp", "sudo", ["sysctl", "-w", "net.core.rmem_max=24912805"]],
            ["Setting wmem_max for usrp", "sudo", ["sysctl", "-w", "net.core.wmem_max=24912805"]],

            # Ensure xmmgr group exists
            ["Ensure xmmgr group exists", "bash", ["-c", "getent group xmmgr || sudo groupadd xmmgr"]],
            # Ensure user xmmgr exists and has correct group
            ["Ensure xmmgr user exists", "bash", ["-c", (
                "id -u xmmgr || "
                "(sudo -S useradd -m -g xmmgr xmmgr && echo 'xmmgr:xmmgr' | sudo -S chpasswd)"
            )]],
            # Ensure docker group exists
            ["Ensure docker group exists", "bash", ["-c", "getent group docker || sudo groupadd docker"]],
            # Add xmmgr to docker group
            ["Add xmmgr to docker group", "sudo", ["usermod", "-aG", "docker", "xmmgr"]],
            # Restart and Enable docker for use
            ["Restarting docker", "sudo", ["systemctl", "restart", "docker"]],
            ["Enabling docker", "sudo", ["systemctl", "enable", "docker"]],
            ["Checking docker status", "sudo", ["systemctl", "status", "docker"]],

            # Setting up launch dir
            ["Removing existing launch directory", "bash", [
                "-c",
                'if [ -d "/home/xmmgr/launch" ]; then sudo rm -r "/home/xmmgr/launch"; fi'
            ]],
            ["moving launch directory", "sudo", ["tar", "-xf", os.path.join(self.resource_dir, "launch.tar.gz"), "-C", "/home/xmmgr/"]],
            ["Changing group of launch directory to xmmgr", "sudo", ["chgrp", "-R", "xmmgr", "/home/xmmgr/launch"]],
            ["Changing owner of launch directory to xmmgr", "sudo", ["chown", "-R", "xmmgr", "/home/xmmgr/launch"]],
            ["Creating NodeConfigWizard Desktop icon", "sudo", ["bash", os.path.join(self.resource_dir, "createNodeConfigWizardDesktop.sh")]],

            # Setting up recordings dir
            ["Creating recordings directory", "mkdir", ["/home/xmmgr/recordings"]],
            ["Creating dc_calibration directory", "mkdir", ["/home/xmmgr/recordings/dc_calibration"]],
            ["Changing group of recordings directory to xmmgr", "sudo", ["chgrp", "-R", "xmmgr", "/home/xmmgr/recordings"]],
            ["Changing owner of recordings directory to xmmgr", "sudo", ["chown", "-R", "xmmgr", "/home/xmmgr/recordings"]],
            ["Changing group of dc_calibration directory to xmmgr", "sudo", ["chgrp", "-R", "xmmgr", "/home/xmmgr/recordings/dc_calibration"]],
            ["Changing owner of dc_calibration directory to xmmgr", "sudo", ["chown", "-R", "xmmgr", "/home/xmmgr/recordings/dc_calibration"]],
            ["Copying dc_calibration.sh to recordings", "sudo", ["cp", os.path.join(self.resource_dir, "dc_calibration.sh"), "/home/xmmgr/recordings/dc_calibration/"]],
            ["changing priveleges of dc_calibration.sh", "sudo", ["chmod", "755", "/home/xmmgr/recordings/dc_calibration/dc_calibration.sh"]],

            # Load Docker Images
            ["creating postgres image", "sudo", ["docker", "load", "-i", os.path.join(self.resource_dir, "postgres.tar.gz")]],
            ["creating node-webserver image", "sudo", ["docker", "load", "-i", os.path.join(self.resource_dir, "node-webserver.tar.gz")]],
            ["creating client image", "sudo", ["docker", "load", "-i", os.path.join(self.resource_dir, "client.tar.gz")]],
            ["creating services image", "sudo", ["docker", "load", "-i", os.path.join(self.resource_dir, "services.tar.gz")]],
            ["creating signal image", "sudo", ["docker", "load", "-i", os.path.join(self.resource_dir, "signal.tar.gz")]],

            # The folllowing steps require knowledge about how dc_calibration will be run, how containers will be changes form bash to xmidas_node, etc.
            # ["changing to bash mode", "sed", ["-i" , "s/xmidas_node/bash/g", "/home/xmmgr/git/launch/trex_environment.sh"]],
            # ["Running launchCompose.sh", "sudo", ["/home/xmmgr/git/trexinstaller/gui/source_trex.sh"]],
            # ["Creating Desktop icon", "sudo", [os.path.join(self.resource_dir, "createDesktop.sh")]],
            ["Copying OpenVPN files", "cp", [os.path.join(self.resource_dir, "OpenVPN/"), "/home/xmmgr/", "-r"]],
            ["Adjusting OpenVPN file permissions", "sudo", ["chmod", "-R", "755", "/home/xmmgr/OpenVPN/"]],

            # Power down the machine once installation completes
            ["Shutting down system", "sudo", ["shutdown", "-h", "now"]],

            # ["running dc_calibration", "sudo", ["docker", "exec", "node-service", "bash", "-c", "\"./root/.local/share/uhd/cal/dc_calibration.sh\""]],
            # ["changing to xmidas mode", "sed", ["-i" , "10,$s/bash/xmidas_node/g", "/home/xmmgr/git/launch/trex_environment.sh"]],
        ]

        # Ensure all sudo commands use the -S flag for password input
        for cmd in self.post_install_commands:
            if cmd[1] == "sudo" and (not cmd[2] or cmd[2][0] != "-S"):
                cmd[2].insert(0, "-S")

        # The launch directory should always live inside the xmmgr user's
        # home directory.  Default to ``/home/xmmgr/launch`` so no dialog is
        # required to pick the location.
        self.launch_parent_dir = "/home/xmmgr"
        self.launch_dir = os.path.join(self.launch_parent_dir, "launch")
        self.current_command = ""
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
        self.sudoDialog = InputDialog("Sudo Login")
        self.ovpnDialog = InputDialog("OVPN Profile Number")
        self.networkDialog = NetworkInfoDialog()

        self.layout.addStretch(1)
        self.progressBar = QProgressBar(self)
        self.progressBar.setVisible(False)
        self.progressBar.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.layout.addWidget(self.progressBar)

        self.statusLabel = QLabel("")
        self.statusLabel.setVisible(False)
        self.layout.addWidget(self.statusLabel)

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
    
    def networkSetup(self):
        script_dir = self.resource_dir
        self.update_resource_paths(script_dir)
        packages_path = os.path.join(script_dir, "packages.csv")
        if not os.path.exists(packages_path):
            raise FileNotFoundError(f"{packages_path} not found")

        packages = []
        with open(packages_path, newline="") as f:
            for row in csv.reader(f):
                if not row:
                    continue
                pkg = row[0].strip()
                if pkg and not pkg.startswith("#"):
                    packages.append(pkg)

        self.install_commands.append([
            "Updating apt cache", "sudo", ["-S", "apt-get", "update"]
        ])

        for pkg in packages:
            if pkg.endswith("google-chrome-stable_current_amd64.deb"):
                deb_path = os.path.join("/tmp", "google-chrome-stable_current_amd64.deb")
                self.install_commands.append([
                    "Downloading Google Chrome", "wget", [
                        "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb",
                        "-O",
                        deb_path,
                    ],
                ])
                self.install_commands.append([
                    "Installing google-chrome", "sudo", ["-S", "dpkg", "-i", deb_path]
                ])
                self.install_commands.append([
                    "Fixing dependencies", "sudo", ["-S", "apt-get", "-f", "install", "-y"]
                ])
                self.install_commands.append([
                    "Removing chrome deb", "rm", [deb_path]
                ])
            else:
                self.install_commands.append([
                    f"Installing {pkg}", "sudo", ["-S", "apt-get", "install", "-y", pkg]
                ])

        
        serverCommand = -1
        sftpCommand = -1
        libfltk = -1
        libfltk_images = -1 
        for i, command in enumerate(self.install_commands):
            if "openssh-server" in command[0]:
                serverCommand = i
                print("openssh-server")
                print(i,"\n")
            if "openssh-sftp" in command[0]:
                sftpCommand = i
                print("openssh-sftp")
                print(i,"\n")
            if "libfltk1.3" in command[0]:
                libfltk = i
            if "libfltk-images" in command[0]:
                libfltk_images = i
        if serverCommand != -1 and sftpCommand != -1:
            print("switching command indexes for openssh-server and openssh-sftp")
            self.install_commands[sftpCommand], self.install_commands[serverCommand] = self.install_commands[serverCommand], self.install_commands[sftpCommand]
            if libfltk > libfltk_images:
                self.install_commands[libfltk], self.install_commands[libfltk_images] = self.install_commands[libfltk_images], self.install_commands[libfltk]
        else:
            print("serverCommand: ", self.install_commands[serverCommand], "; sftpCommand: ", self.install_commands[sftpCommand])
            print("Error openssh-server command and openssh-sftp command not swapped. OpenSSH might not be installed correctly")
            return

    def startInstallation(self):
        self.startButton.setEnabled(False)
        self.startButton.setVisible(False)
        self.progressBar.setVisible(True)
        self.statusLabel.setVisible(True)

        script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        script_dir = self.verify_resource_directory(script_dir)
        self.resource_dir = script_dir
        self.update_resource_paths(script_dir)

        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.readyReadStandardError.connect(self.read_error)
        self.process.finished.connect(self.process_finished)

        # self.updateMessage("Enter Docker Credentials")
        # self.request_docker()
        # self.updateMessage("Enter Bitbucket Credentials")
        # self.request_bitbucket()
        self.networkSetup()
        self.install_commands.extend(self.post_install_commands)
        self.total_commands = len(self.install_commands)
        self.request_sudo()
        for i in self.install_commands:
            print(i)

        self.startProcess()

    def startProcess(self):
        command = self.install_commands.pop(0)
        # if "Logging into sudo" in command[0]:
        #     self.updateMessage("Logging into sudo")
        #     self.request_sudo()
            # command[2][0] = "\"" + self.sudo_password +"\""
            # print("command[2]: ", command[2])
        if command[0] == "Creating git directory":
            self.request_launch_location()
            command[2][0] = self.launch_parent_dir
            self.update_launch_paths()
        elif command[0] == "Removing existing launch directory":
            self.request_launch_location()
            # the command string is at index 1 of the argument list
            index = 1
            if len(command[2]) > index:
                command[2][index] = (
                    f'if [ -d "{self.launch_dir}" ]; then sudo rm -r "{self.launch_dir}"; fi'
                )
            self.update_launch_paths()
        elif command[0] == "moving launch directory":
            if "-C" in command[2]:
                index = command[2].index("-C") + 1
            else:
                # Fallback to original index when -C is expected
                index = 3
            if len(command[2]) > index:
                command[2][index] = self.launch_parent_dir + "/"
        elif command[0] == "Moving launch to git directory":
            index = 3 if command[1] == "sudo" else 2
            command[2][index] = self.launch_parent_dir + "/"
        elif command[0] == "Loading USRP FPGA":
            dialog = RadioConfigDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                device = dialog.device_combo.currentText()
                addr = dialog.conn_edit.text().strip()
                self.ensure_fpga_image(device)
                if device == "x310":
                    command[2] = [f"--args=type=x300,addr={addr}", f"--fpga-path={self.X310_FPGA_PATH}"]
                else:
                    serial_arg = f",serial={addr}" if addr else ""
                    command[2] = [f"--args=type=b200{serial_arg}", f"--fpga-path={self.B210_FPGA_PATH}"]
            else:
                # skip command if dialog cancelled
                self.progress += 1
                self.updateProgress(self.progress)
                self.statusLabel.setText(f"Processes left: {len(self.install_commands)}")
                if self.install_commands:
                    self.startProcess()
                return
        elif command[0] == "Shutting down system":
            box = QMessageBox(self)
            box.setWindowTitle("Confirm Shutdown")
            box.setText("Installation completed. Shut down now?")
            box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            choice = box.exec()
            if choice != QMessageBox.StandardButton.Yes:
                self.progress += 1
                self.updateProgress(self.progress)
                self.statusLabel.setText(f"Processes left: {len(self.install_commands)}")
                self.exitButton.setVisible(True)
                self.label.setText('Installation completed.')
                self.progressBar.setValue(100)
                return
        elif "clone" in command[2]:
            command[2][1] = command[2][1].replace("username", self.bitbucket_username)
            command[2][1] = command[2][1].replace("password", self.bitbucket_password)
            command[2][3] = command[2][3].replace("branch_name", self.branch_name)
            print("command[1]", command[1])
        elif "docker" in command[2] and "login" in command[2]:
            try:
                user_index = command[2].index("-u") + 1
                pass_index = command[2].index("-p") + 1
                command[2][user_index] = self.docker_username
                command[2][pass_index] = self.docker_password
            except ValueError:
                pass
        elif "Setting up ovpn profile" == command[0]:
            command[2][2] = self.ovpn_profile
        #elif "docker" in command[1] and "load" in command[2][1]:
            #self.process.start("docker", ["image", "ls", "docker-trex.artifactory.parsons.us/trex/"+command[0]])
            #if command[0] in self.process.readAllStandardOutput().data().decode():
                #self.progress += 1
                #self.updateProgress(self.progress)
                #print("This worked")
                #print("docker image", command[0]," already exists")
                #return
        elif "running dc_calibration" in command[0]:
            self.request_network_config()
        else:
            print("command: ", command)
        description = command[0]
        self.current_command = description
        self.label.setText(description)
        if description == "Loading USRP FPGA":
            self.logsChecked.setChecked(True)
        self.statusLabel.setText(f"Processes left: {len(self.install_commands)}")
        print("Executing command: ", command[1]+" "+" ".join(command[2]))
        self.updateMessage(command[0])
        self.process.start(command[1], command[2])
        print("End of startProcess")

    def logs(self, state):
        if state == Qt.CheckState.Checked.value:
            self.logsText.setVisible(True)
        else:
            self.logsText.setVisible(False)

    def updateProgress(self, value):
        self.progressBar.setValue(int(value/(self.total_commands+1) * 100))

    def updateMessage(self, message):
        self.label.setText(message)

    def quitWindow(self):
        QApplication.instance().quit()

 
    def request_sudo(self):
        self.center_layout.addWidget(self.sudoDialog)
        self.center_layout.setAlignment(self.sudoDialog, Qt.AlignmentFlag.AlignCenter)
        self.sudoDialog.visible()
        self.sudoDialog.input2.setFocus()
        if self.sudoDialog.exec() == QDialog.DialogCode.Accepted:
            self.sudoDialog.setVisible(False)
            self.sudo_username, self.sudo_password, nothing2 = self.sudoDialog.get_inputs()
            if not self.sudo_username:
                self.sudo_username = getpass.getuser()
            print("Sudo username: ", self.sudo_username, ", sudo password: ", self.sudo_password, ", branch: ", nothing2)
        self.center_layout.removeWidget(self.sudoDialog)


    def request_launch_location(self):
        """Set the launch directory to the xmmgr user's home."""
        self.launch_parent_dir = "/home/xmmgr"
        self.launch_dir = os.path.join(self.launch_parent_dir, "launch")
        print("launch directory set to", self.launch_dir)
    
    def request_network_config(self):
        print('requesting network configuration')
        self.center_layout.addWidget(self.networkDialog)
        if self.networkDialog.exec() == QDialog.DialogCode.Accepted:
            self.center_layout.removeWidget(self.networkDialog)


    def update_launch_paths(self):
        for cmd in self.install_commands:
            updated_args = []
            for arg in cmd[2]:
                if "/home/xmmgr/git/trexinstaller" in arg:
                    updated_args.append(arg)
                    continue
                if arg.startswith("/home/xmmgr/git/launch"):
                    arg = arg.replace("/home/xmmgr/git/launch", self.launch_dir)
                elif arg.startswith("/home/xmmgr/git/"):
                    arg = arg.replace("/home/xmmgr/git", self.launch_parent_dir)
                elif arg == "/home/xmmgr/git":
                    arg = self.launch_parent_dir
                updated_args.append(arg)
            cmd[2] = updated_args

    def update_resource_paths(self, script_dir):
        replacements = {
            "/home/xmmgr/Downloads/launch.tar.gz": os.path.join(script_dir, "launch.tar.gz"),
            os.path.join(SCRIPT_DIR, "launch.tar.gz"): os.path.join(script_dir, "launch.tar.gz"),
            "/home/xmmgr/Downloads/postgres.tar.gz": os.path.join(script_dir, "postgres.tar.gz"),
            os.path.join(SCRIPT_DIR, "postgres.tar.gz"): os.path.join(script_dir, "postgres.tar.gz"),
            "/home/xmmgr/Downloads/node-webserver.tar.gz": os.path.join(script_dir, "node-webserver.tar.gz"),
            os.path.join(SCRIPT_DIR, "node-webserver.tar.gz"): os.path.join(script_dir, "node-webserver.tar.gz"),
            "/home/xmmgr/Downloads/client.tar.gz": os.path.join(script_dir, "client.tar.gz"),
            os.path.join(SCRIPT_DIR, "client.tar.gz"): os.path.join(script_dir, "client.tar.gz"),
            "/home/xmmgr/Downloads/services.tar.gz": os.path.join(script_dir, "services.tar.gz"),
            os.path.join(SCRIPT_DIR, "services.tar.gz"): os.path.join(script_dir, "services.tar.gz"),
            "/home/xmmgr/Downloads/signal.tar.gz": os.path.join(script_dir, "signal.tar.gz"),
            os.path.join(SCRIPT_DIR, "signal.tar.gz"): os.path.join(script_dir, "signal.tar.gz"),
            "/home/xmmgr/Downloads/createDesktop.sh": os.path.join(script_dir, "createDesktop.sh"),
            os.path.join(SCRIPT_DIR, "createDesktop.sh"): os.path.join(script_dir, "createDesktop.sh"),
            "/home/xmmgr/Downloads/OpenVPN/": os.path.join(script_dir, "OpenVPN/"),
            os.path.join(SCRIPT_DIR, "OpenVPN/"): os.path.join(script_dir, "OpenVPN/"),
        }

        for cmd in self.post_install_commands:
            cmd[2] = [replacements.get(arg, arg) for arg in cmd[2]]

    def verify_resource_directory(self, script_dir):
        required_files = [
            "launch.tar.gz",
            "postgres.tar.gz",
            "node-webserver.tar.gz",
            "services.tar.gz",
            "signal.tar.gz",
            "client.tar.gz"
        ]
        missing = [f for f in required_files if not os.path.exists(os.path.join(script_dir, f))]
        if missing:
            msg = f"Resources missing in:\n{script_dir}\n" + "\n".join(missing)
            box = QMessageBox(self)
            box.setWindowTitle("Missing Resources")
            box.setText(msg + "\nUse this directory?")
            use_btn = box.addButton("Use This Directory", QMessageBox.ButtonRole.YesRole)
            browse_btn = box.addButton("Browse", QMessageBox.ButtonRole.NoRole)
            box.exec()
            if box.clickedButton() == browse_btn:
                selected_dir = QFileDialog.getExistingDirectory(self, "Select Resource Directory", script_dir)
                if selected_dir:
                    script_dir = selected_dir
        return script_dir

    def ensure_fpga_image(self, device: str) -> None:
        """Download the FPGA image for *device* if it is missing."""
        if device == "x310":
            target = self.X310_FPGA_PATH
            dtype = "x3xx"
            fname = "usrp_x310_fpga_XG.bit"
        else:
            target = self.B210_FPGA_PATH
            dtype = "b2xx"
            fname = "usrp_b210_fpga.bin"

        if os.path.exists(target):
            return

        self.logsText.append(f"Downloading {device} FPGA image...")
        try:
            subprocess.run(
                ["sudo", "-S", "uhd_images_downloader.py", "-t", dtype],
                check=False,
                text=True,
                input=f"{self.sudo_password}\n",
            )
        except FileNotFoundError:
            self.logsText.append("uhd_images_downloader.py not found")
            return

        search_dirs = ["/usr/local/share/uhd/images", "/usr/share/uhd/images"]
        for d in search_dirs:
            src = os.path.join(d, fname)
            if os.path.exists(src):
                os.makedirs(os.path.dirname(target), exist_ok=True)
                try:
                    shutil.copy(src, target)
                except Exception as exc:
                    self.logsText.append(str(exc))
                break

    def read_output(self):
        output = self.process.readAllStandardOutput().data().decode()
        if "error" in output.lower():
            print("Error: ", output)
            self.logsText.append(f"<font color='red'>{output}</font>")
        else:
            print(output)
            self.logsText.append(output)
            if "WARNING: apt does not have a stable CLI interface. Use with caution in scripts." in output:
                output = output.replace("WARNING: apt does not have a stable CLI interface. Use with caution in scripts.", "")

            if self.current_command == "Loading USRP FPGA":
                self.statusLabel.setText(output.strip())
            if "overwrite" in output:
                self.logsText.append(output)
                print(output)
                self.logsText.append("Saying yes to overwrite")
                # Send 'y' (yes) followed by a newline to confirm overwriting
                self.process.write(b"y\n")
            if "password for" in output:
                self.process.write(f"{self.sudo_password}\n".encode())
                self.logsText.append("self.sudo_password: "+self.sudo_password)
            if "New password:" in output or "Retype new password:" in output:
                self.process.write(f"{self.root_password}\n".encode())
                self.logsText.append("self.root_password: "+self.root_password)
            if "startVPN.service" in output:
                self.process.write(b"q\n")
        

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
            if "password for" in error:
                self.process.write(f"{self.sudo_password}\n".encode())
                self.logsText.append("self.sudo_password: "+self.sudo_password)

    def process_finished(self, exit_code, exit_status):
        self.logsText.append(f"Process finished with exit code {exit_code}")
        self.progress += 1
        self.updateProgress(self.progress)
        self.statusLabel.setText(f"Processes left: {len(self.install_commands)}")
        self.current_command = ""
        print("Processes left: ", len(self.install_commands))
        if self.install_commands:
            self.startProcess()
        else:
            self.exitButton.setVisible(True)
            self.label.setText('Installation completed.')
            self.progressBar.setValue(100)
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    qt_material.apply_stylesheet(app, theme='dark_blue.xml')
    window = MainWindow()
    window.show()
    app.exec()
