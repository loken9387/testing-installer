from PyQt6.QtCore import QSize, Qt, QThread, pyqtSignal, QProcess
import sys
from PyQt6.QtWidgets import QApplication

class Test():
    command = ["Logging into sudo", "echo xmmgr | sudo -S bash -c 'echo \"xmmgr ALL=(ALL) NOPASSWD:ALL\" | EDITOR=\"tee -a\" visudo'"]
    process = QProcess()
    
    def __init__(self):
        self.process.finished.connect(self.process_finished)
        self.process.start(self.command[1])
   
    def process_finished(self):
        print("Process finished")
        print("Standard Output:", self.process.readAllStandardOutput().data().decode())
        print("Standard Error:", self.process.readAllStandardError().data().decode())

if __name__ == '__main__':
    test = Test()
    # Keep the application running to allow the process to complete
    app = QApplication(sys.argv)
    sys.exit(app.exec())