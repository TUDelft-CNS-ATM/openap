import os
import pandas as pd
import numpy as np
import argparse
from scipy.optimize import curve_fit


def clean_name(name):
    if "SelectOne" in name:
        name = name.split(" ")[0].strip()
    elif "Build Spec" in name:
        name = name.split(" ")[0].strip()
    elif "Block" in name:
        name = name.split(" ")[0].strip()
    elif "series" in name:
        name = name.split(" ")[0].strip()
    elif "(" in name:
        name = name.split("(")[0].strip()
    return name


def clean_bpr(bpr):
    try:
        bpr = float(bpr)
    except:
        bpr = "-"
    return bpr


f = "input/edb-emissions-databank v25a (web).xlsx"

xl = pd.ExcelFile(f)

df0 = xl.parse(sheet_name=2)

df0.dropna(subset=["UID"], inplace=True)

df = df0.iloc[
    1:,
    [
        0,
        1,
        3,
        4,
        5,
        6,
        11,
        12,
        17,
        19,
        22,
        23,
        24,
        25,
        35,
        36,
        37,
        38,
        48,
        49,
        50,
        51,
        80,
        81,
        82,
        83,
        84,
        94,
    ],
]
df.columns = [
    "uid",
    "name",
    "type",
    "bpr",
    "pr",
    "max_thrust",
    "superseded",
    "superseded_by",
    "out_production",
    "out_service",
    "ei_hc_to",
    "ei_hc_co",
    "ei_hc_app",
    "ei_hc_idl",
    "ei_co_to",
    "ei_co_co",
    "ei_co_app",
    "ei_co_idl",
    "ei_nox_to",
    "ei_nox_co",
    "ei_nox_app",
    "ei_nox_idl",
    "ff_to",
    "ff_co",
    "ff_app",
    "ff_idl",
    "fuel_lto",
    "manufacturer",
]

df.dropna(subset=["name"], inplace=True)

df.loc[:, "uid"] = df["uid"].str.strip()
df.loc[:, "name"] = df["name"].str.strip()
df.loc[:, "name"] = df["name"].apply(clean_name)

df.loc[:, "bpr"] = df["bpr"].apply(clean_bpr)

df.loc[:, "max_thrust"] = (df["max_thrust"] * 1000).astype(int)

df = df[df["superseded"] != "x"]
df = df[df["uid"] != ""]
df = df[df["bpr"] != "-"]
df = df[df["ei_hc_to"] != "-"]
df = df[df["ei_hc_co"] != "-"]
df = df[df["ei_hc_app"] != "-"]
df = df[df["ei_hc_idl"] != "-"]
df = df[df["ei_hc_to"] != "*"]
df = df[df["ei_hc_co"] != "*"]
df = df[df["ei_hc_app"] != "*"]
df = df[df["ei_hc_idl"] != "*"]
df = df[df["ei_co_to"] != "-"]
df = df[df["ei_co_co"] != "-"]
df = df[df["ei_co_app"] != "-"]
df = df[df["ei_co_idl"] != "-"]
df = df[df["ei_co_to"] != "*"]
df = df[df["ei_co_co"] != "*"]
df = df[df["ei_co_app"] != "*"]
df = df[df["ei_co_idl"] != "*"]
df = df[df["ei_nox_to"] != "-"]
df = df[df["ei_nox_co"] != "-"]
df = df[df["ei_nox_app"] != "-"]
df = df[df["ei_nox_idl"] != "-"]
df = df[df["ei_nox_to"] != "*"]
df = df[df["ei_nox_co"] != "*"]
df = df[df["ei_nox_app"] != "*"]
df = df[df["ei_nox_idl"] != "*"]
df = df[df["ff_to"] != "-"]
df = df[df["ff_co"] != "-"]
df = df[df["ff_app"] != "-"]
df = df[df["ff_idl"] != "-"]
df = df[df["fuel_lto"] != "-"]

df.drop_duplicates(subset=["name"], keep="last", inplace=True)

# Die supersededs vinden we nu niet meer interessant
df = df.loc[
    :,
    [
        "uid",
        "name",
        "type",
        "bpr",
        "pr",
        "max_thrust",
        "superseded",
        "ei_hc_to",
        "ei_hc_co",
        "ei_hc_app",
        "ei_hc_idl",
        "ei_co_to",
        "ei_co_co",
        "ei_co_app",
        "ei_co_idl",
        "ei_nox_to",
        "ei_nox_co",
        "ei_nox_app",
        "ei_nox_idl",
        "ff_to",
        "ff_co",
        "ff_app",
        "ff_idl",
        "fuel_lto",
        "manufacturer",
    ],
]


def normal_fit(x, beta, gamma):
    return beta * (x - 0.001) ** (-gamma) * np.exp(-2 * (x - 0.001) ** beta)


df_coef_co = pd.DataFrame()


for i, r in df.iterrows():
    X = [r["ff_idl"], r["ff_app"], r["ff_co"], r["ff_to"]]
    Y = [r["ei_co_idl"], r["ei_co_app"], r["ei_co_co"], r["ei_co_to"]]

    if Y[0] == 0:
        Y[0] = 0.0000001
    if Y[1] == 0:
        Y[1] = 0.0000001
    if Y[2] == 0:
        Y[2] = 0.0000001
    if Y[3] == 0:
        Y[3] = 0.0000001

    coef_co, covco = curve_fit(normal_fit, X[0:2], Y[0:2])
    df_coef_co.loc[i, "ene_name"] = r["name"]
    df_coef_co.loc[i, "co_beta"] = coef_co[0]
    df_coef_co.loc[i, "co_gamma"] = coef_co[1]
    df_coef_co.loc[i, "co_Y0"] = Y[0]
    df_coef_co.loc[i, "co_Y1"] = Y[1]
    df_coef_co.loc[i, "co_Y2"] = Y[2]
    df_coef_co.loc[i, "co_Y3"] = Y[3]

df_coef_co.to_csv("db/engine_ei_co.csv", index=False)
