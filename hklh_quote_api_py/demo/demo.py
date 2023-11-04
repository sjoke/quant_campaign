# -*- coding: utf-8 -*-

from quote_impl import QuoteImpl
# import os, sys
# sys.path.append("..")
from random_policy import RandomPolicy
from model import LRModelPolicy
from recorder import Recorder
from proto.type_pb2 import SDSDataType

from time import sleep
import sys
import signal
from tqdm import tqdm


class Quote():
    def __init__(self, host, port):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        self.api_ = QuoteImpl(host, port, policy, recorder)
        self.stop_ = False

    def signal_handler(self, signal, frame):
        self.stop_ = True
        self.stop()
        sys.exit(0)

    def stop(self):
        self.api_.stop()

    def start(self):

        # 1. start tcp thread, connect
        self.api_.run()

        # 2. set user info
        self.api_.setUserInfo("McYSHk409183", "20231027")

        # 3. wait api quit
        while not self.stop_:
            sleep(1)

def run_local():
    import pandas as pd
    api = QuoteImpl("", "", policy, recorder, run_mode)
    df = pd.read_csv('history_quote\\df_20230901.csv', nrows=10000)
    # df = df.dropna(axis=0, how='any')
    df = df.sort_values(["date", "times"])
    for i, row in tqdm(df.iterrows(), total=len(df)):
        tick = row.to_dict()
        tick['hjcode'] = tick['code']
        del tick['code']
        tick['times'] = "{:0>6d}".format(int(tick['times'] / 1000))
        api.onTick(tick)
    
# def main():
    # if len(sys.argv) < 3:
    #     print("usage: python demo.py ip port")
    #     sys.exit(0)
    # ip = sys.argv[1]
    # port = int(sys.argv[2])
    # print("ip:",ip," port:",port)


if __name__ == '__main__':
    policy = LRModelPolicy(20230901)
    recorder = Recorder()
    run_mode = 'remote'
    if len(sys.argv) >= 2:
        run_mode = sys.argv[1]
    if run_mode == 'local':
        run_local()
    else:
        q = Quote("45.40.234.224", 9999)
        q.start()
    # main()
