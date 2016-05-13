"""
 forms.py

 For all the forms we use in the web application. Should be made modular.

"""

import datetime

from flask_wtf import Form
from wtforms import StringField, BooleanField, SelectField, IntegerField, FormField, SubmitField
from wtforms.fields.core import UnboundField
from wtforms.validators import DataRequired, Optional, ValidationError
from app.util.validators import\
source_, specialChars, species, length, digit, fpBinary,\
range_, genAnimal, genSample, nonemptySource, isA, postalCode, micValue, antigenType, seroValue,\
dateTaken, Requires
NOW = datetime.datetime.now()

def validate_mic(drug):
    return StringField(drug, validators=[micValue(), Optional()], description = drug)
    
# class DrugForm(Form):
#     azm = validate_mic("azm")
#     chl = validate_mic("chl")
#     cip = validate_mic("cip")
#     cli = validate_mic("cli")
#     ery = validate_mic("ery")
#     flr = validate_mic("flr")
#     gen = validate_mic("gen")
#     nal = validate_mic("nal")
#     tel = validate_mic("tel")
#     tet = validate_mic("tet")

class DateForm(Form):
    year = StringField('Year', validators=[Optional(), range_("Year", 1900, NOW.year), dateTaken()],\
        description = "yyyy")

    month = StringField('Month', validators=[Optional(), Requires('year'), range_("Month", 1, 12),\
        dateTaken()], description = "mm")

    day = StringField('Day', validators=[Optional(), Requires('year'), Requires('month'),\
        dateTaken(), range_("Day", 1, 31)], description = "dd")

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


    ################################################################################################
    # <<<<<NOTE>>>>> THIS SECTION REQUIRES REFACTORING
    ################################################################################################
    # drugs = ['azm', 'chl', 'cip', 'cli', 'ery', 'flr', 'gen', 'nal', 'tel', 'tet']
    # resistance = {drug:validate_mic(drug) for drug in drugs}

    # drugs = FormField(DrugForm, label="Drug resistance: ")

    azm = validate_mic("azm")
    chl = validate_mic("chl")
    cip = validate_mic("cip")
    cli = validate_mic("cli")
    ery = validate_mic("ery")
    flr = validate_mic("flr")
    gen = validate_mic("gen")
    nal = validate_mic("nal")
    tel = validate_mic("tel")
    tet = validate_mic("tet")
    ################################################################################################

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
    
    serotype = StringField("serotype", validators=[Optional(), seroValue()])
    antigen = StringField("antigen", validators = [Optional(), antigenType()])

    date = FormField(DateForm, label="Date Taken: ")
    outbreakName = StringField("outbreakName", validators=[Optional()])
    outbreakDateLowerBound = FormField(DateForm, label="Outbreak date start: ")
    outbreakDateUpperBound = FormField(DateForm, label="Outbreak date end (optional): ")

    sma1 = StringField("sma1", validators=[Optional()])
