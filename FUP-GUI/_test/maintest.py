import os
import sys
import socket

import message
from message import Message

import client
from message_header import Header
from message_body import BodyData
from message_body import BodyRequest
from message_util import MessageUtil


from PyQt5.QtWidgets import QApplication, QVBoxLayout, QMainWindow, QLabel, QAction, qApp, QDesktopWidget, QInputDialog, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt


class FUPGui(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        serverIp = '1'

        Ip = serverIp
        label1 = QLabel('IP: ', self)
        label1.move(10, 20)

        labelIp = QLabel(Ip, self)
        labelIp.move(35, 20)

        font1 = label1.font()
        font1.setPointSize(12)

        label1.setFont(font1)
        labelIp.setFont(font1)

        layout = QVBoxLayout()
        layout.addWidget(label1)
        layout.addWidget(labelIp)

        self.setLayout(layout)
        self.setWindowTitle('FUP GUI')
        self.setGeometry(300, 300, 300, 300,)

        self.statusBar()
        self.center()
        self.menu()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def menu(self):
        # Exit
        exitAction = QAction(QIcon('exit.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit')
        exitAction.triggered.connect(qApp.quit)

        # IP
        ipsetAction = QAction(QIcon(), 'Set IP', self)
        ipsetAction.setShortcut('Ctrl+I')
        ipsetAction.setStatusTip('Set IPv4')
        ipsetAction.triggered.connect(self.setIp)

        # Port
        portsetAction = QAction(QIcon(), 'Set port', self)
        portsetAction.setShortcut('Ctrl+P')
        portsetAction.setStatusTip('Set port')
        portsetAction.triggered.connect(self.setPort)

        ## Menu
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        # File menu
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        # Settings menu
        settingsMenu = menubar.addMenu('&Settings')
        settingsMenu.addAction(ipsetAction)
        settingsMenu.addAction(portsetAction)

    def setIp(self):
        text, ok = QInputDialog.getText(self, 'Set IPv4', 'Enter the IPv4:')
        if ok:
            FUPGui.serverIp = text

    def setPort(self):
        text, ok = QInputDialog.getText(self, 'Set port', 'Enter the port:')

        if ok:
            self.le.setText(str(text))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FUPGui()
    sys.exit(app.exec_())