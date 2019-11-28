#%% Importing
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns
import scipy.stats as stats

#%% Importing more quickly
dataset = pd.read_csv("data.csv")\
    [["Indicator", "GeoAreaName", "TimePeriod", "Value", "Nature"]]


#%% Splitting between indicators. 
# The Social indicator is filtered to only use the value for all ages.
socio_set = dataset[dataset["Indicator"]=="1.1.1"]
socio_set = socio_set[socio_set["Nature"]=="G"]
nat_set = dataset[dataset["Indicator"]=="7.1.2"]

#%% Removing < > indicators to turn data to floats, changing percentages to fractions
socio_set["Value"] = socio_set["Value"].astype("float")/100
nat_set["Value"] = nat_set["Value"].astype("str").map(lambda x: x.lstrip('<>'))
nat_set["Value"] = nat_set["Value"].astype("float")/100

del dataset
#%% Filtering for most recent year per country
yearid = pd.merge(socio_set, nat_set, how="inner", on="GeoAreaName")
yearid = yearid[yearid["TimePeriod_x"]==yearid["TimePeriod_y"]]

yearselected = yearid.groupby(["GeoAreaName"])["TimePeriod_x"].max().reset_index()

del yearid

#%% Filtering the split datasets to only contain the selected years.
socio_subset = pd.merge(yearselected, socio_set, how="left", left_on=["GeoAreaName", "TimePeriod_x"],\
    right_on=["GeoAreaName","TimePeriod"]).drop(["TimePeriod_x"], axis=1)
nat_subset = pd.merge(yearselected, nat_set, how="left", left_on=["GeoAreaName", "TimePeriod_x"],\
    right_on=["GeoAreaName","TimePeriod"]).drop(["TimePeriod_x"], axis=1)

del yearselected, nat_set, socio_set

#%% Sorting just to make sure. This should already be so.
socio_subset = socio_subset.sort_values(by="GeoAreaName")
nat_subset = nat_subset.sort_values(by="GeoAreaName")


#%% Sanity Check
def sanchecker(df1, df2):
    if df1["GeoAreaName"].equals(df2["GeoAreaName"]):
        return("DataFrame Areas Match")
    else: 
        return("DataFrame Area Mismatch")

print(sanchecker(socio_subset, nat_subset))

#%% Setting Up Main Plot
fig, ax = plt.subplots(1,1)
sns.scatterplot(socio_subset["Value"], nat_subset["Value"], marker="D", color="DarkGreen")

# Adding labels
plt.xlabel("Percentage of Population living in Poverty")
plt.ylabel("Proportion of Population Relying\n on Clean Fuels and Technology")
plt.xlim(0,1)
plt.ylim(0,1)

# Setting values to percentages
ax.xaxis.set_major_formatter(FuncFormatter(FuncFormatter('{0:.0%}'.format))) 
ax.yaxis.set_major_formatter(FuncFormatter(FuncFormatter('{0:.0%}'.format)))

# Setting Aspect Ratio 
ax.set_aspect(1)
plt.show()

# Saving Main plot
plt.savefig("sdg_scatter_1.1.1_7.1.2.pdf", bbox_inches = "tight")
del fig, ax, FuncFormatter
plt.close()

#%% Finding Correlation Coefficients
lincorr, lincorrpval = stats.pearsonr(socio_subset["Value"], nat_subset["Value"])
monocorr, monocorrpval = stats.spearmanr(socio_subset["Value"], nat_subset["Value"])

#%% Defining Output Functions 
def significancecheck(pvalue):
    if pvalue > 0.1:
        return("This P-value is too high for the result to \
            be considered statistically significant.")
    elif pvalue > 0.05:
        return("This P-value is statistically significant at a level of 0.1.")
    elif pvalue > 0.01: 
        return("This P-value is statistically significant at a level of 0.05.")
    else:
        return("This P-value is statistically significant at a level of 0.01.")

def tradeoff(corr):
    if corr < 0:
        return("\nThe negative correlation implies that a reduction in \
            Proportion of population below international poverty line is paired with \
                an increase in the Proportion of population with primary reliance on clean fuels \
                    and technology, implying a synergy between the two SDG's")
    elif corr > 0: 
        return("\nThe positive correlation implies that an increase in \
            Proportion of population below international poverty line is paired with \
                an increase in the Proportion of population with primary reliance on clean fuels \
                    and technology, implying a tradeoff between the two SDG's")
    else:
        return("\nThere is no correlation")
#%% Printing Outputs
print("The indicators used are Proportion of population below international poverty line (1.1.1) \
    and Proportion of population with primary reliance on clean fuels and technology (7.1.2).")
print("\nThe Linear Correlation Coëfficient is estimated at {0}, with a p-value of {1}"\
    .format(round(lincorr, 3), format(round(lincorrpval, 5),'.6f')))
print(significancecheck(lincorrpval))
print("The Monotonic Correlation Coëfficient is estimated at {0}, with a p-value of {1}"\
    .format(round(monocorr, 3), format(round(monocorrpval, 5),'.6f')))
print(significancecheck(monocorrpval))
print(tradeoff(np.mean([lincorr, monocorr])))