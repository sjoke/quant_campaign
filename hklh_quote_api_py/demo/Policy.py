# -*- coding: utf-8 -*-
import numpy as np

class Policy():
    def __init__(self) -> None:
        self.position = dict()

    def update(self):
        pass
    
    def check(self, tick: dict):
        for k, v in tick.items():
            if k in ['hjcode', 'times']:
                if len(v) <= 0:
                    return False
            else:
                if np.isnan(v) or float(v) <= 1e-8:
                    return False
        return True

    def decide(self, tick):
        op = 0
        pred_y = 0
        features = []
        return op, pred_y, features