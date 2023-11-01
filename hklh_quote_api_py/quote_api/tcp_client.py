import socket
import queue
from .qtp_msg import QtpMsg
import threading,time

class TcpClient:
    def __init__(self):
        socket.setdefaulttimeout(5)
        
        self.q_ = queue.Queue(1024)
        self.data_ = b''
        self.running_ = True
        self.is_connect_ = False
        self.socket_ = None
        self.ip_ = ""
        self.port_ = 0
        self.connect_change_fun = None

    def isConnected(self):
        return self.is_connect_

    def setConnectCallback(self,fun):
        self.connect_change_fun = fun

    def onConected(self,status):
        if(self.connect_change_fun):
            self.connect_change_fun(status)

    def connectdChange(self,status,force_push=False):
        if self.is_connect_ != status or force_push :
            self.onConected(status)
        self.is_connect_ = status


    def __connect(self, ip, port):
        self.ip_ = ip
        self.port_ = port
        self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_.connect((ip, port))

    def __reconnect(self):
        self.__connect(self.ip_, self.port_)

    def __recv_data_len(self,size):
        self.data_ = b''
        while self.running_:
            try:
                if not self.isConnected():
                    time.sleep(3)
                    continue
                d = self.socket_.recv(size - len(self.data_))
                if len(d) == 0:
                    self.connectdChange(False)
                    self.socket_.close()
                    continue
                self.data_ += d
                if len(self.data_) == size:
                    return self.data_
            except Exception as e:
                time.sleep(3)

                continue
                
        return None


    def stop(self):
        self.running_ = False

    def recv_data(self):
        while self.running_:
            if not self.isConnected():
                time.sleep(3)
                continue
            ret = self.__recv_data_len(12)
            if ret is None:
                break
            msg = QtpMsg()
            msg.head.decode(self.data_)
            if msg.head.opt_len > 0:
                ret = self.__recv_data_len(msg.head.opt_len)
                if ret is None:
                 break
                msg.opt_data = self.data_[:]
            if msg.head.data_len > 0:
                ret =  self.__recv_data_len(msg.head.data_len)
                if ret is None:
                 break
                msg.data = self.data_[:]
            self.q_.put(msg)


    def run(self, ip, port):
        try:
            self.__connect(ip, port)
            self.connectdChange(True,True)
            return True
        except Exception as e:
            self.connectdChange(False)
            return False

    def send_data(self, data):
        try:
            if self.isConnected():
                self.socket_.send(data)
                return True
        except Exception as e:
            self.connectdChange(False)
        
        return False