"""
 forms.py
"""

import datetime

from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, SelectField
from wtforms.validators import DataRequired, Optional
from .util.validators import\
source_, specialChars, species, length, digit, fpBinary,\
range_, genAnimal, genSample, nonemptySource

NOW = datetime.datetime.now()

class AddForm(Form):

    def __init__(self, ses):
        self.session = ses
        super(AddForm, self).__init__()

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

    source = StringField("source", validators=[Optional(), source_(), genAnimal(), genSample()])

