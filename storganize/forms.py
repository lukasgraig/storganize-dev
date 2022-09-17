from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

class BoxForm(FlaskForm):
    box_title = StringField('title', validators=[DataRequired()])
    box_desc = StringField('desc')
    box_type = StringField('box_type')

class CreateUser(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])