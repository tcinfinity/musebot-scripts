import os
import pandas as pd
import numpy as np

#from matplotlib.pyplot import plt
import pylab as plt

import argparse

def extract_loss(file):
    with open(file, "r", encoding="utf8") as f:
        #f.read().split('\n')
        data = f.read().split('\n')
        data = [x for x in data if len(x) > 0]
        data = [x for x in data if x[0] == '[']        

        # [34710 | 5347.28] loss=0.03 avg=0.05
        steps = [x.split()[0][1::] for x in data]
        loss = [x.split()[3][5:] for x in data]
        avg_loss = [x.split()[4][4:] for x in data]

        # df = pd.DataFrame([loss, avg_loss], columns=['loss', 'avg_loss'], dtype=float)
        df = pd.DataFrame({'No. of steps':steps,'loss': loss, 'avg_loss': avg_loss}, dtype=float)

        # plot with x-axis as No. of steps (epochs) and y-axis as loss and avg_loss
        df.plot(title='Training Loss', x='No. of steps', kind='line', grid=True)
        plt.show()

    return loss, avg_loss

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f', help='file containing data for loss and avg loss')
    args = parser.parse_args()

    if os.path.isfile(args.file):

        loss, avg_loss = extract_loss(args.file)



