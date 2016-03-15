from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired
from util.validators import length
from util.validators import digit
from util.validators import fpBinary


class AddForm(Form):
    name=StringField('name',validators=[DataRequired()])
    fp=StringField('fp',validators=[DataRequired(),length(min=10,max=10),digit(),fpBinary()])





