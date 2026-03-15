"""Message file Columns: 1.) Time: Seconds after midnight with decimal precision of at least milliseconds and up to nanoseconds depending on the requested period 2.) Type: 1: Submission of a new limit order 2: Cancellation (Partial deletion of a limit order) 3: Deletion (Total deletion of a limit order) 4: Execution of a visible limit order 5: Execution of a hidden limit order 7: Trading halt indicator
(Detailed information below) 3.) Order ID: Unique order reference number (Assigned in order flow) 4.) Size: Number of shares 5.) Price: Dollar price times 10000 (i.e., A stock price of $91.14 is given by 911400) 6.) Direction: -1: Sell limit order 1: Buy limit order Note: Execution of a sell (buy) limit order corresponds to a buyer (seller) initiated trade, i.e. Buy (Sell) trade.

type 5: [(1, 69946), (3, 63528), (4, 6559), (2, 868), (5, 606)]

direction 2 : [(-1, 72640), (1, 68867)]
"""

# https://lobsterdata.com/info/DataSamples.php

import re
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display
from datetime import datetime
from collections import Counter
from datetime import timedelta
from matplotlib.animation import FFMpegWriter

ddir = "OrderBook"
dirs = os.listdir(ddir)

# book file contains the bids and offers in blocks of 4 starting with the nearest to the midmarket
# the 4 values in each block correspond to ask, ask_size, bid, bid_size
# rows are padded with zeros block sizes as needed

dir1 = 'LOBSTER_SampleFile_MSFT_2012-06-21_50'
sdir = os.path.join(ddir, dir1)
csv_files = [f for f in os.listdir(sdir) if re.search(r'.csv$', f)]

book = pd.read_csv(os.path.join(sdir, csv_files[1]), header=None)
msg = pd.read_csv(os.path.join(sdir, csv_files[0]), header=None)

msg.columns = ['time','type','orderid','size','price','direction']
msg_time = [str(timedelta(seconds=t)) for t in msg['time']]

def get_bid_ask(bk):
    # trim each series to eliminate nulls padding each series
    ask, ask_size = np.array([(a/10000,s) for a,s in zip(bk[0::4], bk[1::4]) if s > 0]).T
    bid, bid_size = np.array([(b/10000,s) for b,s in zip(bk[2::4], bk[3::4]) if s > 0]).T
    
    # the last entries also need to be removed
    ask, ask_size, bid, bid_size = ask[:-1], ask_size[:-1], bid[:-1], bid_size[:-1]

    return ask, ask_size, bid, bid_size

# for i,bk in book[10:150011:20000].iterrows():
#     ask, ask_size, bid, bid_size = get_bid_ask(bk)

#     print(f"range = {max(bid) - min(bid)}")

#     plt.figure(figsize=(18,6))
#     plt.plot(bid, np.cumsum(bid_size),'o-', color='red', label='bid')
#     plt.plot(ask, np.cumsum(ask_size), 'o-',color='purple', label='ask')
#     plt.title(f"{dir1} - { msg_time[i]} - bid-offer level 2", fontsize=15)
#     plt.xlabel("price",fontsize=15)
#     plt.ylabel("size", fontsize=15)
#     plt.legend(loc='lower right',fontsize=15)
#     plt.show()

print(f"{dir1 = }")
title1 = dir1.replace("LOBSTER_SampleFile_","")

fig, ax = plt.subplots(figsize=(18,6))

writer = FFMpegWriter(fps=3)

with writer.saving(fig, "orderbook.mp4", dpi=100):
    for i,bk in book[2000:book.shape[0]:2000].iterrows():
        ask, ask_size, bid, bid_size = get_bid_ask(bk)
        # print(f"range = {min(bid)} - {max(ask)}")
        ax.clear()

        ax.plot(bid, np.cumsum(bid_size), 'o-', color='red', label='bid')
        ax.plot(ask, np.cumsum(ask_size), 'o-',color='purple', label='ask')
        ax.set_title(f"{title1} - { msg_time[i]} - level 2", fontsize=15)
        ax.set_xlabel("price",fontsize=15)
        ax.set_ylabel("size", fontsize=15)
        ax.legend(loc='lower right',fontsize=15)

        ax.set_xlim(30.0, 32.0)
        ax.set_ylim(0.0, 400000.0)
        
        writer.grab_frame()