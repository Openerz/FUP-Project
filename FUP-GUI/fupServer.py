import os
import sys
import socketserver

import message
from message import Message
from message_header import Header
from message_body import BodyRequest
from message_body import BodyResponse
from message_body import BodyResult
from message_util import MessageUtil

from threading import Thread
from PyQt5 import QtCore
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QMessageBox, QFileDialog
from PyQt5 import uic

serverPort = 8080
serverIP = '127.0.0.1'
upload_dir = ''

_translate = QtCore.QCoreApplication.translate
ui = 'fupServer.ui'

class fupServer(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(ui, self)

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

    def start(self):
        t = Thread(target=serverStart, args=(self, serverIP, serverPort, upload_dir))
        t.start()

    def stop(self):
        pass

    def saveFile(self):
        global upload_dir
        try:
            fname = QFileDialog.getExistingDirectory(self)
            self.lineEdit_file.setText(fname)
            upload_dir = fname
        except Exception as err:
            self.textLog.append('Exception has occurred.\n{0}\n'.format(err))
            self.textLog.moveCursor(QTextCursor.End)


class FileReceiveHandler(socketserver.BaseRequestHandler):
    def handle(self):
        ex.textLog.append('[-] Client Connection: {0}'.format(self.client_address[0]))
        ex.textLog.moveCursor(QTextCursor.End)

        client = self.request  # client socket

        reqMsg = MessageUtil.receive(client)  # Receive a file transfer request message sent by the client.

        if reqMsg.Header.MSGTYPE != message.REQ_FILE_SEND:
            client.close()
            return

        reqBody = BodyRequest(None)

        print("Do you want to accept? (yes / no):")
        answer = sys.stdin.readline()

        rspMsg = Message()
        rspMsg.Body = BodyResponse(None)
        rspMsg.Body.MSGID = reqMsg.Header.MSGID
        rspMsg.Body.RESPONSE = message.ACCEPTED

        rspMsg.Header = Header(None)

        msgId = 0
        rspMsg.Header.MSGID = msgId
        msgId = msgId + 1
        rspMsg.Header.MSGTYPE = message.REP_FILE_SEND
        rspMsg.Header.BODYLEN = rspMsg.Body.GetSize()
        rspMsg.Header.FRAGMENTED = message.NOT_FRAGMENTED
        rspMsg.Header.LASTMSG = message.LASTMSG
        rspMsg.Header.SEQ = 0

        if answer.strip() != "yes":  # If 'yes' is not entered, send a 'reject' answer to the client.
            rspMsg.Body = BodyResponse(None)
            rspMsg.Body.MSGID = reqMsg.Header.MSGID
            rspMsg.Body.RESPONSE = message.DENIED

            MessageUtil.send(client, rspMsg)
            client.close()
            return
        else:
            MessageUtil.send(client, rspMsg)  # Sends a "Accept" answer to the client when 'Yes' is entered.

            ex.textLog.append('Start file request...')
            ex.textLog.moveCursor(QTextCursor.End)

            fileSize = reqMsg.Body.FILESIZE
            fileName = reqMsg.Body.FILENAME
            recvFileSize = 0
            with open(upload_dir + "\\" + fileName, 'wb') as file:  # Create an upload file.
                fragmentedCnt = 0
                dataMsgId = -1
                prevSeq = 0

                while True:
                    reqMsg = MessageUtil.receive(client)
                    if reqMsg == None:
                        break

                    if reqMsg.Header.MSGTYPE != message.FILE_SEND_DATA:
                        break

                    if dataMsgId == -1:
                        dataMsgId = reqMsg.Header.MSGID
                    elif dataMsgId != reqMsg.Header.MSGID:
                        break

                    if prevSeq != reqMsg.Header.SEQ:  # Stop the if the message goes out of order.
                        ex.textLog.append('{0}, {1}\n'.format(prevSeq, reqMsg.Header.SEQ))
                        ex.textLog.moveCursor(QTextCursor.End)
                        break

                    fragmentedCnt += 1
                    prevSeq += 1

                    recvFileSize += reqMsg.Body.GetSize()  # Record the byte object some of the transferred files in a file created by the server.
                    file.write(reqMsg.Body.GetBytes())

                    if reqMsg.Header.LASTMSG == message.LASTMSG:  # The last message is out of the loop.
                        break

                ex.textLog.append('')
                file.close()

                ex.textLog.append('# Fragmented count: {0}'.format(fragmentedCnt))
                ex.textLog.moveCursor(QTextCursor.End)
                ex.textLog.append('Receive file size : {0} bytes\n'.format(recvFileSize))
                ex.textLog.moveCursor(QTextCursor.End)

                rstMsg = Message()
                rstMsg.Body = BodyResult(None)
                rstMsg.Body.MSGID = reqMsg.Header.MSGID
                rstMsg.Body.RESULT = message.SUCCESS

                rstMsg.Header = Header(None)
                rstMsg.Header.MSGID = msgId
                msgId += 1
                rstMsg.Header.MSGTYPE = message.FILE_SEND_RES
                rstMsg.Header.BODYLEN = rstMsg.Body.GetSize()
                rstMsg.Header.FRAGMENTED = message.NOT_FRAGMENTED
                rstMsg.Header.LASTMSG = message.LASTMSG
                rstMsg.Header.SEQ = 0

                if fileSize == recvFileSize:  # Compare the size of the file in the file transfer request with \
                    MessageUtil.send(client, rstMsg) # the size of the file actually received and send a success message if.
                else:
                    rstMsg.Body = BodyResult(None)
                    rstMsg.Body.MSGID = reqMsg.Header.MSGID
                    rstMsg.Body.RESULT = message.FAIL
                    MessageUtil.send(client, rstMsg)  # If there is a problem with the file size, send a failure message.

            ex.textLog.append('File transfer complete.\n')
            ex.textLog.moveCursor(QTextCursor.End)
            client.close()

def serverStart(self, bindIP, bindPort, bindDir):
    uploadIP = bindIP
    uploadPort = bindPort
    upload_Dir = bindDir
    try:
        if os.path.isdir(upload_Dir) == 0:
            os.mkdir(upload_Dir)
    except OSError as err:
        self.textLog.append('Exception has occurred.\n{0}\n'.format(err))
        self.textLog.moveCursor(QTextCursor.End)
        pass

    try:
        server = socketserver.TCPServer((uploadIP, uploadPort), FileReceiveHandler)
        self.textLog.append('Start File Upload Server...')
        self.textLog.append('IP: {0}:{1}\n'.format(uploadIP, uploadPort))
        self.textLog.moveCursor(QTextCursor.End)
        server.serve_forever()
    except Exception as err:
        print(err)

    print("The server finished.")

app = QApplication(sys.argv)
ex = fupServer()
ex.show()

sys.exit(app.exec())