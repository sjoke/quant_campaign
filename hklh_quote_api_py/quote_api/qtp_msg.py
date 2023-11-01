from enum import Enum
import struct

class QtpOptIdEnum(Enum):
    kOptionId_Reserved = 60000                  # 保留ID
    kOptionId_SessionId = 60001                 # SessionId 后台程序使用
    kOptionId_PageInfo = 60002                  # 分页信息，PB协议查询回来的大部分都在PB包体里，这个主要非PB使用
    kOptionId_SubscribeKey = 60003              # 订阅字段，int64 那么长，每一位代表一个字段，可以选择订阅或查询少量字段，节约带宽
    kOptionId_ServerTime = 60004                # 服务器时间，ping请求应答中使用
    kOptionId_ReqId = 60005                     # 请求ID，查询时使用
    kOptionId_Extended = 61000                  # 未使用
    
class QtpOpt:
    def __init__(self,opt_id=0,data=b''):
        self.id = opt_id
        self.data = data
    
    def set_data(self,data):
        self.data = data

    def set_opt(self,data,id):
        self.data = data
        self.id = id

    def set_id(self,opt_id):
        self.id = opt_id
    
    def encode(self):
        str = struct.pack('HH', self.id, len(self.data))+self.data
        return str

    def decode(self,data):
        decode_data = self.data[0:3]
        self.id, opt_len = struct.unpack('HH', decode_data)
        if opt_len != len(data)-4:
            TypeError("optlen decode error")
        self.data = data[4:opt_len]
        
    

# 明确一点，每个ID都有确定的解析方式
# 除了kOptionId_PageInfo 全部都是INT64
# id[16]-len[16]-data[len]
class QtpOptions:
    def __init__(self,data=b''):
        self.data = data
        self.opts = []

    def decode(self,data):
        self.data = data
        decode_data = self.data[:]
        while len(decode_data) > 4:
            opt_id, opt_len = struct.unpack('HH', decode_data[0:4])
            opt = QtpOpt()
            if len(decode_data) < opt_len+4:
                break
            opt.set_opt(decode_data[4:opt_len+4],opt_id)
            decode_data = decode_data[opt_len+4:]
            self.opts.append(opt)
            
    def get_opt_data(self, opt_id):
        for item in self.opts:
            if item.id == opt_id:
                return item.data
        return None
    
    def encode(self):
        self.data = b''
        for item in self.opts:
            self.data = self.data + item.encode()
        return self.data

    def insert(self,opt):
        self.opts.append(opt)
    
    def remove(self,opt_id):
        for opt in self.opts:
            if opt.id == opt_id:
                self.opts.remove(opt)
                

class QtpMsgHead:
    def __init__(self, ver=0, msg_type=0, service=0, topic=0, opt_len=0, data_len=0):
        self.version = 0
        self.service = 0
        self.msg_type = 0
        self.topic = 0
        self.opt_len = 0
        self.data_len = 0

    def decode(self, data):
        self.version, self.service, self.msg_type, self.topic, self.opt_len, self.data_len = struct.unpack('BBHHHI', data)
        if self.data_len == len(data) - 12:
            return True
        return False

    def encode(self):
        str = struct.pack('BBHHHI', self.version, self.service, self.msg_type, self.topic, self.opt_len, self.data_len)
        return str

class QtpMsg:
    def __init__(self):
        self.head = QtpMsgHead()
        self.opts = QtpOptions()
        self.opt_data = b''
        self.data = b''
    
    def set_data(self,data):
        self.data = data[:]
        self.head.data_len = len(self.data)
    
    def set_opt_reqid(self,reqid):
        opt = QtpOpt(QtpOptIdEnum.kOptionId_ReqId,reqid)
        self.opts.insert(opt)

    def set_opt(self,opt_id,opt_data):
        opt = QtpOpt(opt_id,opt_data)
        self.opts.insert(opt)

    def remove_opt(self,opt_id):
        self.opts.remove(opt_id)

    def encode(self):
        opt_str = self.opts.encode()
        self.head.opt_len = len(opt_str)
        data_str = self.head.encode()
        data_str += opt_str
        if self.head.data_len > 0:
            data_str += self.data
        return data_str
    
    def get_opt(self, opt_id):
        return self.opts.get_opt_data(opt_id)
        
    def data_length(self):
        return self.head.opt_len + self.head.data_len
    
    def decode(self,data):
        if len(data) < 12:
            return False
        self.head.decode(data[0:12])
        if self.head.opt_len > 0:
            self.opts.decode(data[12:self.head.opt_len+12])
        self.data = data[self.head.opt_len+12:self.head.opt_len+12 + self.head.data_len]
        return True


