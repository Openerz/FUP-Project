REQ_FILE_SEND = 0x01  # 메세지 타입 상수 정의
REP_FILE_SEND = 0x02
FILE_SEND_DATA = 0x03
FILE_SEND_RES = 0x04

NOT_FRAGMENTED = 0x00  # 파일 분할 여부 상수 정의
FRAGMENTED = 0x01

NOT_LASTMSG = 0x00  # 분할된 메세지의 마지막 여부 상수 정의
LASTMSG = 0x01

ACCEPTED = 0x00  # 파일 전송 수락 여부 상수 정의
DENIED = 0x01

FAIL = 0x00  # 파일 전송 성공 여부 상수 정의
SUCCESS = 0x01


class ISerializable:
    def GetBytes(self):  # 메세지, 헤더, 바디는 모두 이 클래스를 상속한다. 즉, 이들은 자신의 데이터를 바이트 배열로 변환하고 그 바이트 배열의 크기를 반환해야 한다.
        pass

    def GetSize():
        pass


class Message(ISerializable):
    def __init__(self):
        self.Header = ISerializable()
        self.Body = ISerializable()

    def GetBytes(self):
        buffer = bytes(self.GetSize())

        header = self.Header.GetBytes()
        body = self.Body.GetBytes()

        return header + body

    def GetSize(self):
        return self.Header.GetSize() + self.Body.GetSize()