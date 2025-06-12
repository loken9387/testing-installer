import sys
import os
import subprocess

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
    QLabel,
    QHBoxLayout,
    QSizePolicy,
    QTextBrowser,
    QCheckBox,
    QRadioButton,
    QFileDialog,
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

class OptionDialog(QDialog):
    def __init__(self, title):
        super().__init__()

        self.selected_option = None

        # Set up the layout
        self.layout = QVBoxLayout()

        # Create radio buttons for the two options
        self.option1 = QRadioButton("Offline install")
        self.option2 = QRadioButton("Online install")

        # Add radio buttons to the layout
        self.layout.addWidget(self.option1)
        self.layout.addWidget(self.option2)

        # Create the submit button
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit)

        # Add the submit button to the layout
        self.layout.addWidget(self.submit_button)

        # Set the layout for the widget
        self.setLayout(self.layout)

    def submit(self):
        if self.option1.isChecked():
            self.selected_option = "offline"
        elif self.option2.isChecked():
            self.selected_option = "online"
        else:
            QMessageBox.warning(self, "No Selection", "Please select an option before submitting.")
            return

        # Print the selected option (for demonstration purposes)
        print(f"Selected option: {self.selected_option}")

        # Close the widget
        self.accept()
        self.close()

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
    progress = 0
    sudo_password = ''
    root_password = 'root'
    bitbucket_username = ''
    bitbucket_password = ''
    docker_username = ''
    docker_password = ''
    branch_name = 'release/v2.4.1-baseline'
    base_url = "http://localhost:8080/api/missions/import/upload"
    ovpn_profile = "profile-"
    ovpn_number = 0
    install_method = ""
    install_commands = []

    # offline install commands
    offline_commands = [
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
        ["Loading USRP FPGA", "uhd_image_loader", ["--args=type=x300,addr=192.168.40.2", "--fpga-path=/scratch/images/usrp_x310_fpga_XG.bit"]],
        ["Setting rmem_max for usrp", "sudo", ["sysctl", "-w", "net.core.rmem_max=24912805"]],
        ["Setting wmem_max for usrp", "sudo", ["sysctl", "-w", "net.core.wmem_max=24912805"]],
        ["Making hosts.sh executable", "chmod", ["+x", "hosts.sh"]],
        ["Running hosts.sh", "sudo", ["./hosts.sh"]],
        ["Adding docker group", "sudo", ["groupadd", "docker"]],
        ["Forcing adding docker group if it doesn't exist", "sudo", ["groupadd", "-f", "docker"]],
        ["Adding user xmmgr to docker group", "sudo", ["usermod", "-aG", "docker", "xmmgr"]],
        ["Making daemon.sh executable", "chmod", ["+x", "daemon.sh"]],
        ["Running daemon.sh", "sudo", ["./daemon.sh"]],
        ["Restarting docker", "sudo", ["systemctl", "restart", "docker"]],
        ["Enabling docker", "sudo", ["systemctl", "enable", "docker"]],
        ["Checking docker status", "sudo", ["systemctl", "status", "docker"]],
        ["Running hosts.sh again", "sudo", ["./hosts.sh"]],
        ["Creating git directory", "mkdir", ["/home/xmmgr/git"]],
        ["Changing group of git directory to xmmgr", "sudo", ["chgrp", "-R", "xmmgr", "/home/xmmgr/git"]],
        ["Changing owner of git directory to xmmgr", "sudo", ["chown", "-R", "xmmgr", "/home/xmmgr/git"]],
        ["Removing existing launch directory", "sudo", ["rm", "-r", "/home/xmmgr/git/launch"]],
        ["moving launch directory", "tar", ["-xf", "/home/xmmgr/Downloads/launch.tar", "-C", "/home/xmmgr/git/"]],
        ["Moving launch to git directory", "sudo", ["mv", "launch", "/home/xmmgr/git/"]],
        ["Creating recordings directory", "mkdir", ["/home/xmmgr/recordings"]],
        ["Creating dc_calibration directory", "mkdir", ["/home/xmmgr/recordings/dc_calibration"]],
        ["Changing group of launch directory to xmmgr", "sudo", ["chgrp", "-R", "xmmgr", "/home/xmmgr/git/launch"]],
        ["Changing owner of launch directory to xmmgr", "sudo", ["chown", "-R", "xmmgr", "/home/xmmgr/git/launch"]],
        ["Changing group of recordings directory to xmmgr", "sudo", ["chgrp", "-R", "xmmgr", "/home/xmmgr/recordings"]],
        ["Changing owner of recordings directory to xmmgr", "sudo", ["chown", "-R", "xmmgr", "/home/xmmgr/recordings"]],
        ["Changing group of dc_calibration directory to xmmgr", "sudo", ["chgrp", "-R", "xmmgr", "/home/xmmgr/recordings/dc_calibration"]],
        ["Changing owner of dc_calibration directory to xmmgr", "sudo", ["chown", "-R", "xmmgr", "/home/xmmgr/recordings/dc_calibration"]],
        ["Running hosts.sh again", "sudo", ["./hosts.sh"]],
        ["Creating Missions", "mkdir", ["/home/xmmgr/missions"]],
        ["Adding read permission for webserver", "sudo", ["chmod", "664", "/home/xmmgr/git/launch/config/webserver/application.properties"]],
        ["creating postgres image", "sudo", ["docker", "load", "-i", "/home/xmmgr/Downloads/postgres.tar.gz"]],
        ["creating node-webserver image", "sudo", ["docker", "load", "-i", "/home/xmmgr/Downloads/node-webserver.tar.gz"]], 
        ["creating services image", "sudo", ["docker", "load", "-i", "/home/xmmgr/Downloads/services.tar.gz"]], 
        ["creating signal image", "sudo", ["docker", "load", "-i", "/home/xmmgr/Downloads/signal.tar.gz"]], 
        # The folllowing steps require knowledge about how dc_calibration will be run, how containers will be changes form bash to xmidas_node, etc.
        ["changing to bash mode", "sed", ["-i" , "s/xmidas_node/bash/g", "/home/xmmgr/git/launch/trex_environment.sh"]], 
        ["Creating Desktop icon", "sudo", ["/home/xmmgr/Downloads/createDesktop.sh"]],
        ["Copying OpenVPN files", "cp", ["/home/xmmgr/Downloads/OpenVPN/", "/home/xmmgr/", "-r"]],
        ["Adjusting OpenVPN file permissions", "sudo", ["chmod", "-R", "755", "/home/xmmgr/OpenVPN/"]],
        ["running dc_calibration", "sudo", ["docker", "exec", "node-service", "bash", "-c", "\"./root/.local/share/uhd/cal/dc_calibration.sh\""]],
        ["changing to xmidas mode", "sed", ["-i" , "10,$s/bash/xmidas_node/g", "/home/xmmgr/git/launch/trex_environment.sh"]], 
    ]

    # online install commands
    online_commands = [
        ["Updating apt package index", "sudo", ["-S", "apt-get", "update", "-y"]],
        ["Upgrading packages", "sudo", ["apt-get", "upgrade", "-y"]],
        ["Installing openssh-server", "sudo", ["apt", "install", "openssh-server", "-y"]],
        ["Starting ssh", "sudo", ["systemctl", "start", "ssh"]],
        ["Enabling ssh now", "sudo", ["systemctl", "enable", "ssh", "--now"]],
        ["Enabling ssh", "sudo", ["systemctl", "enable", "ssh"]],
        ["Disabling firewall", "sudo", ["ufw", "disable"]],
        ["Allowing port 22 to be used", "sudo", ["ufw", "allow", "ssh"]],
        ["Installing vim", "sudo", ["apt", "install", "vim", "-y"]],
        ["Installing locate", "sudo", ["apt", "install", "mlocate", "-y"]],
        ["Installing find", "sudo", ["apt", "install", "find"]],
        ["Installing Tigervncserver", "sudo", ["apt", "install", "tigervnc-standalone-server", "-y"]],
        ["Installing Tigervncviewer", "sudo", ["apt", "install", "tigervnc-viewer", "-y"]],
        ["Installing docker-compose", "sudo", ["apt", "install", "docker-compose", "-y"]],
        ["Installing net-tools", "sudo", ["apt", "install", "net-tools", "-y"]],
        ["Installing selinux-utils", "sudo", ["apt", "install", "selinux-utils", "-y"]],
        ["Installing gcc", "sudo", ["apt", "install", "gcc", "-y"]],
        ["Installing package needed to change gedit color scheme", "sudo", ["apt", "install", "dbus-x11", "-y"]],
        ["Installing xrdp", "sudo", ["apt", "install", "xrdp", "-y"]],
        ["Starting xrdp", "sudo", ["systemctl", "start", "xrdp"]],
        ["Enabling xrdp", "sudo", ["systemctl", "enable", "xrdp"]],
        ["Installing minicom to look at hoover stack", "sudo", ["apt", "install", "minicom", "-y"]],
        ["Installing minicom", "sudo", ["dpkg", "-i", "minicom_2.8-2_amd64.deb", "-y"]],
        ["Installing screen to look at gps", "sudo", ["apt", "install", "screen", "-y"]],
        ["Installing dos2unix for cpu testing to convert windows file to linux", "sudo", ["apt", "install", "dos2unix"]],
        ["Installing sensors for cpu testing", "sudo", ["apt", "install", "lm-sensors", "-y"]],
        ["Setting correct performance mode", "echo", ["performance", "|", "sudo", "tee", "/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"]],
        ["Allowing connections from any host", "xhost", ["+"]],
        ["Loading USRP FPGA", "uhd_image_loader", ["--args=type=x300,addr=192.168.40.2", "--fpga-path=/scratch/images/usrp_x310_fpga_XG.bit"]],
        ["Setting rmem_max for usrp", "sudo", ["sysctl", "-w", "net.core.rmem_max=24912805"]],
        ["Setting wmem_max for usrp", "sudo", ["sysctl", "-w", "net.core.wmem_max=24912805"]],
        ["Making hosts.sh executable", "chmod", ["+x", "hosts.sh"]],
        ["Running hosts.sh", "sudo", ["./hosts.sh"]],
        ["Adding docker group", "sudo", ["groupadd", "docker"]],
        ["Forcing adding docker group if it doesn't exist", "sudo", ["groupadd", "-f", "docker"]],
        ["Adding user xmmgr to docker group", "sudo", ["usermod", "-aG", "docker", "xmmgr"]],
        ["Making daemon.sh executable", "chmod", ["+x", "daemon.sh"]],
        ["Running daemon.sh", "sudo", ["./daemon.sh"]],
        ["Restarting docker", "sudo", ["systemctl", "restart", "docker"]],
        ["Enabling docker", "sudo", ["systemctl", "enable", "docker"]],
        ["Checking docker status", "sudo", ["systemctl", "status", "docker"]],
        ["Running hosts.sh again", "sudo", ["./hosts.sh"]],
        ["Creating git directory", "mkdir", ["/home/xmmgr/git"]],
        ["Changing group of git directory to xmmgr", "sudo", ["chgrp", "-R", "xmmgr", "/home/xmmgr/git"]],
        ["Changing owner of git directory to xmmgr", "sudo", ["chown", "-R", "xmmgr", "/home/xmmgr/git"]],
        ["Removing existing launch directory", "sudo", ["rm", "-r", "/home/xmmgr/git/launch"]],
        ["moving launch directory", "tar", ["-xf", "/home/xmmgr/Downloads/launch.tar", "-C", "/home/xmmgr/git/"]],
        ["Moving launch to git directory", "sudo", ["mv", "launch", "/home/xmmgr/git/"]],
        ["Creating recordings directory", "mkdir", ["/home/xmmgr/recordings"]],
        ["Creating dc_calibration directory", "mkdir", ["/home/xmmgr/recordings/dc_calibration"]],
        ["Changing group of launch directory to xmmgr", "sudo", ["chgrp", "-R", "xmmgr", "/home/xmmgr/git/launch"]],
        ["Changing owner of launch directory to xmmgr", "sudo", ["chown", "-R", "xmmgr", "/home/xmmgr/git/launch"]],
        ["Changing group of recordings directory to xmmgr", "sudo", ["chgrp", "-R", "xmmgr", "/home/xmmgr/recordings"]],
        ["Changing owner of recordings directory to xmmgr", "sudo", ["chown", "-R", "xmmgr", "/home/xmmgr/recordings"]],
        ["Changing group of dc_calibration directory to xmmgr", "sudo", ["chgrp", "-R", "xmmgr", "/home/xmmgr/recordings/dc_calibration"]],
        ["Changing owner of dc_calibration directory to xmmgr", "sudo", ["chown", "-R", "xmmgr", "/home/xmmgr/recordings/dc_calibration"]],
        ["Running hosts.sh again", "sudo", ["./hosts.sh"]],
        ["Creating Missions", "mkdir", ["/home/xmmgr/missions"]],
        ["Adding read permission for webserver", "sudo", ["chmod", "664", "/home/xmmgr/git/launch/config/webserver/application.properties"]],
        ["creating postgres image", "sudo", ["docker", "load", "-i", "/home/xmmgr/Downloads/postgres.tar.gz"]],
        ["creating node-webserver image", "sudo", ["docker", "load", "-i", "/home/xmmgr/Downloads/node-webserver.tar.gz"]], 
        ["creating services image", "sudo", ["docker", "load", "-i", "/home/xmmgr/Downloads/services.tar.gz"]], 
        ["creating signal image", "sudo", ["docker", "load", "-i", "/home/xmmgr/Downloads/signal.tar.gz"]], 
        # The folllowing steps require knowledge about how dc_calibration will be run, how containers will be changes form bash to xmidas_node, etc.
        ["changing to bash mode", "sed", ["-i" , "s/xmidas_node/bash/g", "/home/xmmgr/git/launch/trex_environment.sh"]], 
        ["Creating Desktop icon", "sudo", ["/home/xmmgr/Downloads/createDesktop.sh"]],
        ["Copying OpenVPN files", "cp", ["/home/xmmgr/Downloads/OpenVPN/", "/home/xmmgr/", "-r"]],
        ["Adjusting OpenVPN file permissions", "sudo", ["chmod", "-R", "755", "/home/xmmgr/OpenVPN/"]],
        ["running dc_calibration", "sudo", ["docker", "exec", "node-service", "bash", "-c", "\"./root/.local/share/uhd/cal/dc_calibration.sh\""]],
        ["changing to xmidas mode", "sed", ["-i" , "10,$s/bash/xmidas_node/g", "/home/xmmgr/git/launch/trex_environment.sh"]], 
    ] 

    # branch_name = 'release/v2.4.1-baseline'
    def __init__(self):
        super().__init__()
        print("Init")
        self.launch_parent_dir = os.path.join(os.path.expanduser("~"), "git")
        self.launch_dir = os.path.join(self.launch_parent_dir, "launch")
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
        self.installMethodDialog = OptionDialog("Installation Method")
        self.sudoDialog = InputDialog("Sudo Login")
        self.ovpnDialog = InputDialog("OVPN Profile Number")
        self.networkDialog = NetworkInfoDialog()

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
    
    def offlineSetup(self):
        script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        thumb_drive_path = os.path.join(script_dir, "dependencies")
        self.update_resource_paths(script_dir)
        print("offlineSetup() function")

        # Ensure the thumb drive path exists
        if not os.path.exists(thumb_drive_path):
            raise FileNotFoundError(f"The thumb drive path {thumb_drive_path} does not exist.")

        # List all .deb files in the thumb drive directory
        deb_files = [f for f in os.listdir(thumb_drive_path) if f.endswith('.deb')]
        deb_files.sort()
        for i, deb_file in enumerate(reversed(deb_files)):
            deb_file_path = os.path.join(thumb_drive_path, deb_file)
            self.install_commands.insert(0,[f"Installing {deb_file}", "sudo", ["-S", "dpkg", "-i", deb_file_path]])
        
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

        script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        self.update_resource_paths(script_dir)

        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.readyReadStandardError.connect(self.read_error)
        self.process.finished.connect(self.process_finished)

        # self.updateMessage("Enter Docker Credentials")
        # self.request_docker()
        # self.updateMessage("Enter Bitbucket Credentials")
        # self.request_bitbucket()
        self.requestInstallationMethod()
        match self.install_method:
            case "online":
                self.install_commands.extend(self.online_commands)
            case "offline":
                self.offlineSetup()
                self.install_commands.extend(self.offline_commands)
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
            command[2][2] = self.launch_dir
            self.update_launch_paths()
        elif command[0] == "moving launch directory":
            command[2][3] = self.launch_parent_dir + "/"
        elif command[0] == "Moving launch to git directory":
            command[2][2] = self.launch_parent_dir + "/"
        elif "clone" in command[2]:
            self.updateMessage("Enter Bitbucket Credentials")
            self.request_bitbucket()
            command[2][1] = command[2][1].replace("username", self.bitbucket_username)
            command[2][1] = command[2][1].replace("password", self.bitbucket_password)
            command[2][3] = command[2][3].replace("branch_name", self.branch_name)
            print("command[1]", command[1])
        elif "docker" in command[2][0] and "login" in command[2][1]:
            self.updateMessage("Enter Docker Credentials")
            self.request_docker()
            print("need to update docker credentials")
            command[2][4] = self.docker_username
            command[2][6] = self.docker_password
        elif "Setting up ovpn profile" == command[0]:
            self.updateMessage("Enter OpenVPN profile number")
            self.request_ovpn()
            print("need to update ovpn profile")
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
        self.label.setText(description)
        print("Executing command: ", command[1]+" "+" ".join(command[2]))
        self.updateMessage(command[0])
        self.process.start(command[1], command[2])
        self.progress += 1
        self.updateProgress(self.progress)
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

    def onReset(self, input):
        self.label.setText("Next step: ", input)
        self.startButton.setVisible(False)
        self.exitButton.setVisible(False)
 
    def requestInstallationMethod(self):
        self.center_layout.addWidget(self.installMethodDialog)
        self.center_layout.setAlignment(self.installMethodDialog, Qt.AlignmentFlag.AlignCenter) 
        if self.installMethodDialog.exec() == QDialog.DialogCode.Accepted:
            self.installMethodDialog.setVisible(False)
            self.install_method = self.installMethodDialog.selected_option
            print("self.install_method = ", self.install_method)
        self.center_layout.removeWidget(self.installMethodDialog) 
    
    def request_sudo(self):
        self.center_layout.addWidget(self.sudoDialog)
        self.center_layout.setAlignment(self.sudoDialog, Qt.AlignmentFlag.AlignCenter)
        self.sudoDialog.visible()
        self.sudoDialog.input2.setFocus()
        if self.sudoDialog.exec() == QDialog.DialogCode.Accepted:
            self.sudoDialog.setVisible(False)
            nothing1, self.sudo_password, nothing2 = self.sudoDialog.get_inputs()
            print("Sudo username: ", nothing1, ", sudo password: ", self.sudo_password, ", branch: ", nothing2)
        self.center_layout.removeWidget(self.sudoDialog)

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
    
    def request_ovpn(self):
        self.center_layout.addWidget(self.ovpnDialog)
        self.center_layout.setAlignment(self.ovpnDialog, Qt.AlignmentFlag.AlignCenter)
        self.ovpnDialog.visible()
        self.ovpnDialog.input1.setFocus()
        if self.ovpnDialog.exec() == QDialog.DialogCode.Accepted:
            self.ovpnDialog.setVisible(False)
            x, self.ovpn_number, y = self.ovpnDialog.get_inputs()
            print("self.ovpn_number: ", self.ovpn_number, "; x: ", x, "; y: ", y)
            self.ovpn_profile = "profile-" + self.ovpn_number + ".ovpn"
            print("updating ovpn profile: ", self.ovpn_profile)
        self.center_layout.removeWidget(self.ovpnDialog)

    def request_launch_location(self):
        default_dir = self.launch_parent_dir
        selected_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Launch Directory Location",
            default_dir,
        )
        if selected_dir:
            self.launch_parent_dir = selected_dir
        self.launch_dir = os.path.join(self.launch_parent_dir, "launch")
        print("launch directory set to", self.launch_dir)
    
    def request_network_config(self):
        print('requesting network configuration')
        self.center_layout.addWidget(self.networkDialog)
        if self.networkDialog.exec() == QDialog.DialogCode.Accepted:
            self.center_layout.removeWidget(self.networkDialog)

    def set_bitbucket(self, username, password):
        self.bitbucket_username = username.replace("@", "%40")
        self.bitbucket_password = password.replace("@", "%40")
        # self.branch_name =

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
            "/home/xmmgr/Downloads/launch.tar": os.path.join(script_dir, "launch.tar"),
            "/home/xmmgr/Downloads/postgres.tar.gz": os.path.join(script_dir, "postgres.tar.gz"),
            "/home/xmmgr/Downloads/node-webserver.tar.gz": os.path.join(script_dir, "node-webserver.tar.gz"),
            "/home/xmmgr/Downloads/services.tar.gz": os.path.join(script_dir, "services.tar.gz"),
            "/home/xmmgr/Downloads/signal.tar.gz": os.path.join(script_dir, "signal.tar.gz"),
            "/home/xmmgr/Downloads/createDesktop.sh": os.path.join(script_dir, "createDesktop.sh"),
            "/home/xmmgr/Downloads/OpenVPN/": os.path.join(script_dir, "OpenVPN/"),
        }
        for cmd_list in (self.offline_commands, self.online_commands):
            for cmd in cmd_list:
                cmd[2] = [replacements.get(arg, arg) for arg in cmd[2]]

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
            if "overwrite" in output:
                self.logsText.append(output)
                print(output)
                self.logsText.append("Saying yes to overwrite")
                # Send 'y' (yes) followed by a newline to confirm overwriting
                self.process.write(b"y\n")
            if "password for xmmgr" in output:
                self.process.write(f"{self.sudo_password}\n".encode())
                self.logsText.append("self.sudo_password: "+self.sudo_password)
            if "New password:" in output or "Retype new password:" in output:
                self.process.write(f"{self.root_password}\n".encode())
                self.logsText.append("self.root_password: "+self.root_password)
            if "startVPN.service" in output:
                self.process.write(b"q\n")
            # elif "COMMAND_DONE" in output:
            #     self.progress += 1
            #     self.updateProgress(self.progress)
            # elif "COMMAND: " in output:
            #     output = output.replace("COMMAND: ", "")
            #     self.updateMessage(output)
            #     self.logsText.append(output)
            #     print(output)
            # else:
            #     print(output)
            #     self.logsText.append(output)
        

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
            if "password for xmmgr" in error:
                self.process.write(f"{self.sudo_password}\n".encode()) 
                self.logsText.append("self.sudo_password: "+self.sudo_password)

    def process_finished(self, exit_code, exit_status):
        self.logsText.append(f"Process finished with exit code {exit_code}")
        print("Processes left: ", len(self.install_commands))
        if self.install_commands:
            self.startProcess()
        else:
            self.exitButton.setVisible(True) 
            self.label.setText('Installation completed.')
            self.progressBar.setValue(100)
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    qt_material.apply_stylesheet(app, theme='dark_teal.xml')
    window = MainWindow()
    window.show()
    app.exec()
