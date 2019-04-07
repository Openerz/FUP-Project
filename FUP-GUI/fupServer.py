import sys

from _message.server import serverStart
from threading import Thread
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QDialog, QInputDialog, QMessageBox
from PyQt5 import uic

serverPort = 8080
serverIP = '127.0.0.1'
upload_dir = 'test'

_translate = QtCore.QCoreApplication.translate
ui = 'fupServer.ui'

class fupServer(QMainWindow):

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


    def upload(self):
        pass

    @staticmethod
    def start():
        t = Thread(target=serverStart, args=(upload_dir, serverIP, serverPort))
        t.start()

    @staticmethod
    def stop():
        pass

    @staticmethod
    def accept():
        QMessageBox.showinfo('About', 'About...')

app = QApplication([])
ex = fupServer()
sys.exit(app.exec())