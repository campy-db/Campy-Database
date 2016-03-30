from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, SelectField
from wtforms.validators import DataRequired, Optional
from util.validators import length, digit, fpBinary, range_, source
import datetime
now = datetime.datetime.now()


class AddForm(Form):

    def __init__(self, ses):
        self.session = ses
        super(AddForm, self).__init__()

    tries = 0

    warning = False

    name = StringField("name", validators = [DataRequired()])

    spec = StringField("spec")

    fp = StringField("fp", validators =\
         [ Optional(), length(min = 40, max = 40), fpBinary() ])

    dcy = StringField("dcy", validators =\
          [ Optional(), length(title = "year", min = 4, max = 4), digit(), range_("Year", 0, now.year)])

    dcm = StringField("dcm", validators =\
          [ Optional(), length(title = "month", min = 1, max = 2), digit(), range_("Month", 1, 12)])

    dcd = StringField("dcd", validators =\
    	  [ Optional(), length(title = "day", min = 1, max = 2), digit(), range_("Day", 1, 31)])

    lab = StringField("lab")

    silico = BooleanField("silico")

    source = StringField("source", validators = [ Optional(), source() ])

    sourceType = SelectField("sourceType", choices = [ ("", ""),
                                                       ("Abattoir_type", "Abattoir"),
                                                       ("Farm_type", "Farm"),
                                                       ("Retail_type", "Retail"),
                                                       ("Wild_type", "Wild") ] )

    aID = StringField("aID")

    sex = SelectField("sex", choices = [ ("", ""), 
    	                                 ("m", "Male"), 
    	                                 ("f", "Female") ])
    domestic = BooleanField("domestic")

    aage = SelectField("aage", choices = [ ("", ""), 
    	                                   ("newborn", "Newborn"), 
    	                                   ("juvenile", "Juvenile"), 
    	                                   ("adult", "Adult") ] )

    


