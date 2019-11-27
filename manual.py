
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