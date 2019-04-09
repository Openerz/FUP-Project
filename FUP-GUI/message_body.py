from message import ISerializable
import message
import struct


class BodyRequest(ISerializable):  # 파일 전송 요청 메세지(0x01)에 사용할 본문 클래스이다. FILESIZE와 FILENAME 데이터 속성을 갖는다.
    def __init__(self, buffer):
        if buffer != None:
            slen = len(buffer)

            # 1 unsigned long long, N character
            self.struct_fmt = str.format('=Q{0}s', slen - 8)
            self.struct_len = struct.calcsize(self.struct_fmt)
            if slen > 4:  # unsigned long long의 크기
                slen = slen - 4
            else:
                slen = 0

            unpacked = struct.unpack(self.struct_fmt, buffer)

            self.FILESIZE = unpacked[0]
            self.FILENAME = unpacked[1].decode(
                encoding='utf-8').replace('\x00', '')
        else:
            self.struct_fmt = str.format('=Q{0}s', 0)
            self.struct_len = struct.calcsize(self.struct_fmt)
            self.FILESIZE = 0
            self.FILENAME = ''

    def GetBytes(self):
        buffer = self.FILENAME.encode(encoding='utf-8')

        # 1 unsigned long long, N character
        self.struct_fmt = str.format('=Q{0}s', len(buffer))

        return struct.pack(
            self.struct_fmt,
            *(
                self.FILESIZE,
                buffer
            ))

    def GetSize(self):
        buffer = self.FILENAME.encode(encoding='utf-8')

        # 1 unsigned long long, N character
        self.struct_fmt = str.format('=Q{0}s', len(buffer))
        self.struct_len = struct.calcsize(self.struct_fmt)
        return self.struct_len


class BodyResponse(
    ISerializable):  # 파일 전송 요청에 대한 응답 메세지(0x02)에 사용할 본문 클래스이다. 요청 메세지의 MSGID와 수락 여부를 나타내는 RESPONSE 데이터 속성을 갖는다.
    def __init__(self, buffer):

        # 1 unsigned int, Byte
        self.struct_fmt = '=IB'
        self.struct_len = struct.calcsize(self.struct_fmt)

        if buffer != None:
            unpacked = struct.unpack(self.struct_fmt, buffer)

            self.MSGID = unpacked[0]
            self.RESPONSE = unpacked[1]
        else:
            self.MSGID = 0
            self.RESPONSE = message.DENIED

    def GetBytes(self):
        return struct.pack(
            self.struct_fmt,
            *(
                self.MSGID,
                self.RESPONSE
            ))

    def GetSize(self):
        return self.struct_len


class BodyData(ISerializable):  # 실제 파일을 전송하는 메세지(0x03)에 사용할 본문 클래스이다. 앞서 프로토콜 정의에서 언급되었던 것처럼 DATA 필드만 갖고 있다.
    def __init__(self, buffer):
        if buffer != None:
            self.DATA = buffer

    def GetBytes(self):
        return self.DATA

    def GetSize(self):
        return len(self.DATA)


class BodyResult(
    ISerializable):  # 파일 전송 결과 메세지, 메세지(0x04)에 사용할 본문 클래스이다. 요청 메세지의 MSGID와 성공 여부를 나타내는 RESULT 데이터 속성을 갖는다.
    def __init__(self, buffer):

        # 1 unsigned int, Byte
        self.struct_fmt = '=IB'
        self.struct_len = struct.calcsize(self.struct_fmt)
        if buffer != None:
            unpacked = struct.unpack(self.struct_fmt, buffer)
            self.MSGID = unpacked[0]
            self.RESULT = unpacked[1]
        else:
            self.MSGID = 0
            self.RESULT = message.FAIL

    def GetBytes(self):
        return struct.pack(
            self.struct_fmt,
            *(
                self.MSGID,
                self.RESULT
            ))

    def GetSize(self):
        return self.struct_len