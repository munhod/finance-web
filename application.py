import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd
from forms import LoginForm, RegisterForm, BuyForm, SellForm, QuoteForm

os.environ['API_KEY'] = 'pk_92ef5cd5464140d0afeea62ccfeb90bc'

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SECRET_KEY"] = 'abcd'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///finance.db"

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    rows = db.execute("SELECT symbol, SUM(shares) FROM transactions WHERE user_id = :user_id GROUP BY symbol HAVING SUM(shares) != 0;", user_id=session['user_id'])
    symbols = [row['symbol'] for row in rows]
    prices = {symbol: lookup(symbol)['price'] for symbol in symbols}
    prices['cash'] = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session['user_id'])[0]['cash']
    prices['total'] = sum([row['SUM(shares)'] * prices[row['symbol']] for row in rows])
    
    return render_template('index.html', rows=rows, prices=prices)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    form = BuyForm()
    
    if form.validate_on_submit():
        resp = lookup(form.symbol.data)
        [cash] = db.execute("SELECT cash FROM users WHERE id = :user_id",
                        user_id=session['user_id'])
        
        user_cash = cash.get('cash')
        total_price = int(form.shares.data) * resp['price']
        
        if  user_cash < total_price:
            return apology("not enough cash to complete the transaction")
        
        flash('BOUGHT!', 'success')
        user_cash -= total_price
        db.execute("UPDATE users SET cash = :cash WHERE id = :user_id", cash = user_cash, user_id=session['user_id'])
        db.execute("INSERT INTO transactions (symbol, shares, price, user_id) VALUES (:symbol, :shares, :price, :user_id)", 
                symbol=form.symbol.data, shares=int(form.shares.data), price=resp['price'], user_id=session['user_id'])

        return redirect('/')
    return render_template('buy.html', form=form)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    history = db.execute("SELECT * FROM transactions WHERE user_id = :user_id ORDER BY date DESC", user_id=session['user_id'])
    return render_template('history.html', history=history)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=form.username.data)
        
        # Ensure username exists and password is correct
        if len(rows) == 1 and check_password_hash(rows[0]["hash"], form.password.data):
            # Remember which user has logged in
            session["user_id"] = rows[0]["id"]
            
            flash('LOGGED IN!', 'success')
            # Redirect user to home page
            return redirect("/")
        else:
            flash('Login unsuccessful. Please check username and password', 'danger')
        
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    form = QuoteForm()
    if form.validate_on_submit():
        resp = lookup(form.symbol.data)
        return render_template('quoted.html', resp=resp)
   
    return render_template('quote.html', form=form)
    
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    form = RegisterForm()
    
    if form.validate_on_submit():
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=form.username.data,
                    hash=generate_password_hash(form.password.data))
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    
    return render_template("register.html", form=form)


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    form = SellForm()
    rows = db.execute("SELECT * FROM transactions WHERE user_id=:user_id", user_id = session['user_id'])
    symbols = [row['symbol'] for row in rows]
    
    if form.validate_on_submit():
    
        if form.symbol.data not in symbols:
            return apology('symbol not in portfolio', 403)
        
        elif int(form.shares.data) > sum([row['shares'] for row in rows if row['symbol'] == form.symbol.data]):
            return apology('share number exceeded', 403)
        
        [cash] = db.execute("SELECT cash FROM users WHERE id = :user_id",
                          user_id=session['user_id'])
        
        resp = lookup(form.symbol.data)
        user_cash = cash.get('cash')
        
        total_price = int(form.shares.data) * resp['price']
        
        user_cash += total_price

        db.execute("UPDATE users SET cash = :cash WHERE id = :user_id", cash = user_cash, user_id=session['user_id'])
        db.execute("INSERT INTO transactions (symbol, shares, price, user_id) VALUES (:symbol, :shares, :price, :user_id)", 
                   symbol=form.symbol.data, shares=-int(form.shares.data), price=resp['price'], user_id=session['user_id'])
        flash('SOLD!', 'success')
        
        return redirect('/')
    else:    
        return render_template('sell.html', symbols=symbols, form=form)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
