"""
 validators.py

 Here we store all validators, or interfaces to shared_validators, that are required for the forms
 we use. Flask validators have kind of a specific format, so that's why we need shared_validators
 in a seperate module and have shared_validator interfaces here. The shared_validators will be
 re-used when we do batch upload.
"""
# pylint: disable=W0613

from wtforms.validators import ValidationError, Regexp
from .valid_values import GEN_ANIMALS, SAMPLE_TYPES, GEN_SAMPLE_TYPES
from ..sparql import queries as q
from .shared_validators import validSpecies, validBinaryFP, validSource, genValue, validPostalCode

####################################################################################################
# Raises an error if the field value does not contain any of the characters in bad_chars.
####################################################################################################
def specialChars(bad_chars):

    message = "This field cannot contain the characters: {}".format(" ".join(bad_chars))

    def _specialChars(form, field):

        v = field.data

        invalid = any([True if b in v else False for b in bad_chars])

        if invalid:
            raise ValidationError(message)

    return _specialChars

####################################################################################################
# Raises an error if the length of the field value is between min and max (exclusive).
####################################################################################################
def length(title=None, min_=-1, max_=-1):

    if min_ != -1 and max_ != -1:

        if min_ != max_:
            message = "Length must be between {} and {} characters long.".format(min_, max_)
            message = "Length of {} must be between {} and {} characters long." \
			          .format(title, min_, max_) if title else message
        else:
            message = "Length must be exactly {}.".format(max_)
            message = "Length of {} must be exactly {}." \
			          .format(title, max_) if title else message

    elif min_ != -1 and max_ == -1:
        message = "Length must be greater than or equal to {}.".format(min_)
        message = "Length of {} must be greater than or equal to {}." \
		           .format(title, min_) if title else message

    else:
        if min_ == -1 and max_ != -1:
            message = "Length must be less than or equal to {}.".format(max_)
            message = "Length of {} must be less than or equal to {}." \
			     	   .format(title, max_) if title else message

    def _length(form, field):

        l = field.data and len(str(field.data)) or 0

        if l != 0 and (l < min_ or max_ != -1 and l > max_):

            raise ValidationError(message)

    return _length


####################################################################################################
# Raises an error if the field value is an integer.
####################################################################################################
def digit(title=None):

    title = title if title else "Value"

    message = "{} must be a number.".format(title)

    regex = "[0-9]+"

    return Regexp(regex=regex, message=message)

####################################################################################################
# Raises an error if the field value is one of the campy species defined in valid_values. See
# validSpecies in shared_validators.
####################################################################################################
def species():

    def _species(form, field):

        v = field.data

        valid, message = validSpecies(v)

        if not valid:
            raise ValidationError(message)

    return _species

####################################################################################################
# Raises an error if the field value contains only 1s and 0s. See validBinary in
# shared_validators.py
####################################################################################################
def fpBinary():

    def _binary(form, field):

        v = field.data

        valid, message = validBinaryFP(v)

        if not valid:
            raise ValidationError(message)

    return _binary

####################################################################################################
# Raises an error if the field value is in between min and max, exclusive
####################################################################################################
def range_(title=None, min_=None, max_=None):

    title = title if title else "Number"

    def _range_(form, field):

        v = field.data or None

        try:
            v = int(v)
        except ValueError:
            v = None

        if v and (min_ is not None and v < min_) or (max_ is not None and v > max_):

            if max_ is None:
                message = "{} must be at least {}.".format(title, min_)
            elif min_ is None:
                message = "{} must be at most {}.".format(title, max_)
            else:
                message = "{} must be between {} and {}.".format(title, min_, max_)

            raise ValidationError(message)

    return _range_

####################################################################################################
# This is called for all the fields that are related to source. It raises an error if the source
# field is empty. So say someone picks abattoir in the locale field and source is empty, an error
# saying you must specicy a source will be raised. That's good.
####################################################################################################
def nonemptySource():

    message = "You must specify a source"

    def _nonempty_source(form, field):

        if not form.source.data:
            raise ValidationError(message)

    return _nonempty_source


def vtest(form, field, other_errors):

    v = field.data

    if v:
        processGeneral(form, v, ["sam", "bill"], "last_test", other_errors)

####################################################################################################
# An interface function for processGeneral. This is for handling general animal input.
####################################################################################################
def genAnimal():

    def _genAnimal(form, field, other_errors):

        v = field.data

        if v:
            processGeneral(form, v, GEN_ANIMALS, "last_animal", other_errors)

    return _genAnimal

####################################################################################################
# Same deal as genAnimal but for handling general sample type input
####################################################################################################
def genSample():

    def _genSample(form, field, other_errors):

        v = field.data

        if v:
            processGeneral(form, v, GEN_SAMPLE_TYPES, "last_sample_type", other_errors)

    return _genSample

####################################################################################################
# Handles vals that are in gen_list. See genValue in shared_validators, most the work is done there.
####################################################################################################
def processGeneral(form, val, gen_list, last_val_key, other_errors):

    last_val = form.session[last_val_key]

    valid, message, gen_val = genValue(val, gen_list, last_val, other_errors)

    if not valid:

        form.session[last_val_key] = gen_val
        raise ValidationError(("warning", message))

####################################################################################################
# Here we do pretty much the same thing as in genAnimal, except for sample types.
####################################################################################################
def isA(class_):

    def _isA(form, field):

        val = field.data

        result = q.isA(val, class_)

        if not result:

            message = "\"{}\" is not an {}".format(val, class_)

            raise ValidationError(message)

    return _isA

####################################################################################################
# Raise an error if the source value is not a valid animal+[sample type], environment, or a valid
# human+[sample type]. (sample type is optional). See valid source in shared_validators.py
####################################################################################################
def source_():

    def _validSource(form, field):

        val = field.data

        valid, message = validSource(val)

        if not valid:
            raise ValidationError(message)

    return _validSource

####################################################################################################
# Raises an error if the field data is not a well formated postal code.
####################################################################################################
def postalCode():

    def _postalCode(form, field):

        val = field.data

        valid, message = validPostalCode(val)

        if not valid:
            raise ValidationError(message)

    return _postalCode

def otherErrors(form):

    result = False

    for name, f in form._fields.iteritems():
        result = True if f.errors else result

    return result
