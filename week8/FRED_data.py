import matplotlib.pyplot as plt
import requests
import pandas as pd
import os
from fredapi import Fred
import pandas as pd
import re

import numpy as np
# import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter


API_KEY = os.getenv("FRED_API_KEY")

url = "https://api.stlouisfed.org/fred/series/search"
# fred = Fred(api_key=os.getenv("FRED_API_KEY"))

def get_FRED_series_ids(search_text="AA corporate bond"):
    params = {
        "search_text": search_text,
        "api_key": API_KEY,
        "file_type": "json"
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    # Extract series list
    series = data["seriess"]
    
    # Convert to DataFrame
    df = pd.DataFrame(series)
    
    # Show some useful columns
    cols = ["id", "title", "frequency", "units", "observation_start", "observation_end"]
    # print(df[cols])
    
    # # Optional: save results
    # df.to_csv("fred_series_search.csv", index=False)
    return df

df_AA = get_FRED_series_ids(search_text="AA corporate bond")
df_OAS  = get_FRED_series_ids(search_text="corporate bond OAS")

year_points = [1,2,3,4,5,10,15,20,25,30]
dfs = df_AA
df = pd.DataFrame([t for i,t in dfs.iterrows() if re.search(r"^\d+-Year", t['title']) and "Bond Spot Rate" in t['title']])
df["year"] = df["title"].str.extract(r"(\d+)").astype(int)
df = df[[y in year_points for y in df['year'].tolist()]]

df = df.sort_values(by="year")
# display(df.head(20),width=200)

# df['title'].tolist()

# print(df.groupby("frequency").size().reset_index(name="count"))

ids = df['id'].tolist()
# ids, year_points

data = {}
fred = Fred(api_key=os.getenv("FRED_API_KEY"))
for y, fred_id in zip(year_points,ids):
    data[y] = fred.get_series(fred_id)

# plt.figure(figsize=(18,5))
# for y in year_points:
#     plt.plot(data[y], label=str(y) + "-Year")
# plt.legend()
# plt.title("High Quality Corporate Bond Yields", fontsize=20)
# plt.ylabel("Bond Yield", fontsize=20)
# plt.show()

yc = pd.DataFrame(data)
# print(yc.shape)

plt.figure(figsize=(18,6))
for i in range(1, yc.shape[0], 50):
    plt.plot(yc.iloc[i,:], 'o-', label=str(yc.index[i])[:10])
plt.legend()
plt.title("High Quality Corporate Bond Yields", fontsize=20)
plt.ylabel("Bond Yield", fontsize=20)
plt.xlabel("Years to Maturity", fontsize=20)
plt.show()

###############   create movie of yield curve changes over time ###############

fig, ax = plt.subplots()

writer = FFMpegWriter(fps=10)

with writer.saving(fig, "corp_yc.mp4", dpi=100):
    for i in range(1,yc.shape[0],1):
        yc_date = str(yc.index[i])[:10]
        ax.clear()
        plt.plot(yc.iloc[i,:], 'o-', label=yc_date)
        plt.legend()
        plt.title("US Corporate Bond Index Yield", fontsize=20)   
        plt.ylabel("Bond Yield", fontsize=20)
        plt.xlabel("Years to Maturity", fontsize=20)
        ax.set_ylim(0, 15.0)

        writer.grab_frame()


quit()
##############
# Option Adjusted Spreads
#############
df_OAS_ = pd.DataFrame([t for i,t in df_OAS.iterrows() if re.search(r"\d+ Year", t['title']) and "Index Option-Adjusted Spread" in t['title']])

df_OAS_['years'] = [re.search(r"ICE BofA\s+(.*?)\s+Year", text).group(1) for text in df_OAS_['title'].to_list()]
df_OAS_["year one"] = df_OAS_["years"].str.extract(r"(\d+)").astype(int)
df_OAS_ = df_OAS_.sort_values('year one')
df_OAS_

OAS_data = {}
fred = Fred(api_key=os.getenv("FRED_API_KEY"))
for i,r in df_OAS_.iterrows():
    y, fred_id = r['years'], r['id']
    OAS_data[y] = fred.get_series(fred_id)

OAS_df = pd.DataFrame(OAS_data)

# plt.figure(figsize=(19,5))
# plt.plot(OAS_df, label=OAS_df.columns)
# plt.legend()
# plt.title("US Corporate Bond Index OAS")
# plt.ylabel("Option Adjusted Spread")
# plt.show()

OAS_yc = OAS_df

# plt.figure(figsize=(18,6))
# for i in range(1, OAS_yc.shape[0], 500):
#     plt.plot(OAS_yc.iloc[i,:], 'o-', label=str(OAS_yc.index[i])[:10])
# plt.legend()
# plt.title("US Corporate Bond Index OAS", fontsize=20)
# plt.ylabel("Option Adjusted Spread", fontsize=20)
# plt.xlabel("Years to Maturity", fontsize=20)
# plt.show()

###############   create movie of OAS changes over time ###############

fig, ax = plt.subplots()

writer = FFMpegWriter(fps=10)

with writer.saving(fig, "corp_OAS_yc.mp4", dpi=100):
    for i in range(1,OAS_yc.shape[0],10):
        yc_date = str(OAS_yc.index[i])[:10]
        ax.clear()
        plt.plot(OAS_yc.iloc[i,:], 'o-', label=yc_date)
        plt.legend()
        plt.title("US Corporate Bond Index OAS", fontsize=20)   
        plt.ylabel("Option Adjusted Spread", fontsize=20)
        plt.xlabel("Years to Maturity", fontsize=20)
        ax.set_ylim(0, 8.5)

        writer.grab_frame()