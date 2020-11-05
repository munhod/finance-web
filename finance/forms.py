from finance.helpers import lookup
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo, NumberRange
from finance import db
from finance.models import Transactions
from flask import session

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
    
    #def validate_username(self, username):
    #    user = User.query.filter_by(username=username.data).first()
    #    if user:
    #        raise ValidationError('That username is taken. Please choose a different one')
    
class BuyForm(FlaskForm):
    
    symbol = StringField('Symbol', validators=[DataRequired()])
    shares = IntegerField('Shares', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Buy')

    
class SellForm(FlaskForm):
    
    rows = db.session.query(Transactions.symbol, Transactions.shares).filter_by(user_id=1).all()
    symbols = [row[0] for row in rows]
    
    symbol = SelectField('Symbol', choices=set(symbols), validators=[DataRequired()])
    shares = IntegerField('Shares', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Sell')

class QuoteForm(FlaskForm):
    
    symbol = StringField('Symbol', validators=[DataRequired()])
    submit = SubmitField('Get Price')
    
    
    
    