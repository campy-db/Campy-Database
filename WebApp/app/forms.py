"""
 forms.py

 For all the forms we use in the web application. Should be made modular.

"""

import datetime

from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, SelectField
from wtforms.validators import DataRequired, Optional
from .util.validators import\
source_, specialChars, species, length, digit, fpBinary,\
range_, genAnimal, genSample, nonemptySource, isA, postalCode

NOW = datetime.datetime.now()

####################################################################################################
# A form for filtering isolates on the names.html page
####################################################################################################
class FilterIsoForm(Form):
    species = StringField("species", validators=[Optional(), species()])

####################################################################################################
# A form for inputing an isolate name
####################################################################################################
class IsoNameForm(Form):
    iso_title = StringField("iso_title", validators=[DataRequired(), isA("Isolate")])

####################################################################################################
# A form for adding new isolate data
####################################################################################################
class AddForm(Form):

    def __init__(self, ses):
        self.session = ses
        super(AddForm, self).__init__()

    ################################################################################################
    # Overloads the validate_on_submit method defined in flask_wtf/form.py.
    # All general value validators need to go here because they have to check for other errors in
    # the form.
    ################################################################################################
    def validate_on_submit(self):

        result = super(AddForm, self).validate_on_submit()

        other_errors = not result # result is True if there are no errors

        def checkGenVals(addError):

            gen_result = result

            try:
                genAnimal(self, self.source, other_errors)
            except ValueError as e:
                gen_result = False
                if addError:
                    self.source.errors.append(e.args[0])

            try:
                genSample(self, self.source, other_errors)
            except ValueError as e:
                gen_result = False
                if addError:
                    self.source.errors.append(e.args[0])

            return gen_result

        if checkGenVals(False) is False:
            other_errors = True
            result = checkGenVals(True)

        return result

    name = StringField("name", validators=[DataRequired(), specialChars("<>")])

    spec = StringField("spec", validators=[Optional(), species()])

    fp = StringField("fp", validators=\
                          [Optional(), length(min_=40, max_=40), fpBinary()])

    dcy = StringField("dcy", validators=\
                             [Optional(), digit("Year"), range_("Year", 1900, NOW.year)])

    dcm = StringField("dcm", validators=\
                             [Optional(), digit("Month"), range_("Month", 1, 12)])

    dcd = StringField("dcd", validators=\
    	                     [Optional(), digit("Day"), range_("Day", 1, 31)])

    lab = StringField("lab")

    silico = BooleanField("silico")

    source = StringField("source", validators=[Optional(), source_()])

    sourceLocale = SelectField("sourceType",
                               validators=[Optional(), nonemptySource()],
                               choices=[("", ""),
                                        ("abattoir", "Abattoir"),
                                        ("farm", "Farm"),
                                        ("retail", "Retail"),
                                        ("wild", "Wild"),
                                        ("domestic", "Domestic")])

    aID = StringField("aID", validators=[Optional(), nonemptySource()])

    sex = SelectField("sex",
                      validators=[Optional(), nonemptySource()],
                      choices=[("", ""),
                               ("m", "Male"),
                               ("f", "Female")])

    aage = SelectField("aage",
                       validators=[Optional(), nonemptySource()],
                       choices=[("", ""),
                                ("newborn", "Newborn"),
                                ("juvenile", "Juvenile"),
                                ("adult", "Adult")])

    # Needs a travel validator. Should just make a getTravelLoc function
    # that returns country, subnational, city (need this for clean_triple_writers)
    travel = StringField("travel", validators=[Optional(), nonemptySource()])

    hage = StringField("hage", validators=[Optional(),
                                           nonemptySource(),
                                           digit(),
                                           length(min_=1, max_=2)])

    postal_code = StringField("postal_code", validators=[Optional(),
                                                         nonemptySource(),
                                                         postalCode()])

    hsex = SelectField("sex",
                       validators=[Optional(), nonemptySource()],
                       choices=[("", ""),
                                ("m", "Male"),
                                ("f", "Female")])

    pID = StringField("pID", validators=[Optional(), nonemptySource()])



