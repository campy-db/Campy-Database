# -*- coding: latin-1 -*-
"""
 cleanCSV.py

 For cleaning csvs, checking if csv values are what they should be.
"""

import re
from collections import defaultdict
import pandas as pd
from dateutil.parser import parse as dateParse

####################################################################################################
# Really shouldn't be here but we need it and I donno where to put it right now. Oh well, I'll do it
# later.
# Returns true if a value in vals is the same as one or more of the other values in vals.
# Standardizes all values in vals and puts them in a dictionary. If the dictionary entry for a value
# is greater than 1, return true.
#
# vals - A list of values to be compared
####################################################################################################
def compare(vals):

    d = defaultdict(int) # the value for a given key is set to 0 when it is inserted. How nice

    # clean all the values first. Otherwise A-B is not the same as
    # A_b (for out purposes they are the same)
    vals = [cleanString(v).lower() for v in vals if not pd.isnull(v)]

    # Add it to the dict and increase its value
    for val in vals:
        d[val] += 1

    return any(True if d[val] > 1 else False for val in vals)

####################################################################################################
# Returns True if the value given, v, doesn't equal one of the bad words, ie words that don't
# mean unknown or n/a. False otherwise.
####################################################################################################
def isGoodVal(v):

    bad_words =\
    ("", "none", "-", "unknown", "n/a", "n\\a", "#n/a",\
     "#n\\a", "missing", "not given", "other", "na")

    v = v.strip().lower() if not isNumber(v) else v

    return v not in bad_words

####################################################################################################
# Converts DDD MM SS format lat and long to signed degree format.
# Note that the lat and longs in the csv are not really in DDD MM SS form as they have the strings
# 'lat'/'long', 'deg', and 'in' in them.
####################################################################################################
def convertGPS(coord):

    coord = coord.strip()

    # Only convert them if they are'nt already in signed deg form.
    if not isNumber(coord):

        nums = re.split(r"[A-Za-z]+", coord)

        deg = float(nums[1].strip())
        min_ = float(nums[2].strip())
        sec = float(nums[3].strip())

        coord = (deg+(min_+sec/60)/60)
    return coord

####################################################################################################
# Returns true if s is a number, eg hex, int, double etc
####################################################################################################
def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

####################################################################################################
# Removes characters that screw things up when the string is being used as a URI
####################################################################################################
def cleanString(s):

    if not isNumber(s) and not pd.isnull(s):

        s = s.strip()

        # For numbers, sometimes we get the value <30. This becomes the same as 30 if we replace the
        # <, similarily >, (both are illegal uri characters) with _. This is no good as we end
        # up with tag_30 hasLiteralValue 30 and hasLiteralValue <30. So we replace < with
        # 'l' and > with 'g'. So now we end up with tag_30 hasLiteralvalue 30 and tag_g30 hasLiteral
        # Value >30.

        # Replaces '>' with 'g' if '>' is followed by a digit, or ' = '
        s = re.sub(r">(?=(\d|=\d))", "g", s)
        re.sub(r"<(?=(\d|=\d))", "l", s) # and ' = ' is followed by a digit

        for c in r"{;}: .,-()\/#\"<>":
            s = s.replace(c, '_')

        s = re.sub("__+", "_", s) # Change 2 or more consecutive underscores into one underscore
        s = s[:len(s)-1] if s[len(s)-1] == "_" else s # Get rid of trailing underscores
        s = s[1:] if s[0] == "_" and len(s) > 1 else s # Also get rid of leading underscores

    return s

####################################################################################################
# Removes characters from strings that are to be used as names in an ontology
####################################################################################################
def cleanName(s):

    if not isNumber(s) and not pd.isnull(s):
        for c in "}{\"":
            s = s.replace(c, "")
        s = s.strip()
    return s

####################################################################################################
# Some of the years and ids were converted to doubles for some reason
####################################################################################################
def cleanInt(s):

    if not pd.isnull(s) and isNumber(s):
        s = str(int(float(s)))

    return s

####################################################################################################
# Converts date d to a specified format. We'll be using ISO. df is True if the format has the day
# first, eg 14/01/1993. But some are month first, eg 4/18/2015. This is the default.
####################################################################################################
def convertDate(d, df):
    result = -1
    # Sometimes dates are just the year or day.
    try:
        if d != "" and not pd.isnull(d):

            df = "%Y-%m-%d"
            dt = dateParse(d, dayfirst=df)
            result = (dt.strftime(df))

        else:
            result = d

    except ValueError:
        result = -1

    return result

####################################################################################################
# Removes a prefix from val of length l
# All prefixes in the csv have an underscore before them. Not all values in a column are prefixed.
####################################################################################################
def remPrefix(val, l):
    if val != "" and not pd.isnull(val) and "_" in val:
        val = val[l:]
    return val


####################################################################################################
# cleanGene
####################################################################################################
def cleanGene(g):

    g = g.replace("Oxford", "")
    g = g.replace("MOMP peptide", "MOMP")
    g = g.replace("fla peptide", "flaPeptide")
    g = g.strip()

    return g

####################################################################################################
# Main. Just for testing purposes.
####################################################################################################
def main():
    print cleanName("{sam")

if __name__ == "__main__":
    main()
