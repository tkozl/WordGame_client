# Network client interface for the game
# ===============================================================

from socket import *
from enum import Enum

# ===============================================================

# Possible types of server responses
class Answer(Enum):
    END = 1
    CORRECT = 2
    INCORRECT = 3
    IGNORED = 4
    GUESSED = 5
    ERROR = 6
    BAD_LOGIN = 7
    SUCCESS = 8
    NO_CONNECTION = 9
    TIME_OUT = 10

# ===============================================================

class Client:

    def __init__(self, ip :str, port :int, user :str, password :str, authType=1) -> None:
        self.__socket = socket(AF_INET, SOCK_STREAM)
        self.__user = user
        self.__password = password
        self.__ip = ip
        self.__port = port
        self.__authType = authType
    

    def __del__(self):
        try:
            self.socket.shutdown(SHUT_RDWR)
        except Exception:
            pass
        self.socket.close()


    @property
    def socket(self) -> None:
        return self.__socket
    

    @property
    def ip(self) -> None:
        return self.__ip
    

    @property
    def port(self) -> None:
        return self.__port
    

    def connect(self) -> tuple:
        try:
            self.socket.connect((self.ip, self.port))
            if self.__authType == 1:
                self.socket.send(bytes(self.__user + '\n', 'utf-8'))
                self.socket.send(bytes(self.__password + '\n', 'utf-8'))
            else:
                self.socket.send(bytes(self.__user + '\n' + self.__password + '\n', 'utf-8'))
            self.socket.settimeout(2.0)
            rsp = self.socket.recv(1024)
            rsp = rsp.decode('utf-8')
            if rsp[0] not in ('+', '-'):
                return (Answer.ERROR, rsp)
            if rsp[0] == '-':
                return (Answer.BAD_LOGIN, -1)
            if rsp[0] == '+':
                if len(rsp) == 1:
                    return (Answer.ERROR, rsp)
                else:
                    try:
                        key = int(rsp[1])
                        return (Answer.SUCCESS, key)
                    except Exception:
                        return (Answer.ERROR, rsp)
        except error:
            try:
                self.disconnect()
            except Exception:
                pass
            return (Answer.NO_CONNECTION, -1)
    

    def disconnect(self) -> None:
        try:
            self.socket.shutdown(SHUT_RDWR)
        except Exception:
            pass
        self.socket.close()
        self.__socket = socket(AF_INET, SOCK_STREAM)
    

    def listen(self) -> tuple:
        try:
            self.socket.settimeout(2.0)
            msg = self.socket.recv(1024)
            msg = msg.decode('utf-8')
            if len(msg) > 0:
                msg = standardizeRsp(msg)
            if len(msg) > 0:
                return (Answer.SUCCESS, msg)
            else:
                return (Answer.NO_CONNECTION, '')
        except error as exc:
            if exc.__str__() == 'timed out':
                return (Answer.TIME_OUT, '')
            else:
                return (Answer.NO_CONNECTION, '')
    

    def send(self, msg :str) -> bool:
        try:
            self.socket.send(bytes(msg, 'utf-8'))
            return True
        except error:
            return False


# ===============================================================


def isInt(str) -> bool:
    try: 
        int(str)
        return True
    except ValueError:
        return False


def isRspCorrect(msg) -> bool:
    if msg in ('EMPTY MESSAGE', ''):
        return False
    msg = msg.split('\n')
    if msg[-1] == '':
        msg = msg[:-1]
    if msg[0] == '?':
        return True
    if msg[0] == '+1' or msg[0] == '+2' or msg[0] == '-':
        return True
    elif msg[0] == '#':
        return True
    elif msg[0] == '!':
        return True
    elif msg[0] == '=':
        try:
            if len(msg) >= 3 and isInt(msg[1]) and msg[2] == '?':
                return True
            else:
                for char in msg[1]:
                    if char not in ('0', '1'):
                        return False
                if len(msg[1]) > 0:
                    return True
                else:
                    return False
        except Exception:
            return False
    else:
        if len(msg) <= 2:
            for char in msg[0]:
                if char not in ('1', '2', '3', '4'):
                    return False
            if len(msg[0]) != 0:
                return True
            else:
                return False
        else:
            try:
                if len(msg[0]) != 0 and isInt(msg[1]) and msg[2] == '?':
                    return True
            except Exception:
                return False


def standardizeRsp(rsp :str) -> str:
    newRsp = ''
    i = 0
    for char in rsp:
        if i == 0 and char in ('\0', '\n'):
            continue
        i += 1
        if char == '\0':
            newRsp += '\n'
        else:
            newRsp += char
    if len(newRsp) == 0:
        newRsp = 'EMPTY MESSAGE'
    return newRsp
