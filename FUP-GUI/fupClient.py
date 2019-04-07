import sys

from _message.client import clientStart
from threading import Thread
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QDialog, QInputDialog, QMessageBox
from PyQt5 import uic

serverPort = 8080
serverIP = '127.0.0.1'
filepath = '.\\test.txt'

_translate = QtCore.QCoreApplication.translate
ui = 'fupClient.ui'

class FupClient(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi(ui, self)
        self.initUI()

    def initUI(self):
        self.show()

    def setIP(self):
        text, ok = QInputDialog.getText(self, 'Set IP', 'IP:')

        if ok:
            global serverIP
            serverIP = str(text)
            self.label_ip.setText(_translate("MainWindow", str(text)))

    def setPort(self):
        text, ok = QInputDialog.getText(self, 'Set Port', 'Port (1024~65535):')

        if ok:
            global serverPort
            try:
                serverPort = int(text)
                self.label_port.setText(_translate("MainWindow", str(text)))
            except ValueError:
                QMessageBox.critical(self, "Error", "Enter a number")

    def setFile(self):
        pass

    @staticmethod
    def upload():
        t = Thread(target=clientStart, args=(serverIP, serverPort, filepath))
        t.start()

app = QApplication([])
ex = FupClient()
sys.exit(app.exec())