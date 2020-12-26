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


def func_co(x, beta, gamma):
    return beta * (x - 0.001) ** (-gamma) * np.exp(-2 * (x - 0.001) ** beta)


def func_nox(x, c1, p1):
    return c1 * x ** p1


def func_hc(x, beta, gamma):
    return beta * (x + 0.05) ** (-gamma) * np.exp(-4 * (x - 0.001) ** beta)


df_coef = pd.DataFrame()


for i, r in df.iterrows():

    df_coef.loc[i, "engine"] = r["name"]

    # process NOx
    x_nox = [0, r["ff_idl"], r["ff_app"], r["ff_co"], r["ff_to"]]
    y_nox = [0, r["ei_nox_idl"], r["ei_nox_app"], r["ei_nox_co"], r["ei_nox_to"]]

    guess = np.array([20, 0.75])
    coef_nox, cov = curve_fit(func_nox, x_nox, y_nox, guess)

    df_coef.loc[i, "nox_c"] = coef_nox[0]
    df_coef.loc[i, "nox_p"] = coef_nox[1]

    # process CO
    x_co = [r["ff_idl"], r["ff_app"], r["ff_co"], r["ff_to"]]
    y_co = [r["ei_co_idl"], r["ei_co_app"], r["ei_co_co"], r["ei_co_to"]]
    y_co = np.maximum(y_co, [1e-7, 1e-7, 1e-7, 1e-7])

    coef_co, covco = curve_fit(func_co, x_co[0:2], y_co[0:2])
    df_coef.loc[i, "co_beta"] = coef_co[0]
    df_coef.loc[i, "co_gamma"] = coef_co[1]
    df_coef.loc[i, "co_max"] = 2 * y_co[0]
    df_coef.loc[i, "co_min"] = (y_co[2] + y_co[3]) / 2

    # process HC
    x_hc = [r["ff_idl"], r["ff_app"], r["ff_co"], r["ff_to"]]
    y_hc = [r["ei_hc_idl"], r["ei_hc_app"], r["ei_hc_co"], r["ei_hc_to"]]

    if max(y_hc) == 0:
        df_coef.loc[i, "hc_na"] = True
    else:
        df_coef.loc[i, "hc_na"] = False

        df_coef.loc[i, "hc_max"] = 2 * max(y_hc[0], y_hc[1])
        df_coef.loc[i, "hc_min"] = (y_hc[2] + y_hc[3]) / 2

        y_hc = np.maximum(y_hc, [1e-7, 1e-7, 1e-7, 1e-7])

        logX, logY = np.log10(x_hc), np.log10(y_hc)  # current powers
        b2 = (logY[3] + logY[2]) / 2  # Average power
        a1 = (logY[1] - logY[0]) / (logX[1] - logX[0])
        b1 = logY[0] - a1 * logX[0]

        x_intersect = 10 ** ((b2 - b1) / a1)
        if x_intersect > x_hc[2]:
            df_coef.loc[i, "hc_ff85"] = x_hc[2]
        else:
            df_coef.loc[i, "hc_ff85"] = 0

        try:
            coef_hc, covhc = curve_fit(func_hc, x_hc, y_hc)
            df_coef.loc[i, "hc_beta"] = coef_hc[0]
            df_coef.loc[i, "hc_gamma"] = coef_hc[1]
            df_coef.loc[i, "hc_a1"] = None
            df_coef.loc[i, "hc_b1"] = None
            df_coef.loc[i, "hc_b2"] = None
        except RuntimeError:
            df_coef.loc[i, "hc_beta"] = None
            df_coef.loc[i, "hc_gamma"] = None
            df_coef.loc[i, "hc_a1"] = a1
            df_coef.loc[i, "hc_b1"] = b1
            df_coef.loc[i, "hc_b2"] = b2


# df_coef.to_csv("db/emission.csv", index=False)

from tabulate import tabulate


def to_fwf(df, fname):
    content = tabulate(
        df.values.tolist(),
        list(df.columns),
        tablefmt="plain",
        numalign="left",
        stralign="left",
    )
    open(fname, "w").write(content)


pd.DataFrame.to_fwf = to_fwf

df_coef.to_fwf("db/emission.txt")
print("Fixed-width engine emission coefficient created: emission.txt")
