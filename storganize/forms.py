from flask_wtf import FlaskForm
from wtforms import StringField, FieldList
from wtforms.validators import DataRequired

class BoxForm(FlaskForm):
    box_title = StringField('title', validators=[DataRequired()])
    box_desc = StringField('desc')
    box_type = StringField('box_type')
