#%% Importing
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
from matplotlib.ticker import FuncFormatter
from textwrap import wrap

#%% Setting up the functions. 
# Theoretically the functions should be able to take all percentage based indicators with (almost) no changes.
# 
# Splitting between indicators. 
# The Social indicator is filtered to only use the value for all ages. 
# .copy() is used here to avoid a warning in pandas regarding chained operators.
def Splitter(data, indicator):
    df = data.loc[data["Indicator"]==indicator].copy()
    if len(df["Nature"].unique()) > 1:   
        df = df.loc[df["Nature"]=="G"]
    #Retrieving the indicator name for the plot later. 
    indname = df["SeriesDescription"].iloc[1]
    return df, indname

# Removing < > indicators and turning data to floats, changing percentages to fractions
def Cleaner(df):
    df.loc[:,["Value"]] = df["Value"].astype("str").map(lambda x: x.lstrip('<>'))
    df.loc[:,["Value"]] = df["Value"].astype("float")/100
    return df

# Filtering for most recent year which has both indicators for each country. Ranges from 2000 to 2017.
def FilterMaker(df1, df2):
    year_id = pd.merge(df1, df2, how="inner", on="GeoAreaName")
    year_id = year_id.loc[year_id["TimePeriod_x"]==year_id["TimePeriod_y"]]   
    # Return set of most recent year per country, and remove gaps in the index.
    year_set = year_id.groupby(["GeoAreaName"])["TimePeriod_x"].max().reset_index()
    return year_set
    
# Filtering the dataset to only contain the country + year combinations that have been selected previously.
def Filter(df, year_set):
    mid = pd.merge(year_set, df, how="left", left_on=["GeoAreaName", "TimePeriod_x"],\
        right_on=["GeoAreaName","TimePeriod"])
    out = mid.drop(["TimePeriod_x"], axis=1).sort_values(by="GeoAreaName")
    return out

# Sanity Check
def SanChecker(df1, df2):
    if df1.loc[:,["GeoAreaName"]].equals(df2.loc[:,["GeoAreaName"]]):
        return("Sanity Check: DataFrame Areas Match!")
    else: 
        return("Sanity Check: DataFrame Area Mismatch!")

# Setting up plotter function
def Plotter(df1, df2, indname1, indname2, indep_ind_num, dep_ind_num):
    sns.scatterplot(df1["Value"], df2["Value"], marker="D", color="DarkGreen")

    # Setting axis ticks to percentages. This is why the values had to be converted to fractions earlier.
    ax = plt.gca()
    ax.xaxis.set_major_formatter(FuncFormatter(FuncFormatter('{0:.0%}'.format))) 
    ax.yaxis.set_major_formatter(FuncFormatter(FuncFormatter('{0:.0%}'.format)))

    # Adding responsive and flexible labels
    xlab = '\n'.join(wrap(indname1, 45))
    ylab = '\n'.join(wrap(indname2, 45))
    ax.set(xlabel=xlab, ylabel=ylab)

    # Setting aspect ratio and axis limits
    plt.xlim(0,1)
    plt.ylim(0,1)
    ax.set_aspect(1)

    # Saving main plot
    plt.savefig("sdg_scatter_{0}_{1}.pdf"\
        .format(indep_ind_num, dep_ind_num), bbox_inches = "tight")
    plt.close()

# Finding correlation coefficients and returning them with context.
def Correlator(df1, df2, indname1, indname2, indep_ind_num, dep_ind_num):
    lin_corr, lin_corr_pval = stats.pearsonr(df1["Value"], df2["Value"])
    mono_corr, mono_corr_pval = stats.spearmanr(df1["Value"], df2["Value"])
    
    indicators_out = ("The indicators used are {0} ({1}) and {2} ({3})."\
        .format(indname1, indep_ind_num, indname2, dep_ind_num))
    lin_corr_out = ("\nThe Linear Correlation Coëfficient is estimated at {0}, with a p-value of {1}"\
        .format(round(lin_corr, 3), format(round(lin_corr_pval, 5),'.6f')))
    lin_p_val_out = (SignificanceChecker(lin_corr_pval))
    mono_corr_out = ("The Monotonic Correlation Coëfficient is estimated at {0}, with a p-value of {1}"\
        .format(round(mono_corr, 3), format(round(mono_corr_pval, 5),'.6f')))
    mono_p_val_out = (SignificanceChecker(mono_corr_pval))
    tradeoff_syn_out = (TradeOffChecker(np.mean([lin_corr, mono_corr])))
    return ("{0}\n{1}\n{2}\n{3}\n{4}\n{5}".format(indicators_out, lin_corr_out, lin_p_val_out, \
         mono_corr_out, mono_p_val_out, tradeoff_syn_out))
    
# Defining functions that summarize the results and draw conclusions.
def SignificanceChecker(p_value):
    if p_value > 0.1:
        return("This P-value is too high for the result to \
be considered statistically significant.")
    elif p_value > 0.05:
        return("This P-value is statistically significant at a level of 0.1.")
    elif p_value > 0.01: 
        return("This P-value is statistically significant at a level of 0.05.")
    else:
        return("This P-value is statistically significant at a level of 0.01.")

def TradeOffChecker(corr):
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

#%% Defining wrapper function to call everything previously defined.
def Wrapper(filename = "sdg_1.1.1_7.1.2.csv", indep_ind_num = "1.1.1", dep_ind_num = "7.1.2"):
    #Importing data
    data = pd.read_csv(filename)\
        [["Indicator", "SeriesDescription", "GeoAreaName", "TimePeriod", "Value", "Nature"]]
    #Splitting Data and clearing memory
    indep_set, indep_name = Splitter(data, indep_ind_num)
    dep_set, dep_name = Splitter(data, dep_ind_num)
    del data
    #Cleaning Data
    indep_set = Cleaner(indep_set)
    dep_set = Cleaner(dep_set)
    #Creating Filter
    year_set = FilterMaker(indep_set, dep_set)
    #Filtering Data
    indep_set = Filter(indep_set, year_set)
    dep_set = Filter(dep_set, year_set)
    #Saving Sanity Check output
    output1 = SanChecker(indep_set, dep_set)
    #Plotting data and saving plot
    Plotter(indep_set, dep_set, indep_name, dep_name, indep_ind_num, dep_ind_num)
    #Saving statistic output
    output2 = Correlator(indep_set, dep_set, indep_name, dep_name, indep_ind_num, dep_ind_num)
    final_out = "{0}\n\n{1}".format(output1, output2)
    return final_out

#%% Running Wrapper and printing output
print(Wrapper())
