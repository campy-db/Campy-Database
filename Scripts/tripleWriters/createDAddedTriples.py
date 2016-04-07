"""
 createDAddedTriples
"""

import pandas as pd
from .. import cleanCSV as cn
from .campyTM import CAMPY as ctm

def createDAddedTriples(df, row, isoTitle):

    triple = ""
    dateAdded = df["Date Added to Database"][row]

    if not pd.isnull(dateAdded):

        dateAdded = cn.convertDate(dateAdded, False) # Standardize to iso and check date validity

        if dateAdded != -1:

            dates = str(dateAdded).split("-")

            dates = [int(float(d)) for d in dates]

            triple += ctm.propTriple(isoTitle, {"hasDayAdded":dates[2],
                                                "hasMonthAdded":dates[1],
                                                "hasYearAdded":dates[0]}, True, True)

        # else: Invalid date

    return triple
