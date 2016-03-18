import sys
sys.path.append("/home/student/CampyDB/CampyDatabase")

from Scripts import cleanCSV as cn
import pandas as pd
from campyTM import campy as ctm

######################################################################################################
#
######################################################################################################
def createDTakenTriples(df,row,isoTitle):

	dateTaken = ""
	triple = ""
	year = df["YEAR"][row]
	month = df["MONTH"][row]
	day = df["DAY"][row]

	if not pd.isnull(day) and cn.isNumber(day):

		day = cn.cleanInt(day)
		triple += ctm.propTriple(isoTitle, {"hasDaySampleTaken":day}, "integer", True)


	if not pd.isnull(month) and cn.isNumber(month):

		month = cn.cleanInt(month)
		triple += ctm.propTriple(isoTitle, {"hasMonthSampleTaken":month}, "integer", True)
	

	if not pd.isnull(year) and cn.isNumber(year):

		year = cn.cleanInt(year)
		triple += ctm.propTriple(isoTitle, {"hasYearSampleTaken":year}, "integer", True)


	return triple