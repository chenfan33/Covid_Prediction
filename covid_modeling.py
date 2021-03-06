# -*- coding: utf-8 -*-
"""Covid Modeling.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1sixyg1fCkf6RjKEImq1rH1E6zKUQyffz

# First Model

refer to https://python.quantecon.org/sir_model.html from Thomas J. Sargent & John Stachurski
"""

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = (11, 5)  #set default figure size
import numpy as np
from numpy import exp
from scipy.integrate import odeint

pop_size = 3.3e8
γ = 1 / 18 #recovery rate
σ = 1 / 5.2 #infection rate

def F(x, t, R0=1.6):
    """
    Time derivative of the state vector.

        * x is the state vector (array_like)
        * t is time (scalar)
        * R0 is the effective transmission rate, defaulting to a constant

    """
    s, e, i = x

    # New exposure of susceptibles
    β = R0(t) * γ if callable(R0) else R0 * γ # model the transmission rate

    # Time derivatives
    ds = - β * s * i
    de = β * s * i - σ * e
    di = σ * e - γ * i

    return ds, de, di

i_0 = 1e-7
e_0 = 4 * i_0
s_0 = 1 - i_0 - e_0

x_0 = s_0, e_0, i_0

def test(R0, t_vec, x_init=x_0):
    """
    Solve for i(t) and c(t) via numerical integration,
    given the time path for R0.

    """
    G = lambda x, t: F(x, t, R0)
    s_path, e_path, i_path = odeint(G, x_init, t_vec).transpose()
    r_path = 1-s_path -e_path-i_path
    c_path = 1 - s_path - e_path       # cumulative cases
    return s_path, e_path, i_path, r_path

def te(paths, label, xlabel,times=t_vec):

    fig, ax = plt.subplots()

    for path, label in zip(paths, label):
        ax.plot(times, path, label=label)

    ax.legend(loc='upper left')
    plt.xlabel('time in days')
    plt.ylabel(xlabel)

    plt.show()

mm = ['Susceptible','Exposed','Infected','Recovered']
paths = [s_path, e_path, i_path, r_path]
te(paths, mm,'percentage in population')

s_path, e_path, i_path, r_path = test(r, t_vec)

def solve_path(R0, t_vec, x_init=x_0):
    """
    Solve for i(t) and c(t) via numerical integration,
    given the time path for R0.

    """
    G = lambda x, t: F(x, t, R0)
    s_path, e_path, i_path = odeint(G, x_init, t_vec).transpose()

    c_path = 1 - s_path - e_path       # cumulative cases
    return i_path, c_path,

t_length = 550
grid_size = 1000
t_vec = np.linspace(0, t_length, grid_size)

def plot_paths(paths, labels, xlabel,times=t_vec):

    fig, ax = plt.subplots()

    for path, label in zip(paths, labels):
        ax.plot(times, path, label=label)

    ax.legend(loc='upper left')
    plt.xlabel('time in days')
    plt.ylabel(xlabel)

    plt.show()

R0_vals = np.linspace(1.6, 3.0, 6)
labels = [f'$R0 = {r:.2f}$' for r in R0_vals]
i_paths, c_paths = [], []

for r in R0_vals:
    i_path, c_path = solve_path(r, t_vec)
    i_paths.append(i_path)
    c_paths.append(c_path)

plot_paths(i_paths, labels, 'percentage in population')

plot_paths(c_paths, labels, 'cumulative infected percentage')

"""## With intervention

"""

# η is the speed at which restrictions are imposed
def R0_mitigating(t, r0=3, η=1, r_bar=1.6):
    R0 = r0 * exp(- η * t) + (1 - exp(- η * t)) * r_bar
    return R0

η_vals = 1/5, 1/10, 1/20, 1/50, 1/100
labels = [fr'$\eta = {η:.2f}$' for η in η_vals]

fig, ax = plt.subplots()

for η, label in zip(η_vals, labels):
    ax.plot(t_vec, R0_mitigating(t_vec, η=η), label=label)

ax.legend()
plt.xlabel('time in days')
plt.ylabel('R(t)')
plt.show()

i_paths, c_paths = [], []

for η in η_vals:
    R0 = lambda t: R0_mitigating(t, η=η)
    i_path, c_path = solve_path(R0, t_vec)
    i_paths.append(i_path)
    c_paths.append(c_path)

plot_paths(i_paths, labels, 'percentage in population')

plot_paths(c_paths, labels,'infected percentage')

"""## Lockdown Simulation

"""

# initial conditions
i_0 = 25_000 / pop_size
e_0 = 75_000 / pop_size
s_0 = 1 - i_0 - e_0
x_0 = s_0, e_0, i_0

R0_paths = (lambda t: 0.5 if t < 30 else 2,
            lambda t: 0.5 if t < 120 else 2)

labels = [f'scenario {i}' for i in (1, 2)]

i_paths, c_paths = [], []

for R0 in R0_paths:
    i_path, c_path = solve_path(R0, t_vec, x_init=x_0)
    i_paths.append(i_path)
    c_paths.append(c_path)

plot_paths(i_paths, labels,'active infected percentage')

ν = 0.01

paths = [path * ν * pop_size for path in c_paths]
plot_paths(paths, labels, 'cummulative number of deaths')

paths = [path * ν * γ * pop_size for path in i_paths]
plot_paths(paths, labels, 'daily deaths')



"""# Second Model

refer to https://www.kaggle.com/lisphilar/covid-19-data-with-sir-model/output#Introduction

Citation:
Please cite CovsirPhy library and this notebook as follows.

CovsirPhy Development Team (2020-2021), CovsirPhy version [version number]: Python library for COVID-19 analysis with phase-dependent SIR-derived ODE models, https://github.com/lisphilar/covid19-sir


Hirokazu Takaya (2020-2021), Kaggle Notebook, COVID-19 data with SIR model, https://www.kaggle.com/lisphilar/covid-19-data-with-sir-model
"""

!pip install --upgrade "git+https://github.com/lisphilar/covid19-sir.git#egg=covsirphy"

!pip install openpyxl

from datetime import datetime
time_format = "%d%b%Y %H:%M"
datetime.now().strftime(time_format)

import pandas as pd
from pprint import pprint

import covsirphy as cs
cs.__version__

from google.colab import drive
drive.mount('/content/drive')

"""## Covid Data visualization"""

# Create instance of covsirphy.DataLoader class
data_loader = cs.DataLoader(directory="kaggle/input")
# Retrieve the dataset of the number of COVID-19 cases
# Kaggle platform: covid19dh.csv will be saved in /output/kaggle/working/input
# Local env: covid19dh.csv will be saved in kaggle/input
jhu_data = data_loader.jhu()

jhu_data.cleaned().tail()

jhu_data.subset("Japan", province=None).tail()

df = jhu_data.cleaned()
jhu_first_date, jhu_last_date = df["Date"].min(), df["Date"].max()
jhu_elapsed = (jhu_last_date - jhu_first_date).days
print(f"{jhu_elapsed} days have passed from the date of the first record.")

# We can use a method of cs.DataLoader()
population_data = data_loader.population()
# Show cleaned dataset
population_data.value("Japan", province=None)

"""## population pyramid"""

pyramid_data = data_loader.pyramid()

#the number of days persons of each age group usually go out.
_period_of_life_list = [
    "nursery", "nursery school", "elementary school", "middle school",
    "high school", "university/work", "work", "work", "work", "work",
    "retired", "retired", "retired"
]
df = pd.DataFrame(
    {
        "Age_first": [0, 3, 6, 11, 14, 19, 26, 36, 46, 56, 66, 76, 86],
        "Age_last": [2, 5, 10, 13, 18, 25, 35, 45, 55, 65, 75, 85, 95],
        "Period_of_life": _period_of_life_list,
        "Days": [3, 5, 6, 6, 7, 7, 6, 5, 5, 5, 4, 3, 2]
    }
)
# Adjustment by author
df["Types"] = df["Period_of_life"].replace(
    {
        "nursery": "school",
        "nursery school": "school",
        "elementary school": "school",
        "middle school": "school",
        "high school": "school",
        "university/work": "school/work"
    }
)
df["School"] = df[["Types", "Days"]].apply(lambda x: x[1] if "school" in x[0] else 0, axis=1)
df["Office"] = df[["Types", "Days"]].apply(lambda x: x[1] if "work" in x[0] else 0, axis=1)
df["Others"] = df["Days"] - df[["School", "Office"]].sum(axis=1)
df.loc[df["Others"] < 0, "Others"] = 0
df.loc[df.index[1:5], "School"] -= 1
df.loc[df.index[1:5], "Others"] += 1
df.loc[df.index[5], ["School", "Office", "Others"]] = [3, 3, 1]
df[["School", "Office", "Others"]] = df[["Days", "School", "Office", "Others"]].apply(
    lambda x: x[1:] / sum(x[1:]) * x[0], axis=1
).astype(np.int64)
df.loc[df.index[6:10], "Others"] += 1
df = df.drop(["Days", "Types"], axis=1)
# Show dataset
_out_df = df.copy()
_out_df

def go_out(country, pyramid_data=pyramid_data):

    """
    Return the estimated number of days people usually go out.
    Args:
        country (str): coutry name
        pyramid_data (covsirphy.PopulationPyramidData): pyramid dataset
    
    Returns:
        pandas.DataFrame
    """
    p_df = pyramid_data.subset(country)
    p_df["Cumsum"] = p_df["Population"].cumsum()
    df = pd.merge(_out_df, p_df, left_on="Age_last", right_on="Age", how="left")
    df["Population"] = df["Cumsum"].diff()
    df.loc[df.index[0], "Population"] = df.loc[df.index[0], "Cumsum"]
    df["Population"] = df["Population"].astype(np.int64)
    df["Portion"] = df["Population"] / df["Population"].sum()
    return df.drop(["Per_total", "Cumsum"], axis=1)

go_out("Italy")

ita_action_raw = pd.read_excel(
    "kaggle/input/Dataset_Italy_COVID_19.xlsx",
    sheet_name="Foglio1"
)
ita_action_raw.head()

"""## Visualize the total data

"""

data_cols = ["Infected", "Fatal", "Recovered"]
rate_cols = ["Fatal per Confirmed", "Recovered per Confirmed", "Fatal per (Fatal or Recovered)"]
total_df = jhu_data.total()
total_df = total_df.loc[total_df.index <= jhu_last_date, :]
total_df.tail()

cs.line_plot(total_df[data_cols], "Total number of cases over the world")

cs.line_plot(total_df[rate_cols], "Global rate over time", ylabel="", math_scale=False)

total_df[rate_cols].plot.kde()
plt.title("Kernel density estimation of the rates")
plt.show()

total_df[rate_cols].describe().T

"""## Including Growth Factors

Where C is the number of confirmed cases,
  Growth Factor =ΔCn/ΔCn−1
"""

covid_df = jhu_data.cleaned()
df = covid_df.pivot_table(
    index="Date", columns="Country", values="Confirmed", aggfunc="sum"
).fillna(method="ffill").fillna(0)
# Growth factor: (delta Number_n) / (delta Number_n)
df = df.diff() / df.diff().shift(freq="D")
df = df.replace(np.inf, np.nan).fillna(1.0)
# Rolling mean (window: 7 days)
df = df.rolling(7).mean().dropna().loc[:covid_df["Date"].max(), :]
# round: 0.01
growth_value_df = df.round(2)
growth_value_df.tail()

"""Grouping countires based on growth factor

Outbreaking: growth factor: > 1 for the last 7 days

Stopping: growth factor: < 1 for the last 7 days

At a crossroad: the others
"""

df = growth_value_df.copy()
df = df.iloc[-7:, :].T
day_cols = df.columns.strftime("%d%b%Y")
df.columns = day_cols
last_date = day_cols[-1]
# Grouping
more_col, less_col = "GF > 1 [straight days]", "GF < 1 [straight days]"
df[more_col] = (growth_value_df > 1).iloc[::-1].cumprod().sum(axis=0)
df[less_col] = (growth_value_df < 1).iloc[::-1].cumprod().sum(axis=0)
df["Group"] = df[[more_col, less_col]].apply(
    lambda x: "Outbreaking" if x[0] >= 7 else "Stopping" if x[1] >= 7 else "Crossroad",
    axis=1
)
# Sorting
df = df.loc[:, ["Group", more_col, less_col, *day_cols]]
df = df.sort_values(["Group", more_col, less_col], ascending=False)
growth_df = df.copy()
growth_df.head()

df = pd.merge(covid_df, growth_df["Group"].reset_index(), on="Country")
covid_df = df.loc[:, ["Date", "Group", *covid_df.columns[1:]]]
covid_df.tail()

"""### Outbreaking"""

df = growth_df.loc[growth_df["Group"] == "Outbreaking", :]
", ".join(df.index.tolist()) + "."
growth_df.loc[growth_df["Group"] == "Outbreaking", :].head()

df = covid_df.loc[covid_df["Group"] == "Outbreaking", ["Date", *data_cols]]
df = df.groupby("Date").sum()
df = df.iloc[:-1, :]
if not df.empty:
    cs.line_plot(df, "Group 1 (Outbreaking): Cases over time", y_integer=True)
    df.tail()

df = growth_df.loc[growth_df["Group"] == "Stopping", :]
", ".join(df.index.tolist()) + "."
growth_df.loc[growth_df["Group"] == "Stopping", :].head()

df = covid_df.loc[covid_df["Group"] == "Stopping", ["Date", *data_cols]].groupby("Date").sum()
if not df.empty:
    cs.line_plot(df, "Group 2 (Stopping): Cases over time", y_integer=True)
    df.tail()

df = growth_df.loc[growth_df["Group"] == "Crossroad", :]
", ".join(df.index.tolist()) + "."
growth_df.loc[growth_df["Group"] == "Crossroad", :].head()

df = covid_df.loc[covid_df["Group"] == "Crossroad", ["Date", *data_cols]].groupby("Date").sum()
cs.line_plot(df, "Group 3 (At a crossroad): Cases over time", y_integer=True)
df.tail()

"""## SIR Model

Estimated Mean Values of  R0:
R0 ("R naught") means "the average number of secondary infections caused by an infected host" (Infection Modeling — Part 1).

(Secondary data: Van den Driessche, P., & Watmough, J. (2002).)

2.06: Zika in South America, 2015-2016

1.51: Ebola in Guinea, 2014

1.33: H1N1 influenza in South Africa, 2009

3.5 : SARS in 2002-2003

1.68: H2N2 influenza in US, 1957

3.8 : Fall wave of 1918 Spanish influenza in Genova

1.5 : Spring wave of 1918 Spanish influenza in Genova
"""

# Set tau value and start date of records
# For explanation, the start date will be 01Jan2020
# This is not based on actual data
example_data = cs.ExampleData(tau=1440, start_date="01Jan2020")
# No records has been registered
example_data.cleaned()

# Model name
print(cs.SIR.NAME)
# Example parameter values
pprint(cs.SIR.EXAMPLE, compact=True)

model = cs.SIR
area = {"country": "Full", "province": model.NAME}
# Add records with SIR model
example_data.add(model, **area)
# Records with model variables
df = example_data.specialized(model, **area)
cs.line_plot(
    df.set_index("Date"),
    title=f"Example data of {model.NAME} model",
    y_integer=True
)

"""There is an inflection point of y (the number of currentry infected cases per total population). At this point, value of x (the number of susceptible cases per total population) is nearly equal to  1/R0."""

eg_r0 = model(model.EXAMPLE["population"], **model.EXAMPLE["param_dict"]).calc_r0()
df = example_data.specialized(model, **area)
x_max = df.loc[df["Infected"].idxmax(), "Susceptible"] / cs.SIR.EXAMPLE["population"]
(x_max, 1/eg_r0)

print(cs.SIRF.NAME)
# Example parameter values
pprint(cs.SIRF.EXAMPLE, compact=True)

eg_r0 = model(model.EXAMPLE["population"], **model.EXAMPLE["param_dict"]).calc_r0()
df = example_data.specialized(model, **area)
x_max = df.loc[df["Infected"].idxmax(), "Susceptible"] / cs.SIR.EXAMPLE["population"]
(x_max, 1/eg_r0)

# Set population value
population_data.update(cs.SIRF.EXAMPLE["population"], **area)
population_data.value(**area)

model = cs.SIRF
area = {"country": "Full", "province": model.NAME}
# Add records with SIR model
example_data.add(model, **area)
# Records with model variables
df = example_data.specialized(model, **area)
cs.line_plot(
    df.set_index("Date"),
    title=f"Example data of {model.NAME} model",
    y_integer=True
)

# Show records in JHU-style
sirf_snl = cs.Scenario(example_data, population_data, tau=1440, **area)
_ = sirf_snl.records()

# Set phases (phase: explained in "S-R trend analysis section")
# Records at 01Jan2020 will be removed because Recovered = 0
sirf_snl.clear(include_past=True)
sirf_snl.add().summary()

# Parameter estimation
sirf_snl.estimate(cs.SIRF, timeout=120)

print(setting_dict)

df = sirf_snl.summary()
setting_model = cs.SIRF(population=cs.SIRF.EXAMPLE["population"], **cs.SIRF.EXAMPLE["param_dict"])
setting_dict = {
    "Population": cs.SIRF.EXAMPLE["population"],
    "ODE": cs.SIRF.NAME,
    "Rt": setting_model.calc_r0(),
    "tau": 1440,
    **setting_model.calc_days_dict(1440),
    **cs.SIRF.EXAMPLE["param_dict"]
}
df = df.append(pd.Series(setting_dict, name="setting"))
df.fillna("-")

# Commented out IPython magic to ensure Python compatibility.
from collections import defaultdict
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import functools
from IPython.display import display, Markdown
import math
import os
from pprint import pprint
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib
from matplotlib.ticker import ScalarFormatter
# %matplotlib inline
import numpy as np
import pandas as pd
import dask.dataframe as dd
pd.plotting.register_matplotlib_converters()
import seaborn as sns
import scipy as sci
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import sympy as sym

sirf_snl.estimate_accuracy("0th")

"""### SEWIR MODEL"""

latent_period = 6 * 24 * 60
waiting_time = 7 * 24 * 60
latent_waiting_day = latent_period + waiting_time

df = cs.SIRF.EXAMPLE["param_dict"]
tau = 1440
eg_rho2, eg_rho3 = tau / latent_period, tau / waiting_time
(eg_rho2, eg_rho3)

param_dict = cs.SEWIRF.EXAMPLE["param_dict"]
param_dict.update({"rho2":eg_rho2, "eho3": eg_rho3})
pprint(param_dict, compact=True)

model = cs.SEWIRF
area = {"country": "Full", "province": model.NAME}
# Add records with SIR model
example_data.add(model, param_dict=param_dict, **area)
# Records with model variables
df = example_data.specialized(model, **area)
cs.line_plot(
    df.set_index("Date"),
    title=f"Example data of {model.NAME} model",
    y_integer=True
)

# Preset of SIR-F parameters
preset_dict = cs.SIRF.EXAMPLE["param_dict"]
preset_dict

area = {"country": "Theoretical"}
# Create dataset from 01Jan2020 to 31Jan2020
example_data.add(cs.SIRF, step_n=30, **area)

population_data.update(cs.SIRF.EXAMPLE["population"], **area)
population_data.value(**area)

# Show records with Scenario class
snl = cs.Scenario(example_data, population_data, tau=1440, **area)
record_df = snl.records()
display(record_df.head())
display(record_df.tail())

rho_before = cs.SIRF.EXAMPLE["param_dict"]["rho"]
rho_before

eg_out_df = go_out("Italy")
eg_out_df

gs_before = (eg_out_df[["School", "Office", "Others"]].sum(axis=1) * eg_out_df["Portion"]).sum()
gs_before

df = eg_out_df.copy()
df.loc[df["School"] + df["Office"] > 0, "Others"] += 1
df["School"] = 0
df["Office"] *= 0.5
eg_out_df_after = df.copy()
eg_out_df_after

df = eg_out_df_after.copy()
gs_after = (df[["School", "Office", "Others"]].sum(axis=1) * df["Portion"]).sum()
gs_after

rho_after = rho_before * (gs_after / gs_before)
rho_after / rho_before

"""## Prediction"""

# Set 0th phase from 02Jan2020 to 31Jan2020 with preset parameter values
snl.clear(include_past=True)
snl.add(end_date="31Jan2020", model=cs.SIRF, **preset_dict)
snl.summary()
# Add main scenario: the same parameter to 31Dec2020
snl.add(end_date="31Dec2020", name="Main")
# Add lockdown scenario
snl.clear(include_past=False, name="Lockdown")
snl.add(end_date="31Dec2020", name="Lockdown", rho=rho_after).summary()

_ = snl.simulate(name="Main")

snl.describe()

sigma_before = preset_dict["sigma"]
kappa_before = preset_dict["kappa"]
(sigma_before, kappa_before)

h_bar_before, s_bar_before = 0.5, 0.5


h_bar_after = h_bar_before * 0.1
s_bar_after = s_bar_before
(h_bar_after, s_bar_after)

sigma_after = sigma_before * (1 - h_bar_after * s_bar_after) / (1 - h_bar_before * s_bar_before)
sigma_after

"""### Italy"""

ita_scenario = cs.Scenario(country="Italy")
ita_scenario.register(jhu_data, population_data)
_ = ita_scenario.trend()

# ita_scenario = cs.Scenario(country="Italy")
# ita_scenario.register(jhu_data, population_data)
ita_scenario.records().tail()

_ = ita_scenario.trend()

ita_scenario.estimate(cs.SIRF, timeout=120)

ita_scenario.summary()

_ = ita_scenario.history_rate()

Rts = ita_scenario.summary().rho.to_numpy()
x = np.arange(len(Rts))

plt.plot(x, Rts)
plt.xlabel('phases')
plt.ylabel('Rt')
plt.show()

ita_scenario.get("Start", name="Main", phase="3rd")
c_before, c_after = 1.0, 0.81
ita_out_df = go_out("Italy")

df = ita_out_df.copy()
gs_before = (df[["School", "Office", "Others"]].sum(axis=1) * df["Portion"]).sum()
print(f"{round(gs_before, 1)} days in a week susceptible people go out.")

rho_before = ita_scenario.get("rho", name="Main", phase="1st")
rho_after = ita_scenario.get("rho", name="Main", phase="3rd")
gs_after = rho_after / rho_before / c_after * gs_before * c_before
print(f"{round(gs_after, 1)} days in a week susceptible people go out after lockdown.")

df = ita_out_df.copy()
df["School"] = 0
df.loc[df["Office"] > 0, "Office"] = 1
sum_so = (df[["School", "Office"]].sum(axis=1) * df["Portion"]).sum()
df.loc[df["Others"] > 0, "Others"] = round(gs_after - sum_so, 1)
ita_out_after_df = df.copy()
ita_out_after_df

df = ita_out_after_df.copy()
gs_after2 = (df[["School", "Office", "Others"]].sum(axis=1) * df["Portion"]).sum()
print(f"{round(gs_after2, 1)} days in a week susceptible people go out after lockdown.")

ita_scenario.clear()
ita_scenario.add(days=7)
ita_scenario.simulate().tail(7).style.background_gradient(axis=0)



"""### Japan"""

j_scenario = cs.Scenario(country="Japan")
j_scenario.register(jhu_data, population_data)
_ = ita_scenario.trend()
# ita_scenario = cs.Scenario(country="Italy")
# ita_scenario.register(jhu_data, population_data)
j_scenario.records().tail()

_ = j_scenario.trend()

j_scenario.estimate(cs.SIRF, timeout=120)

j_scenario.clear()
j_scenario.add(days=30)
j_scenario.simulate().tail(7).style.background_gradient(axis=0)

"""### China"""

c_scenario = cs.Scenario(country="China")
c_scenario.register(jhu_data, population_data)
_ = ita_scenario.trend()
# ita_scenario = cs.Scenario(country="Italy")
# ita_scenario.register(jhu_data, population_data)
c_scenario.records().tail()

_ = c_scenario.trend()

c_scenario.estimate(cs.SIRF, timeout=120)
c_scenario.clear()
c_scenario.add(days=30)
c_scenario.simulate().tail(7).style.background_gradient(axis=0)

"""### US"""

us_scenario = cs.Scenario(country="United States")
us_scenario.register(jhu_data, population_data)
_ = ita_scenario.trend()
# ita_scenario = cs.Scenario(country="Italy")
# ita_scenario.register(jhu_data, population_data)

us_scenario = cs.Scenario(country="United States")
us_scenario.register(jhu_data, population_data)
_ = us_scenario.trend()
# ita_scenario = cs.Scenario(country="Italy")
# ita_scenario.register(jhu_data, population_data)
us_scenario.records().tail()

_ = us_scenario.trend()

us_scenario.estimate(cs.SIRF, timeout=120)
us_scenario.clear()
us_scenario.add(days=30)
us_scenario.simulate().tail(7).style.background_gradient(axis=0)