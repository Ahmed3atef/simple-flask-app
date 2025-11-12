import json
from cs50 import SQL
from flask import Flask, render_template, request, session, redirect, flash, url_for, jsonify
from flask_session import Session


app = Flask(__name__)
db = SQL("sqlite:///storage.db")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/', methods=["GET", "POST"])
def index():
    if "user" not in session:
        session["user"] = []

    data = db.execute("SELECT * FROM users WHERE email = ?",request.form.get("email"))
    if request.method == "POST":
        # if user in the database
        if data:
            # make a session to him and return as get
            session["user"].append(data[0]["id"])
            return redirect("/")
        else:
            # if not so he must register
            return render_template("register.html")
    else :
        # if user use method get to enter the website
        if session.get("user"):
            subscriptions = db.execute(
            """ SELECT
                subscriptions.id,
                users.name,
                sports.sport
                FROM subscriptions
                LEFT JOIN users
                    ON subscriptions.user_id = users.id
                LEFT JOIN sports
                    ON subscriptions.sport_id = sports.id
                WHERE users.id IN (?)
            """, session.get("user", "None"))
            return render_template('index.html', subscriptions=subscriptions, is_logged=True)
        else:
        # if user didn't use same browser to enter the page we create cookies to him and redirect to index.html
            return render_template("index.html", is_logged=False)

@app.route("/leave", methods=["POST"])
def leave():
    if request.form.get("id"):
        db.execute("DELETE FROM subscriptions WHERE id = ?", request.form.get("id"))
        flash('You have left the sport successfully')
        return redirect(url_for("index"))
    else:
        flash('Error: No subscription id provided')
        return redirect(url_for("index"))

@app.route("/join", methods=["GET", "POST"])
def join():
    if request.method == "POST":
        user = db.execute("SELECT id, name FROM users WHERE id = ?", session.get('user'))
        sport = db.execute(
            "SELECT sport FROM sports WHERE id = ?", request.form.get("sport_id"))
        db.execute("INSERT INTO subscriptions (user_id, sport_id) VALUES (?, ?)", user[0]['id'], request.form.get("sport_id"))
        return render_template("subscribe_success.html", name=user[0]['name'], sport=sport[0]['sport'])
    else:
        sports = db.execute("SELECT id, sport FROM sports")
        return render_template("subscribe.html", list_sports = sports)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        db.execute("INSERT INTO users (name, email) VALUES (?, ?)", request.form.get("name"), request.form.get("email"))
        session['user'].append(db.execute("SELECT id FROM users WHERE email = ?", request.form.get("email"))[0]['id'])
        return redirect("/")
    else:
        return render_template("register.html")

@app.route('/api')
def api():
    user_id = session.get('user')
    user_sports = db.execute(
        """SELECT
            u.name,
            s.sport
        FROM subscriptions AS sb
        LEFT JOIN users AS u
            ON sb.user_id = u.id
        LEFT JOIN sports AS s
            ON sb.sport_id = s.id
        WHERE u.id = ?""", user_id)
    return jsonify(user_sports)

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")

