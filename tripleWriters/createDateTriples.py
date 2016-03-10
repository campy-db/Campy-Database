import pandas as pd
import campyTM as ctm
import cleanCSV as cn

######################################################################################################
#
######################################################################################################
def createDateTriples(df,row,isoTitle):
	dateTaken=""
	isoTriple=""
	year=df["YEAR"][row]
	month=df["MONTH"][row]
	day=df["DAY"][row]

	# Sometimes year is empty, but the other fields aren't
	if not pd.isnull(day) and not pd.isnull(month) and not pd.isnull(year):
		dateTaken=cn.cleanInt(year)+"-"+cn.cleanInt(month)+"-"+cn.cleanInt(day)
	
	if not pd.isnull(year) and pd.isnull(month) and pd.isnull(day):
		dateTaken=cn.cleanInt(year)

	if dateTaken!="":
		isoTriple+=ctm.campy.propTriple(isoTitle,{"hasDateSampleTaken":dateTaken},"string",True)

	return isoTriple