from helpers import lookup
from cs50 import SQL
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo, NumberRange

db = SQL("sqlite:///finance.db")

class LoginForm(FlaskForm):
    
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    
class RegisterForm(FlaskForm):
    
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = db.execute("SELECT * FROM users WHERE username = :username",
                          username=username.data)
        if user:
            raise ValidationError('That username is taken. Please choose a different one')
    
class BuyForm(FlaskForm):
    
    symbol = StringField('Symbol', validators=[DataRequired()])
    shares = IntegerField('Shares', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Buy')

    
class SellForm(FlaskForm):
    
    symbol = StringField('Symbol', validators=[DataRequired()])
    shares = IntegerField('Shares', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Sell')

class QuoteForm(FlaskForm):
    
    symbol = StringField('Symbol', validators=[DataRequired()])
    submit = SubmitField('Get Price')
    
    
    
    