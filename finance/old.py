@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == 'GET':
        return render_template("register.html")
    
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                    username=username)
        if not username:
            return apology("must provide username", 403)
        
        elif len(rows) > 0:
            return apology("username is already taken",403)
        
        elif not password:
            return apology("must provide password", 403)
        
        elif not confirmation:
            return apology("must confirm password", 403)
        
        elif password != confirmation:
            return apology("passwords are not identical", 403)
        else:
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=username, hash=generate_password_hash(password))
            #flash("Registered!", 'success')
            return redirect('/')


@app.route("/login2", methods=["GET", "POST"])
def login2():
    """Log user in"""

    # Forget any user_id
    session.clear()
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

ef sell():
    """Sell shares of stock"""
    form = SellForm()
    rows = db.execute("SELECT * FROM transactions WHERE user_id=:user_id", user_id = session['user_id'])
    symbols = [row['symbol'] for row in rows]
    
    if request.method == 'POST':
        symbol = request.form.get('symbol')
        if not symbol:
            return apology('empty symbol', 403)
        elif symbol not in symbols:
            return apology('symbol not in portfolio', 403)
        
        shares = request.form.get('shares')
        if not shares:
            return apology('empty shares', 403)
        elif isinstance(shares, int):
            return apology('unacceptable input for shares', 403)
        elif int(shares) <= 0:
            return apology('shares must be positive', 403)
        elif int(shares) > sum([row['shares'] for row in rows if row['symbol'] == symbol]):
            return apology('share number exceeded', 403)
        
        [cash] = db.execute("SELECT cash FROM users WHERE id = :user_id",
                          user_id=session['user_id'])
        
        resp = lookup(symbol)
        user_cash = cash.get('cash')
        
        total_price = int(shares) * resp['price']
        
        user_cash += total_price
        
        db.execute("UPDATE users SET cash = :cash WHERE id = :user_id", cash = user_cash, user_id=session['user_id'])
        db.execute("INSERT INTO transactions (symbol, shares, price, user_id) VALUES (:symbol, :shares, :price, :user_id)", 
                   symbol=symbol, shares=-int(shares), price=resp['price'], user_id=session['user_id'])
        return redirect('/')
    else:    
        return render_template('sell.html', symbols=symbols)