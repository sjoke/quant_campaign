from quote_impl import QuoteImpl
# import os, sys
# sys.path.append("..")

from proto.type_pb2 import SDSDataType

from time import sleep
import sys,signal


class Quote():
    def __init__(self,host,port):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        self.api_ = QuoteImpl(host, port)
        self.stop_ = False
    
    def signal_handler(self,signal, frame):
        self.stop_ = True
        self.stop()
        sys.exit(0)

    def stop(self):
        self.api_.stop()

    def start(self):
        
        # 1. start tcp thread, connect
        self.api_.run()

        # 2. set user info
        # self.api_.setUserInfo("user1", "123456")
        self.api_.setUserInfo('McYSHk409183', '20231027')

        # load model
        self.api_.setModel('./lr.pk')

        # load offline feature
        self.api_.setFeature('./offline_featrures.txt')

        # load stock info
        self.api_.setStockInfo('./stock_info.csv')

        # 3. wait api quit
        while not self.stop_:
            sleep(1)
            
def main():
    # if len(sys.argv) < 3:
    #     print("usage: python demo.py ip port")
    #     sys.exit(0)
    # ip = sys.argv[1]
    # port = int(sys.argv[2])
    # print("ip:",ip," port:",port)
    q = Quote("45.40.234.224",9999)
    q.start()            


if __name__ == '__main__':
    main()