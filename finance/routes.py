from flask import flash, jsonify, redirect, render_template, request, session, url_for, flash
from finance.models import User, Transactions
from finance import app, db
from finance.helpers import apology, login_required, lookup
from finance.forms import LoginForm, RegisterForm, BuyForm, SellForm, QuoteForm
from werkzeug.security import check_password_hash, generate_password_hash

@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    rows = db.session.query(Transactions.symbol,db.func.sum(Transactions.shares)).filter_by(user_id=session['user_id']).group_by(Transactions.symbol).having(db.func.sum(Transactions.shares)!=0).all()

    symbols = [row[0] for row in rows]
    prices = {symbol: lookup(symbol)['price'] for symbol in symbols}
    prices['cash'] = User.query.filter_by(id=session['user_id']).first().cash
    prices['total'] = sum([row[1] * prices[row[0]] for row in rows])
    
    return render_template('index.html', rows=rows, prices=prices)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    form = BuyForm()
    
    if form.validate_on_submit():
        resp = lookup(form.symbol.data)
        user = User.query.filter_by(id=session['user_id']).first()
        
        total_price = int(form.shares.data) * resp['price']
        
        if  user.cash < total_price:
            return apology("not enough cash to complete the transaction")
        
        user.cash -= total_price
        transaction = Transactions(symbol=form.symbol.data, shares=form.shares.data, price=resp['price'], user_id = user.id)
        db.session.add(transaction)
        db.session.commit()
        flash('BOUGHT!', 'success')
        return redirect('/')
    return render_template('buy.html', form=form)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    history = Transactions.query.filter_by(user_id=session['user_id']).all()
    
    return render_template('history.html', history=history)

@app.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.hash, form.password.data):
            # Remember which user has logged in
            session["user_id"] = user.id
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
        user = User(username=form.username.data, hash=generate_password_hash(form.password.data))
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    
    return render_template("register.html", form=form)


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    form = SellForm()
    rows = db.session.query(Transactions.symbol, Transactions.shares).filter_by(user_id=session['user_id']).all()
    symbols = [row[0] for row in rows]
    
    if form.validate_on_submit():
    
        if form.symbol.data not in symbols:
            return apology('symbol not in portfolio', 403)
        
        elif int(form.shares.data) > sum([row[1] for row in rows if row[0] == form.symbol.data]):
            return apology('share number exceeded', 403)
        
        user = User.query.filter_by(id=session['user_id']).first()
        
        resp = lookup(form.symbol.data)
        
        total_price = int(form.shares.data) * resp['price']
        
        user.cash += total_price
        transaction = Transactions(symbol=form.symbol.data, shares=-form.shares.data, price=resp['price'], user_id = user.id)
        
        db.session.add(transaction)
        db.session.commit()
        
        flash('SOLD!', 'success')
        
        return redirect('/')
    else:    
        return render_template('sell.html', symbols=symbols, form=form)