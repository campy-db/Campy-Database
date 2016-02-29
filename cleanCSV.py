from dateutil.parser import parse as dateParse
import pandas as pd
import datetime
import re

######################################################################################################
# Converts DDD MM SS format lat and long to signed degree format.
# Note that the lat and longs in the csv are not really in DDD MM SS form as they have the strings
# 'lat'/'long', 'deg', and 'in' in them.
######################################################################################################
def convertGPS(coord):
	newCoord=coord
	# Only convert them if they are'nt already in signed deg form.
	if not isNumber(coord):
		nums=re.split("[A-Za-z]+",coord)
		
		deg=float(nums[1].strip())
		min=float(nums[2].strip())
		sec=float(nums[3].strip())
		
		newCoord=str(deg+(min+sec/60)/60)
	return newCoord

######################################################################################################
# Returns true if s is a number
######################################################################################################
def isNumber(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

######################################################################################################
# Removes characters from non-numberic values that screw things up 
######################################################################################################
def cleanString(s):
	if not isNumber(s) and not pd.isnull(s):
		s=s.strip()
		for c in ";: -.()+#\"<>":
			s=s.replace(c,'_')
		s=re.sub("__+","_",s)
	return s

######################################################################################################
# Some of the years and ids were converted to doubles for some reason
######################################################################################################
def cleanNum(s):
	if s!="" and not pd.isnull(s) and isNumber(s):
		s=str(int(float(s)))
	return s

######################################################################################################
# Converts date to a specified format. We'll be using ISO. 
######################################################################################################
def convertDate(d):
	result=d
	# Sometimes dates are just the year or day.
	try:
		if d!="" and not pd.isnull(d):
			df="%Y-%m-%d"
			dt = dateParse(d)
			result=(dt.strftime(df))
		else:
			result=d
	except ValueError:
		result=d
	return result

######################################################################################################
# Removes a prefix from val of length l
# All prefixes in the csv have an underscore before them. Not all values in a column are prefixed.
######################################################################################################
def remPrefix(val,l):
	if val!="" and not pd.isnull(val) and "_" in val:
		val=val[l:]
	return val
	

###################################################################################################
# Main. Just for testing purposes.
###################################################################################################
def main():
	print cleanString("s   s")


if __name__=="__main__":
	main()