import os
import pandas as pd
import numpy as np

#from matplotlib.pyplot import plt
import pylab as plt

import argparse

def extract_loss(file, output, graphdata=None): #graphdata = None or 'loss' or 'avg_loss'
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
            
        if graphdata =='loss':
            # plot with x-axis as No. of steps (epochs) and y-axis as only loss
            fig = df.plot(title='Training Loss', x='No. of steps', y='loss', kind='line', grid=True).get_figure()
        elif graphdata =='avg_loss':
            # plot with x-axis as No. of steps (epochs) and y-axis as only loss
            fig = fig = df.plot(title='Training Loss', x='No. of steps', y='avg_loss', kind='line', grid=True).get_figure()
        else:
            # plot with x-axis as No. of steps (epochs) and y-axis as both loss and avg_loss
            fig = df.plot(title='Training Loss', x='No. of steps', kind='line', grid=True).get_figure()

        plt.show()
        fig.savefig(output)

    return loss, avg_loss

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f', help='file containing data for loss and avg loss')
    parser.add_argument('--graphtype', '-g', help='data to be displayed on the y-axis of the graph. defaults to both loss and avg_loss')
    parser.add_argument('--output', '-o', help='output file directory in png format')
    args = parser.parse_args()

    if os.path.isfile(args.file):

        loss, avg_loss = extract_loss(args.file, args.output, args.graphtype)



