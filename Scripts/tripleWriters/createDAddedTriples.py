import sys
sys.path.append("/home/student/CampyDB/CampyDatabase")

from Scripts import cleanCSV as cn
import pandas as pd
import campyTM as ctm

######################################################################################################
#
######################################################################################################
def createDAddedTriples(df,row,isoTitle):

	triple = ""
	dateAdded = df["Date Added to Database"][row]

	if not pd.isnull(dateAdded):

		dateAdded = cn.convertDate(dateAdded, False) # Standardize to iso and check date validity

		if dateAdded != -1:

			dates = dateAdded.split("-")

			dates = [cn.cleanInt(d) for d in dates]

			triple += ctm.campy.propTriple(isoTitle, {"hasDayAdded":dates[2]}, "int", True) +\
			          ctm.campy.propTriple(isoTitle, {"hasMonthAdded":dates[1]}, "int", True) +\
			          ctm.campy.propTriple(isoTitle, {"hasYearAdded":dates[0]}, "int", True)

		# else: Invalid date

	return triple