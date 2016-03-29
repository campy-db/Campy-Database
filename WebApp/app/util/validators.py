import sys
sys.path.append("/home/student/CampyDB/CampyDatabase")
from Scripts import cleanCSV as cn
from wtforms.validators import ValidationError, StopValidation
from validValues import animals, sampleTypes
import re

"""
######################################################################################################
# Continues validation if the number of tries is less than or equal to one, else halts validation.
# So for example if someone tries once to submit a form with a field that has DataRequired() and the
# the field is empty, the DataRequired() error will be raised. But if they try the same thing again,
# the form is considered valid.
######################################################################################################
def warning(msg = None):

	def _warning(form, field):
		if form.tries > 1:
			raise StopValidation()
		else:
			if msg: 
				raise ValidationError(msg)

	return _warning
"""


def length(title = None, min = -1, max = -1):

	if min != -1 and max != -1:

		if min != max:
			message = " Length must be between {} and {} characters long. ".format(min, max)
			message = " Length of {} must be between {} and {} characters long. " \
			          .format(title, min, max) if title else message
		else:
			message = " Length must be exactly {}. ".format(max)
			message = " Length of {} must be exactly {}. " \
			          .format(title, max) if title else message

	elif min != -1 and max == -1:
		message = " Length must be greater than or equal to {}. ".format(min)
		message = " Length of {} must be greater than or equal to {}. " \
		           .format(title, min) if title else message

	else:
		if min == -1 and max != -1:
			message = " Length must be less than or equal to {}. ".format(max)
			message = " Length of {} must be less than or equal to {}. " \
			     	   .format(title, max) if title else message

	def _length(form, field):
		
		l = field.data and len(field.data) or 0
		if (l != 0 and (l < min or max != -1 and l > max)):
			raise ValidationError(message)

	return _length


def digit():

	message = " Value must be a number. "

	def _digit(form, field):
		
		v = field.data
		if not v.isdigit():
			raise ValidationError(message)

	return _digit


def fpBinary():

	message = "  Value must contain only 1's and 0's. "

	def _binary(form, field):
		
		v = field.data
		if (re.search("[01]{40}",v) is None):
			raise ValidationError(message)

	return _binary


def range_(val, min, max):

	message = " {} is out of range. ".format(val)

	def _range_(form, field):
		
		v = field.data and int(field.data) or ""
		if (v < min or v > max):
			raise ValidationError(message)

	return _range_


def source():

    message = "Not a valid animal"

    def _validSource(form, field):

    	val = field.data

        vals = val.split(" ")

        hasAnimal = any(v.replace("_", " ") in animals for v in vals)

        if not hasAnimal:
            raise ValidationError(message)

    return _validSource



"""
if not valid:

    tries = form.session["tries"]

    if tries < 1:
        form.session["tries"] += 1
        raise ValidationError("Are you sure this is the source?")
"""
	

