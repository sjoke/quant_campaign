# -*- coding: utf-8 -*-
import os
from pub import DIR_QUOTE, DIR_OPERATION, DIR_PREDICTION, QUOTE_COLUMNS


class Recorder():
    def __init__(self) -> None:
        self.quote_dir = DIR_QUOTE
        self.operation_dir = DIR_OPERATION
        self.prediction_dir = DIR_PREDICTION
        if not os.path.exists(self.quote_dir):
            os.mkdir(self.quote_dir)
        if not os.path.exists(self.operation_dir):
            os.mkdir(self.operation_dir)
        # if not os.path.exists(self.prediction_dir):
        #     os.mkdir(self.prediction_dir)

    def record_quote(self, tick):
        arr = []
        for col in QUOTE_COLUMNS:
            arr.append("{}".format(tick[col]))
        date = tick['date']
        line = ",".join(arr) + '\n'

        f = os.path.join(self.quote_dir, "quote_{}.csv".format(date))
        with open(f, 'a') as fp:
            fp.write(line)

    def record_operation(self, tick, op, pred_y, features):
        date = tick['date']
        times = tick['times']
        hjcode = tick['hjcode']
        feats = ["{:.4f}".format(x) for x in features]
        feats = "|".join(feats)

        line = "{},{},{},{},{:.4f},{}\n".format(
            date, times, hjcode, op, pred_y, feats)
        f = os.path.join(self.operation_dir,
                         "operation_{}.csv".format(date))
        with open(f, 'a') as fp:
            fp.write(line)
    
    # def record_operation(self, tick, op):
    #     date = tick['date']
    #     times = tick['times']
    #     hjcode = tick['hjcode']
    #     line = "{},{},{},{}\n".format(date, times, hjcode, op)
    #     f = os.path.join(self.operation_dir,
    #                      "operation_{}.csv".format(date))
    #     with open(f, 'a') as fp:
    #         fp.write(line)

