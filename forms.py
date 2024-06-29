from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, HiddenField
from wtforms.validators import DataRequired, Email, Length

class SignUpForm(FlaskForm):
  """Form for registering users"""
  
  first_name = StringField('First Name', validators=[DataRequired()])
  last_name = StringField('Last Name', validators=[DataRequired()])
  username = StringField('Username', validators=[DataRequired()])
  email = StringField('Email', validators=[DataRequired(), Email()])
  password = PasswordField('Password', validators=[DataRequired(), Length(min=10)])

class SignInForm(FlaskForm):
  """Form for signing user in"""
  username = StringField('Username', validators=[DataRequired()])
  password = PasswordField('Password', validators=[DataRequired(), Length(min=10)])

class UserEditForm(FlaskForm):
  first_name = StringField('First Name', validators=[DataRequired()])
  last_name = StringField('Last Name', validators=[DataRequired()])
  email = StringField('Email', validators=[DataRequired(), Email()])
  password = PasswordField('Password', validators=[DataRequired(), Length(min=10)])
