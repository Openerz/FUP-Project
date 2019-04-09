import os
import sys
import socket
import message

from message import Message
from message_header import Header
from message_body import BodyData
from message_body import BodyRequest
from message_util import MessageUtil
from threading import Thread
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QMessageBox, QFileDialog, QDialog
from PyQt5 import uic

CHUNK_SIZE = 4096
serverPort = 8080
serverIP = '127.0.0.1'
filepath = ''

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
        text, ok = QInputDialog.getText(self, 'Setting', 'IP:')

        if ok:
            global serverIP
            serverIP = str(text)
            self.label_ip.setText(_translate("MainWindow", str(text)))

    def setPort(self):
        text, ok = QInputDialog.getText(self, 'Setting', 'Port (1024~65535):')

        if ok:
            global serverPort
            try:
                serverPort = int(text)
                self.label_port.setText(_translate("MainWindow", str(text)))
            except ValueError:
                QMessageBox.critical(self, "Error", "Enter a number")

    def setFile(self):
        pass

    def openFile(self):
        fname = QFileDialog.getOpenFileName(self)
        self.lineEdit_file.setText(fname[0])

    @staticmethod
    def upload():
            t = Thread(target=clientStart, args=(serverIP, serverPort, filepath))
            t.start()

    def msErr(self):
        QMessageBox.critical(self, "Error", "Error")


def clientStart(bindIP, bindPort, bindpath):
    global serverPort, filepath
    serverIp = bindIP
    serverPort = bindPort
    filepath = bindpath

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create TCP socket

    try:
        print("Server: {0}:{1}".format(serverIp, serverPort))

        sock.connect((serverIp, serverPort))  # Accept Connection Request

        msgId = 0

        reqMsg = Message()
        filesize = os.path.getsize(filepath)
        reqMsg.Body = BodyRequest(None)
        reqMsg.Body.FILESIZE = filesize
        reqMsg.Body.FILENAME = filepath[filepath.rindex('\\') + 1:]

        msgId += 1
        reqMsg.Header = Header(None)
        reqMsg.Header.MSGID = msgId
        reqMsg.Header.MSGTYPE = message.REQ_FILE_SEND
        reqMsg.Header.BODYLEN = reqMsg.Body.GetSize()
        reqMsg.Header.FRAGMENTED = message.NOT_FRAGMENTED
        reqMsg.Header.LASTMSG = message.LASTMSG
        reqMsg.Header.SEQ = 0

        MessageUtil.send(sock, reqMsg) # Connect to the server, the client sends a file transfer request message.
        rspMsg = MessageUtil.receive(sock)  # Receive a response from the server

        if rspMsg.Header.MSGTYPE != message.REP_FILE_SEND:
            print("This is not a normal server response.{0}".
                  format(rspMsg.Header.MSGTYPE))
            exit(0)

        if rspMsg.Body.RESPONSE == message.DENIED:
            print("The server refused to send the file.")
            exit(0)

        with open(filepath, 'rb') as file:  # Prepare to open the file and send it to the server.
            totalRead = 0
            msgSeq = 0  # ushort
            fragmented = 0  # byte

            if filesize < CHUNK_SIZE:
                fragmented = message.NOT_FRAGMENTED
            else:
                fragmented = message.FRAGMENTED

            while totalRead < filesize:
                rbytes = file.read(CHUNK_SIZE)
                totalRead += len(rbytes)

                fileMsg = Message()
                fileMsg.Body = BodyData(rbytes)  # Send the file to the server
                                                 # in a 0x03 message before the transfer is complete.

                header = Header(None)
                header.MSGID = msgId
                header.MSGTYPE = message.FILE_SEND_DATA
                header.BODYLEN = fileMsg.Body.GetSize()
                header.FRAGMENTED = fragmented
                if totalRead < filesize:
                    header.LASTMSG = message.NOT_LASTMSG
                else:
                    header.LASTMSG = message.LASTMSG

                header.SEQ = msgSeq
                msgSeq += 1

                fileMsg.Header = header
                print("#", end='')

                MessageUtil.send(sock, fileMsg)

            print()

            rstMsg = MessageUtil.receive(sock)  # Get a receive to see if it's been sent properly

            result = rstMsg.Body
            print("File Receive Success: {0}".format(result.RESULT == message.SUCCESS))

    except Exception as err:
        print("Exception has occurred.")
        print(err)


    sock.close()
    print("The client finished.")

app = QApplication([])
ex = FupClient()
sys.exit(app.exec())