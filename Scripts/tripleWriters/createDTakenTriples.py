"""
 createDTakenTriples
"""

import pandas as pd
from .. import cleanCSV as cn
from .campyTM import CAMPY as ctm

def createDTakenTriples(df, row, isoTitle):

    triple = ""
    year = df["YEAR"][row]
    month = df["MONTH"][row]
    day = df["DAY"][row]

    if not pd.isnull(day) and cn.isNumber(day):

        day = int(float(day))
        triple += ctm.propTriple(isoTitle, {"hasDaySampleTaken":day}, True, True)


    if not pd.isnull(month) and cn.isNumber(month):

        month = int(float(month))
        triple += ctm.propTriple(isoTitle, {"hasMonthSampleTaken":month}, True, True)

    if not pd.isnull(year) and cn.isNumber(year):

        year = int(float(year))
        triple += ctm.propTriple(isoTitle, {"hasYearSampleTaken":year}, True, True)


    return triple
