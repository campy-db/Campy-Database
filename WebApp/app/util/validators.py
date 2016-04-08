"""
 validators.py
"""
# pylint: disable=W0613

import re
from wtforms.validators import ValidationError, Regexp
from .valid_values import ANIMALS, GEN_ANIMALS, SAMPLE_TYPES, GEN_SAMPLE_TYPES, SPECIES
from ..sparql import queries as q

def specialChars(bad_chars):

    message = "This field cannot contain the characters: {}".format(" ".join(bad_chars))

    def _specialChars(form, field):

        v = field.data

        invalid = any([True if b in v else False for b in bad_chars])

        if invalid:
            raise ValidationError(message)

    return _specialChars

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


def digit(title=None):

    title = title if title else "Value"

    message = "{} must be a number.".format(title)

    regex = "[0-9]+"

    return Regexp(regex=regex, message=message)


def species():

    def _species(form, field):

        v = field.data

        v = re.sub("[Cc]ampy(lobacter)?", "", v).lower()

        good_sep = False\
        if re.search(r"subspec[\. ]|spp(\.)?|sub[- ]spec(ies)?", v) is not None else True

        empty_sub =\
        True if v.find("subspecies") != -1 and v.split("subspecies")[1] == "" else False

        specs = [s.strip() for s in v.split("subspecies")]

        spec = [s.strip() for s in specs[0].split("+")]

        spec = v.split("cf.")[1].strip() if v.find("cf.") != -1 else spec

        spec = [spec] if not isinstance(spec, list) else spec

        print spec

        subspec = specs[1] if len(specs) > 1 else ""

        good_spec = all(True if s in SPECIES.keys() else False for s in spec)

        message = "Did you mean \"subspecies\"?" if not good_sep else ""

        message = "You forgot to add a subspecies" if empty_sub else ""

        if good_spec:
            good_subspec = True if not subspec or subspec in SPECIES["".join(spec)] else False

            if not good_subspec:
                message = "Invalid subspecies"
        else:
            message = "Invalid Species"

        if not (good_sep and good_spec and good_subspec and not empty_sub):
            raise ValidationError(message)

    return _species


def fpBinary():

    message = "Value must contain only 1s and 0s."

    def _binary(form, field):

        v = field.data

        if re.search("[01]{40}", v) is None:

            raise ValidationError(message)

    return _binary


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

def nonemptySource():

    message = "You must specify a source"

    def _nonempty_source(form, field):

        if not form.source.data:
            raise ValidationError(message)

    return _nonempty_source


def genVal(form, v, last):

    o_err = otherErrors(form)

    sub_classes = [s.lower() for s in q.getSubClasses(v)]

    sub_class_list = ", ".join(sub_classes)

    if o_err or v != form.session[last]:

        form.session[last] = v

        raise ValidationError\
        (("warning", "Consider these values instead of {}: {}".format(v, sub_class_list)))


def processGenVal(form, field, gen_list, last):

    val = field.data

    vals = [v.lower().replace("_", " ") for v in val.split(" ")]

    has_gen = False

    for v in vals:

        if v in gen_list:

            gen_val = v

            has_gen = True

    if has_gen:
        genVal(form, gen_val, last)


def genAnimal():

    def _genAnimal(form, field):

        processGenVal(form, field, GEN_ANIMALS, "last_animal")

    return _genAnimal


def genSample():

    def _genSample(form, field):

        processGenVal(form, field, GEN_SAMPLE_TYPES, "last_sample_type")

    return _genSample


def source_():

    def _validSource(form, field):

        val = field.data

        vals = [v.lower().replace("_", " ") for v in val.split(" ")]

        has_animal = any([True if v in ANIMALS else False for v in vals])

        has_sample = None

        if len(vals) > 1:
            has_sample = any([True if v in SAMPLE_TYPES else False for v in vals])

        if not has_animal:

            message = "You must specify an animal"

            raise ValidationError(message)

        if has_sample is not None and has_sample is False:

            message = "Invalid sample type"

            raise ValidationError(message)

    return _validSource

def otherErrors(form):

    result = False

    for name, f in form._fields.iteritems():
        result = True if f.errors else result

    return result
