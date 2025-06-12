import sys
import time
import os
import csv

import subprocess
import tempfile

import threading
from PyQt6.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QInputDialog, QLineEdit, QProgressBar, QVBoxLayout, QWidget, QDialog, QLabel
from PyQt6.QtGui import QGuiApplication
import pexpect

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TReX Installation")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        width = 800
        height = 500
        self.resize(width, height)
        screen = QGuiApplication.primaryScreen().geometry()
        x = int((screen.width() - width) / 2)
        y = int((screen.height() - height) / 2)
        self.move(x, y)
        self.vbox = QVBoxLayout(central_widget)
        self.show()
        self.progressWidget = InstallerGUI()
        self.vbox.addWidget(self.progressWidget) 

class Thread(QThread):
    _signal = pyqtSignal(int)
    def __init__(self):
        super(Thread, self).__init__()
    def __del__(self):
        self.wait()
    def run(self):
        for i in range(100):
            time.sleep(0.1)
            self._signal.emit(i)

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
        # Path to the directory containing the installer
        script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        thumb_drive_path = os.path.join(script_dir, "offlineInstall")

        # Ensure the thumb drive path exists
        if not os.path.exists(thumb_drive_path):
            raise FileNotFoundError(f"The thumb drive path {thumb_drive_path} does not exist.")

        # List all .deb files in the thumb drive directory
        deb_files = [f for f in os.listdir(thumb_drive_path) if f.endswith('.deb')]

        if not deb_files:
            print("No .deb files found on the thumb drive.")
        else:
            # Install each .deb file
            for i, deb_file in enumerate(deb_files):
                self.message.emit("Installing "+ deb_file)
                deb_file_path = os.path.join(thumb_drive_path, deb_file)
                try:
                    subprocess.run(f"sudo dpkg -i {deb_file_path}", shell=True, check=True)
                    print(f"Successfully installed {deb_file}")
                except subprocess.CalledProcessError as e:
                    print(f"Failed to install {deb_file}. Error: {e}")
                self.progress.emit(int(i/(len(deb_files)) * 100))

        print("Installation process completed.")

        downloads_dir = "/home/xmmgr/Documents/installWizard/"

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
        self.bitbucket_user = username.replace("@", "%40")
        self.bitbucket_password = password.replace("@", "%40")
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
        self.invisible()

    def invisible(self):
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.hide()
                print("Hiding :", str(widget))

    def visible(self):
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.show()
                print("Showing :", str(widget))           

    def get_inputs(self):
        return self.input1.text(), self.input2.text()

class InstallerGUI(QWidget):
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

        self.dockerDialog = InputDialog("Docker Login")
        self.layout.addWidget(self.dockerDialog)
        self.layout.setAlignment(self.dockerDialog, Qt.AlignmentFlag.AlignTop)

        self.bitbucketDialog = InputDialog("Bitbucket Login")
        self.layout.addWidget(self.bitbucketDialog)
        self.layout.setAlignment(self.bitbucketDialog, Qt.AlignmentFlag.AlignTop)

        self.progressBar = QProgressBar(self)
        self.progressBar.setVisible(False)
        self.progressBar.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.layout.addWidget(self.progressBar)

        self.startButton = QPushButton('Start Installation', self)
        self.startButton.clicked.connect(self.startInstallation)
        self.layout.addWidget(self.startButton)
        
        self.exitButton = QPushButton('Exit', self)
        self.exitButton.clicked.connect(self.close)
        self.exitButton.clicked.connect(self.quitWindow)
        self.exitButton.setVisible(False)
        self.layout.addWidget(self.exitButton)

        self.setLayout(self.layout)

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
        self.dockerDialog.visible()
        self.dockerDialog.input1.setFocus()
        if self.dockerDialog.exec() == QDialog.DialogCode.Accepted:
            username, password = self.dockerDialog.get_inputs()
            self.install_thread.set_user_input(username, password)
            print(f'username entered: {username}, password: {password}')
        # self.dockerDialog.invisible()
        # self.layout.remove(self.dockerDialog)

    def request_bitbucket(self):
        self.bitbucketDialog.visible()
        self.bitbucketDialog.input1.setFocus()
        if self.bitbucketDialog.exec() == QDialog.DialogCode.Accepted:
            username, password = self.bitbucketDialog.get_inputs()
            self.install_thread.set_bitbucket(username, password)
            print(f'username entered: {username}, password: {password}')
        # self.layout.remove(self.bitbucktDialog)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
