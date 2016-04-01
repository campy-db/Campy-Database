import sys
sys.path.append("/home/student/CampyDB/CampyDatabase")
sys.path.append("/home/student/CampyDB/CampyDatabase/WebApp/app")

from Scripts import cleanCSV as cn
from wtforms.validators import ValidationError, StopValidation
from validValues import animals, gen_animals, spec_animals, sample_types
from sparql import queries as q
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

            form.session["form_error"] = True

            raise ValidationError(message)

    return _length


def digit():

    message = " Value must be a number. "

    def _digit(form, field):
		
        v = field.data

        if not v.isdigit():

            form.session["form_error"] = True

            raise ValidationError(message)

    return _digit


def fpBinary():

    message = "  Value must contain only 1s and 0s. "

    def _binary(form, field):
		
        v = field.data

        if (re.search("[01]{40}",v) is None):

            form.session["form_error"] = True

            raise ValidationError(message)

    return _binary


def range_(val, min, max):

    message = " {} is out of range. ".format(val)

    def _range_(form, field):

        v = field.data and int(field.data) or ""

        if (v < min or v > max):

            form.session["form_error"] = True

            raise ValidationError(message)

    return _range_


def nonempty_source():

    message = "You must specify a source"

    def _nonempty_source(form, field):

        if not form.source.data:
            raise ValidationError(message)

    return _nonempty_source


def source():

    message = "Not a valid animal"

    def _validSource(form, field):

        def proc_general_animal(v):

            subClasses = [ s.lower() for s in q.getSubClasses(v) ]

            sc_len = len(subClasses)

            subClassList =\
            "{} , or a {}".format( ", ".join(subClasses[:sc_len-1]), subClasses[sc_len-1] )\
            if sc_len > 1 else subClasses[0]

            if form.session["form_error"] or v != form.session["last_animal"]:

                form.session["last_animal"] = v

                form.warning = True

                raise ValidationError( "Do you know if it's a {}?".format(subClassList) )

        val = field.data

        vals = [ v.lower().replace("_", " ") for v in val.split(" ") ]

        has_animal = False

        has_general_animal = False

        has_sample_form = False

        for v in vals:

            has_animal = True if v in animals else has_animal

            has_sample_form

            if v in gen_animals:

                animal = v

                has_general_animal = True

        if has_general_animal:
            proc_general_animal(v)

        if not has_animal:
            raise ValidationError("Invalid source")

    return _validSource

"""
if not valid:

    tries = form.session["tries"]

    if tries < 1:
        form.session["tries"] += 1
        raise ValidationError("Are you sure this is the source?")
"""
	

