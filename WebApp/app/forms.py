from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, SelectField
from wtforms.validators import DataRequired, Optional
from util.validators import length, digit, fpBinary, range_, source, nonempty_source
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
          [ Optional(), length(title = "year", min = 4, max = 4), digit(), range_("Year", 0, now.year) ])

    dcm = StringField("dcm", validators =\
          [ Optional(), length(title = "month", min = 1, max = 2), digit(), range_("Month", 1, 12) ])

    dcd = StringField("dcd", validators =\
    	  [ Optional(), length(title = "day", min = 1, max = 2), digit(), range_("Day", 1, 31) ])

    lab = StringField("lab")

    silico = BooleanField("silico")

    source = StringField("source", validators = [Optional(), source()])

    sourceLocale = SelectField("sourceType", 
                               validators = [Optional(), nonempty_source()], 
                               choices = [ ("", ""),
                                           ("abattoir", "Abattoir"),
                                           ("farm", "Farm"),
                                           ("retail", "Retail"),
                                           ("wild", "Wild"),
                                           ("domestic", "Domestic") ] )

    aID = StringField("aID", validators = [Optional(), nonempty_source()])

    sex = SelectField("sex", 
                      validators = [Optional(), nonempty_source()], 
                      choices = [ ("", ""), 
    	                          ("m", "Male"), 
    	                          ("f", "Female") ])

    aage = SelectField("aage", 
                       validators = [Optional(), nonempty_source()], 
                       choices = [ ("", ""), 
                                   ("newborn", "Newborn"), 
    	                           ("juvenile", "Juvenile"), 
    	                           ("adult", "Adult") ] )

    


