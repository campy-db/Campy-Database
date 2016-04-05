from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, Optional
from util.validators import specialChars, length, digit, fpBinary, range_, source, genAnimal, genSample, nonemptySource
import datetime
now = datetime.datetime.now()

class AddForm(Form):

    def __init__(self, ses):
        self.session = ses
        super(AddForm, self).__init__()

    name = StringField("name", validators = [DataRequired() , specialChars()])

    spec = StringField("spec")

    fp = StringField("fp", validators =\
         [ Optional(), length(min = 40, max = 40), fpBinary() ])

    dcy = StringField("dcy", validators =\
          [ Optional(), digit("Year"), range_("Year", 1900, now.year) ])

    dcm = StringField("dcm", validators =\
          [ Optional(), digit("Month"), range_("Month", 1, 12) ])

    dcd = StringField("dcd", validators =\
    	  [ Optional(), digit("Day"), range_("Day", 1, 31) ])

    lab = StringField("lab")

    silico = BooleanField("silico")

    sourceLocale = SelectField("sourceType", 
                               validators = [Optional(), nonemptySource()], 
                               choices = [ ("", ""),
                                           ("abattoir", "Abattoir"),
                                           ("farm", "Farm"),
                                           ("retail", "Retail"),
                                           ("wild", "Wild"),
                                           ("domestic", "Domestic") ] )

    aID = StringField("aID", validators = [Optional(), nonemptySource()])

    sex = SelectField("sex", 
                      validators = [Optional(), nonemptySource()], 
                      choices = [ ("", ""), 
    	                          ("m", "Male"), 
    	                          ("f", "Female") ])

    aage = SelectField("aage", 
                       validators = [Optional(), nonemptySource()], 
                       choices = [ ("", ""), 
                                   ("newborn", "Newborn"), 
                                   ("juvenile", "Juvenile"), 
                                   ("adult", "Adult") ] )

    source = StringField("source", validators = [Optional(), source(), genAnimal(), genSample()])

