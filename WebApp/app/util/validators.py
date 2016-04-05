import sys
sys.path.append("/home/student/CampyDB/CampyDatabase")
sys.path.append("/home/student/CampyDB/CampyDatabase/WebApp/app")

from wtforms.validators import ValidationError, StopValidation, Regexp, NumberRange
from valid_values import animals, gen_animals, sample_types, gen_sample_types
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

def specialChars():

    bad_chars = "<>"

    message = "This field cannot contain the characters: {}".format(" ".join(bad_chars))

    def _specialChars(form, field):

        v = field.data

        invalid = any([ True if b in v else False for b in bad_chars ])

        if invalid:
            raise ValidationError(message)

    return _specialChars

def length(title = None, min = -1, max = -1):

    if min != -1 and max != -1:

        if min != max:
            message = "Length must be between {} and {} characters long.".format(min, max)
            message = "Length of {} must be between {} and {} characters long." \
			          .format(title, min, max) if title else message
        else:
            message = "Length must be exactly {}.".format(max)
            message = "Length of {} must be exactly {}." \
			          .format(title, max) if title else message

    elif min != -1 and max == -1:
        message = "Length must be greater than or equal to {}.".format(min)
        message = "Length of {} must be greater than or equal to {}." \
		           .format(title, min) if title else message

    else:
        if min == -1 and max != -1:
            message = "Length must be less than or equal to {}.".format(max)
            message = "Length of {} must be less than or equal to {}." \
			     	   .format(title, max) if title else message

    def _length(form, field):
		
        l = field.data and len(str(field.data)) or 0

        if (l != 0 and (l < min or max != -1 and l > max)):

            raise ValidationError(message)

    return _length


def digit(title = None):

    title = title if title else "Value"

    message = "{} must be a number.".format(title)

    regex = "[0-9]+"

    return Regexp(regex = regex, message = message)


def fpBinary():

    message = "Value must contain only 1s and 0s."

    def _binary(form, field):
		
        v = field.data

        if (re.search("[01]{40}",v) is None):

            raise ValidationError(message)

    return _binary


def range_(title = None, min = None, max = None):

    title = title if title else "Number"

    def _range_(form, field):

        v = field.data or None

        try:
            v = int(v)
        except ValueError: 
            v = None

        if v and (min is not None and v < min) or (max is not None and v > max):

            if max is None:
                message = "{} must be at least {}.".format(title, min)
            elif min is None:
                message = "{} must be at most {}.".format(title, max)
            else:
                message = "{} must be between {} and {}.".format(title, min, max)

            raise ValidationError(message)

    return _range_

def nonemptySource():

    message = "You must specify a source"

    def _nonempty_source(form, field):

        if not form.source.data:
            raise ValidationError(message)

    return _nonempty_source


def genVal(form, v, last):

    o_err = otherErrors(form)

    sub_classes = [ s.lower() for s in q.getSubClasses(v) ]

    sc_len = len(sub_classes)

    sub_class_list = ", ".join(sub_classes)

    if o_err or v != form.session[last]:

        form.session[last] = v

        raise ValidationError\
        ( ("warning", "Consider these values instead of {}: {}".format(v, sub_class_list)) )


def processGenVal(form, field, gen_list, last):

    val = field.data

    vals = [ v.lower().replace("_", " ") for v in val.split(" ") ]

    has_gen = False

    for v in vals:

        if v in gen_list:

            gen_val = v

            has_gen = True

    if has_gen:
        genVal(form, gen_val, last)


def genAnimal():

    def _genAnimal(form, field):

        processGenVal(form, field, gen_animals, "last_animal")

    return _genAnimal


def genSample():

    def _genSample(form, field):

        processGenVal(form, field, gen_sample_types, "last_sample_type")

    return _genSample


def source():

    message = "Must specify an animal"

    def _validSource(form, field):

        val = field.data

        vals = [ v.lower().replace("_", " ") for v in val.split(" ") ]

        has_animal = any([ True if v in animals else False for v in vals ])

        has_sample = None

        if len(vals) > 1:
            has_sample = any([ True if v in sample_types else False for v in vals ])

        if not has_animal:

            message = "You must specify an animal"

            raise ValidationError(message)

        if has_sample is not None and has_sample == False:

            message = "Invalid sample type"

            raise ValidationError(message)

    return _validSource

def otherErrors(form):

    result = False

    for name, f in form._fields.items():
        result = True if f.errors else result

    return result

	

