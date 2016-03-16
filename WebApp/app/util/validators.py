import sys
sys.path.append("/home/student/CampyDB/CampyDatabase")
from Scripts import cleanCSV as cn
from wtforms.validators import ValidationError
import re

def length(min=-1, max=-1):
	if min!=-1 and max!=-1:
		if min!=max:
			message="Length must be between %d and %d characters long." % (min, max)
		else:
			message="Length must be exactly %d" %(max)
	elif min!=-1 and max==-1:
		message="Length must be greater than or equal to %d" % (min)
	else:
		if min==-1 and max!=-1:
			message="Length must be less than or equal to %d" % (max)

	def _length(form,field):
		l=field.data and len(field.data) or 0
		if l!=0 and (l < min or max != -1 and l > max):
			raise ValidationError(message)

	return _length


def digit():
	message="Value must be a number"

	def _digit(form,field):
		v=field.data
		if not v.isdigit():
			raise ValidationError(message)

	return _digit

def fpBinary():
	message="Value must contain only 1's and 0's"

	def _binary(form,field):
		v=field.data
		if v!="" and re.search("[01]{40}",v) is None:
			raise ValidationError(message)

	return _binary


def date():
    message="Value must be a valid date"

    def _date(form,field):
        v=field.data
        v=cn.convertDate(v,True) if v!="" else v
        if v==-1:
            raise ValidationError(message)
    return _date
		

