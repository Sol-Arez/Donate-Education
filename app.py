
import re
from flask import Flask, redirect, render_template, request, session, flash
from flask_session import Session
from tempfile import mkdtemp
import sqlite3
from helpers import login_required
from werkzeug.security import check_password_hash, generate_password_hash


# configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

#Ensure responses are not cached
@app.after_request
def after_request(response):
    response.headers["Cach-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

#Configure session to use filesystem (instead of cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

conn = sqlite3.connect("donateDB.db", check_same_thread= False)
cur = conn.cursor()


@app.route("/")
@login_required
def index():
        
        cur.execute("SELECT subscriber FROM users WHERE id= ?", (session["user_id"],))
        user = cur.fetchall()

        (reference,) = user[0]
        
        don = vol = app = False

        donations = contributions = applications = []
    
        if reference == "donor":
            don = True
            cur.execute("SELECT * FROM donations WHERE d_id= ?", (session["user_id"],))
            donations = cur.fetchall()

        if reference == "volunteer":
            vol = True
            cur.execute("SELECT * FROM contributions WHERE id= ?", (session["user_id"],))
            contributions = cur.fetchall()

        if reference == "applicant":
            app = True
            cur.execute("SELECT * FROM applications WHERE a_id= ?", (session["user_id"],))
            applications = cur.fetchall()

        return render_template("index.html", don=don, vol=vol, app=app, donations=donations, contributions=contributions, applications=applications)
    
@app.route("/donate", methods=["GET", "POST"])
@login_required
def donate():
    if request.method == "POST":

        # Check for a donor to be allowed for donation
        cur.execute("SELECT subscriber FROM users WHERE id= ?", (session["user_id"],))
        (user,) = cur.fetchall()[0]

        if user == "donor":
            n = request.form.get("name")
            e = request.form.get("email")
            ph = request.form.get("phone")
            device = request.form.get("device")
            man = request.form.get("manufacturer")
            m = request.form.get("model")
            a = request.form.get("age")
            w = request.form.get("yes-no")
    

            cur.execute("INSERT INTO donations (d_id, name, email, phone, device, manufacturer, model, age, wipe) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (session["user_id"], n, e, ph, device, man, m, a, w))
            conn.commit()

            flash("Thank you for your donation!")
            return redirect("/")
        else:

            flash("Sorry but you are not allowed to donate with your account!")
            return redirect("/")

    else:

        return render_template("donate.html")

@app.route("/contribute", methods=["GET", "POST"])
@login_required
def contribute():
    if request.method == "POST":

        # Check for a volunteer to be allowed for contribution
        cur.execute("SELECT subscriber FROM users WHERE id= ?", (session["user_id"],))
        (user,) = cur.fetchall()[0]

        if user == "volunteer":

            n = request.form.get("name")
            e = request.form.get("email")
            ph = request.form.get("phone")
            r = request.form.get("region")
            p = request.form.get("job")
            q = request.form.get("quantity")
            d = request.form.get("period")

            cur.execute("INSERT INTO contributions (id, name, email, phone, region, profession, quantity, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",(session["user_id"], n, e, ph, r, p, q, d))
            conn.commit()

            flash("Welcome to our team!")
            return redirect("/")

        else:

            flash("Sorry but you are not allowed to contribute with your account!")
            return redirect("/")

    else:

        return render_template("contribute.html")


@app.route("/apply", methods=["GET", "POST"])
@login_required
def apply():
    if request.method == "POST":

        # Check for an applicant to be allowed for application
        cur.execute("SELECT subscriber FROM users WHERE id= ?", (session["user_id"],))
        (user,) = cur.fetchall()[0]

        if user == "applicant":

            n = request.form.get("name")
            e = request.form.get("email")
            ph = request.form.get("phone")
            r = request.form.get("region")
            a = request.form.get("age")

            cur.execute("INSERT INTO applications (a_id, name, email, phone, region, age) VALUES (?, ?, ?, ?, ?, ?)", (session["user_id"], n, e, ph, r, a))
            conn.commit()
            flash("Your application is confirmed! We will process your application and contact you soon.")
            return redirect("/")

        else:

            flash("Sorry but you are not allowed to apply with your account!")
            return redirect("/")

    else:

        return render_template("apply.html")


@app.route("/logout")
def logout():
    
    #Forget any user_id
    session.clear()

    #Redirect user to the login form
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():

    #Forget any user_id
    session.clear()

    if request.method == "POST":

        #Check for valid username/password
        user = request.form.get("username")
        cur.execute("SELECT * FROM users WHERE username= ?", (user,))
        row = cur.fetchall()
        
        if len(row) != 1 or not check_password_hash(row[0][2], request.form.get("password")):
            message = "Your username/password is not valid!"
            return render_template("login.html", message=message)

        #Remember which user has loged in
        session["user_id"] = row[0][0]

        return redirect("/")

    else:

        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
              
        # Ensure that the username is not already taken
        cur.execute("SELECT username FROM users")
        reg_users = cur.fetchall()
        
        for i in range(len(reg_users)):
        
            if request.form.get("username") == reg_users[i][0]:
                message = "The username is already taken!"
                return render_template("register.html", message=message)

        #Check for matched passwords
        if request.form.get("password") != request.form.get("confirmation"):
            message = "Your passwords do not match!"
            return render_template("register.html", message=message)

        name = request.form.get("username")
        hpas = generate_password_hash(request.form.get("password"))
        mem = request.form.get("subscriber")
        
        cur.execute("INSERT INTO users (username, hash, subscriber) VALUES (?, ?, ?)", (name, hpas, mem))

        conn.commit()

        flash("You have successfuly registered!")
        return render_template("login.html")

    else:

        return render_template("register.html")

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():

    if request.method == "POST":

        cur.execute("SELECT hash FROM users WHERE id= ?", (session["user_id"],))
        password = cur.fetchall()

        if len(password) != 1 or not check_password_hash(password[0][0], request.form.get("current-password")):
            message = "Your  current password is not valid!"
            return render_template("change_password.html", message=message)

        elif request.form.get("new-password") != request.form.get("repeat-password"):
            message = "Your new passwords do not match!"
            return render_template("change_password.html", message=message)

        else:

            new = generate_password_hash(request.form.get("new-password"))
            cur.execute("UPDATE users SET hash= ? WHERE id= ?", (new, session["user_id"]))
            conn.commit()

            flash("You have successfully changed your password!")
            return redirect("/")

    else:

        return render_template("change_password.html")

