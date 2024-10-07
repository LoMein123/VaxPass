import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import display_error, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


g_vaccine_query = "SELECT u.*, n1.firstname AS firstname1, n1.lastname AS lastname1, n2.firstname AS firstname2, n2.lastname AS lastname2 FROM users u LEFT OUTER JOIN nurses n1 ON u.first_dose_admin = n1.username LEFT OUTER JOIN nurses n2 ON u.sec_dose_admin = n2.username WHERE healthcard_id = ?"
GLOBAL_HEALTHID = None

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///vaccine.db")


@app.route("/")
@login_required
def index():
    """Show vaccine history"""

    global g_healthid
    g_healthid = session["user_id"]
    rows = db.execute(g_vaccine_query, g_healthid)

    # Prepare qr code text
    vaccine_qr = "Health Card Id: " + g_healthid + "\n\nName: " + rows[0]["lastname"] + ", " + rows[0]["firstname"] + "\n\n1st dose: "

    if rows[0]["first_dose_name"] != None:
        vaccine_qr = vaccine_qr + rows[0]["first_dose_name"] + " on " + rows[0]["first_dose_date"] + " by " + rows[0]["firstname1"] + " " + rows[0]["lastname1"]
    else:
        vaccine_qr = vaccine_qr + "Not Administrated"

    vaccine_qr = vaccine_qr + "\n\n2nd dose: "

    if rows[0]["sec_dose_name"] != None:
        vaccine_qr = vaccine_qr + rows[0]["sec_dose_name"] + " on " + rows[0]["sec_dose_date"] + " by " + rows[0]["firstname2"] + " " + rows[0]["lastname2"]
    else:
        vaccine_qr = vaccine_qr + "Not Administrated"

    # Pass values into html page
    return render_template("index.html", rows=rows, vaccine_qr=vaccine_qr)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get health card id, name and password from user
        healthid = request.form.get("healthcard_id")
        password = request.form.get("password")

        # Ensure health card ID was submitted
        if not healthid:
            flash("Health Card ID is required!")
            return render_template("login.html")

        # Ensure password was submitted
        if not password:
            flash("Password is required!")
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE healthcard_id = ?", healthid)

        # Ensure health card id exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("invalid username and/or password")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["healthcard_id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/nurselogin", methods=["GET", "POST"])
def nurselogin():
    """Nurse log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get username and password from user
        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username was submitted
        if not username:
            flash("Username is required!")
            return render_template("nurselogin.html")

        # Ensure password was submitted
        if not password:
            flash("Password is required!")
            return render_template("nurselogin.html")

        # Query database for username
        rows = db.execute("SELECT * FROM nurses WHERE username = ?", username)

        # Ensure health card id exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("Invalid Username and/or Password")
            return render_template("nurselogin.html")

        # Remember which user has logged in
        session["username"] = rows[0]["username"]

        # Redirect user to home page
        return redirect("/admin")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("nurselogin.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get health card id, name and password from user
        healthid = request.form.get("healthcard_id")
        password = request.form.get("password")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")

        # Ensure health card ID was submitted
        if not healthid:
            flash("Health Card ID is required!")
            return (render_template("register.html"))

        # Ensure password was submitted
        if not password:
            flash("Password is required!")
            return (render_template("register.html"))

        # Ensure first name was submitted
        if not firstname:
            flash("First Name is required!")
            return (render_template("register.html"))

        # Ensure last name was submitted
        if not lastname:
            flash("Last Name is required!")
            return (render_template("register.html"))

        # Query database for number of registered users
        rows = db.execute("SELECT * FROM users WHERE healthcard_id = ?", healthid)

        # Ensure health card is not duplicate
        if len(rows) != 0:
            flash("Health Card ID already exists!")
            return (render_template("register.html"))

        # Hash password
        pwhash = generate_password_hash(password)

        # Add new user information into database
        dbresult = db.execute("INSERT INTO users (healthcard_id, hash, firstname, lastname) VALUES (?, ?, ?, ?)",
                              healthid, pwhash, firstname, lastname)

        # Remember which user has logged in
        session["user_id"] = healthid

        # Redirect user to home page
        flash(healthid + " Registered!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/registernurse", methods=["GET", "POST"])
def registernurse():
    """Register Nurse"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get health card id, name and password from nurse
        user = request.form.get("username")
        password = request.form.get("password")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")

        # Ensure health card id  was submitted
        if not user:
            flash("First Name is required!")
            return (render_template("registernurse.html"))

        # Ensure password was submitted
        if not password:
            flash("Password is required!")
            return (render_template("register.html"))

        # Ensure password was submitted
        if not firstname:
            flash("First Name is required!")
            return (render_template("register.html"))

        # Ensure username was submitted
        if not lastname:
            flash("Last Name is required!")
            return (render_template("register.html"))

        # Query database for username
        rows = db.execute("SELECT * FROM nurses WHERE username = ?", user)

        # Ensure username exists and password is correct
        if len(rows) != 0:
            flash("Username already exists!")
            return (render_template("register.html"))

        # Hash password
        pwhash = generate_password_hash(password)

        dbresult = db.execute("INSERT INTO nurses (username, hash, firstname, lastname) VALUES (?, ?, ?, ?)",
                              user, pwhash, firstname, lastname)

        # Remember which nurse has logged in
        session["username"] = user

        # Redirect nurse to admin page
        flash("Registered!")
        return render_template("admin.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("registernurse.html")


@app.route("/admin", methods=["GET", "POST"])
def admin():
    """Admin"""

    # Check if user is logged in as nurse
    if session.get("username") is None:
        flash("Please login as nurse")
        return render_template("nurselogin.html")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get usernames and passwords from user
        healthid = request.form.get("healthid")

        # Ensure passwords were submitted
        if not request.form.get("healthid"):
            flash("Health Card Id is Empty")
            return (render_template("admin.html"))

        # Check if health card Id exists
        rows = db.execute("SELECT * FROM users WHERE healthcard_id = ?", healthid)

        if len(rows) == 0:
            flash("Health Card Id does not exists!")
            return (render_template("admin.html"))

        global g_healthid
        g_healthid = healthid

        # Redirect user to home page
        return redirect("/admincentre")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("admin.html")


@app.route("/admincentre", methods=["GET", "POST"])
def admincentre():
    """Administer Vaccine"""

    # Check if user is logged in as nurse
    if session.get("username") is None:
        flash("Please login as nurse")
        return render_template("nurselogin.html")

    global g_healthid

    rows = db.execute(g_vaccine_query, g_healthid)

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        vaccine_type = request.form.get("vaccine_type")

        if vaccine_type == None:
            flash("Must Select Vaccine type")
            return (render_template("admincentre.html", rows=rows))

        nurse_username = session.get("username")

        if rows[0]["first_dose_name"] == None:
            dbresult = db.execute("UPDATE users SET first_dose_name=?, first_dose_admin=?, first_dose_date=datetime('now') WHERE healthcard_id =?",
                                  vaccine_type, nurse_username, g_healthid)

        elif rows[0]["sec_dose_name"] == None:
            dbresult = db.execute("UPDATE users SET sec_dose_name=?, sec_dose_admin=?, sec_dose_date=datetime('now') WHERE healthcard_id =?",
                                  vaccine_type, nurse_username, g_healthid)

        else:
            flash("Cannot apply more than two doses!")
            return (render_template("admincentre.html", rows=rows))

        rows = db.execute(g_vaccine_query, g_healthid)

        return render_template("admincentre.html", rows=rows)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("admincentre.html", rows=rows)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return display_error(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
