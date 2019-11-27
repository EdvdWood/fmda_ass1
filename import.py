#%% Importing
import pandas as pd
import re
import numpy as np
#%% Fast way

dataset = pd.read_csv("data.csv")

#%% Splitting

socio_set = dataset[dataset["Indicator"]=="1.1.1"]
socio_set = socio_set[socio_set["Nature"]=="G"]
nat_set = dataset[dataset["Indicator"]=="7.1.2"]

#%% Filtering for most recent year

socio_filter = socio_set.groupby(["GeoAreaName","TimePeriod"])["Value"].first().reset_index()
nat_filter = nat_set.groupby(["GeoAreaName","TimePeriod"])["Value"].first().reset_index()

yearid = pd.merge(socio_filter, nat_filter, how="inner", on="GeoAreaName")
yearid = yearid[yearid["TimePeriod_x"]==yearid["TimePeriod_y"]]

yearselected = yearid.groupby(["GeoAreaName"])["TimePeriod_x"].max().reset_index()

del socio_filter, nat_filter, yearid

#%%
socio_subset = pd.merge(yearselected, socio_set, how="left", left_on=["GeoAreaName", "TimePeriod_x"], right_on=["GeoAreaName","TimePeriod"])
nat_subset = pd.merge(yearselected, nat_set, how="left", left_on=["GeoAreaName", "TimePeriod_x"], right_on=["GeoAreaName","TimePeriod"])

del yearselected, nat_set, socio_set

#%%
socio_subset = socio_subset.sort_values(by="GeoAreaName")
nat_subset = socio_subset.sort_values(by="GeoAreaName")


#%% 

def grabber(file):
    fulldata = []
    for line in file:
        linedata = re.sub(',(?=[^"]*"[^"]*(?:"[^"]*"[^"]*)*$)',"",line)
        linedata = re.sub('"', '', linedata)
        linedata = linedata.split(",")
        fulldata.append(linedata)
    return fulldata

#%%

def columnist(list, colnum):
    collist = []
    counter = 0
    for sublist in list:
        if counter == 1:
            collist.append(sublist[colnum])
        else:
            counter += 1
    collist = np.array(collist)
    return collist

#%%

def subsplitter(prime, value, follows = "Banana"):
    try:
        if follows == "Banana": follows = prime
    except:
        follows = follows
    subsec = np.where(prime == value)
    sublist = follows[subsec]
    return sublist



#%%

with open("data.csv", "r") as f:
    dataset = grabber(f)
    print(dataset[0])
    pass

del(f)


#%%

first = columnist(dataset, 2)
second = columnist(dataset, 3)

test = subsplitter(first, "6.a.1")

        

    

# %%
