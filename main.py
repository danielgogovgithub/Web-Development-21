import hashlib
import random
import uuid

from flask import Flask, render_template, request, make_response, redirect, url_for
from models import User, db

app = Flask(__name__)
db.create_all()


# Index
@app.route("/", methods=["GET"])
def index():
    session_token = request.cookies.get("session_token")

    if session_token:
        user = db.query(User).filter_by(session_token=session_token).first()
    else:
        user = None

    return render_template("index.html", user=user)
# Index


# Login & Cookie
@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("user-name")
    email = request.form.get("user-email")
    password = request.form.get("user-password")

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    secret_number = random.randint(1, 100)

    user = db.query(User).filter_by(email=email).first()
    if not user:
        user = User(name=name, email=email, secret_number=secret_number, password=hashed_password)
        db.add(user)
        db.commit()

    if hashed_password != user.password:
        return "WRONG PASSWORD! Go back and try again."
    elif hashed_password == user.password:
        session_token = str(uuid.uuid4())
        user.session_token = session_token
        db.add(user)
        db.commit()

        response = make_response(redirect(url_for('index')))
        response.set_cookie("session_token", session_token)
        return response
# Login & Cookie


# Secret Number
@app.route("/result", methods=["POST"])
def result():
    guess = int(request.form.get("guess"))
    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token).first()

    if guess == user.secret_number:
        message = "Correct! The secret number is {0}".format(str(guess))
        new_secret = random.randint(1, 100)
        user.secret_number = new_secret
        db.add(user)
        db.commit()
    elif guess > user.secret_number:
        message = "Your guess is not correct... try something smaller."
    elif guess < user.secret_number:
        message = "Your guess is not correct... try something bigger."

    return render_template("result.html", message=message)
# Secret Number


# Profile
@app.route("/profile", methods=["GET"])
def profile():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token = session_token).first()

    if user:
        return render_template("profile.html", user = user)
    else:
        return redirect(url_for("index"))
# Profile


# Profile Edit
@app.route("/profile/edit", methods=["GET", "POST"])
def profile_edit():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token = session_token).first()

    if request.method == "GET":
        if user:
            return render_template("profile_edit.html", user = user)
        else:
            return redirect(url_for("index"))
    elif request.method == "POST":
        name = request.form.get("profile-name")
        email = request.form.get("profile-email")

        user.name = name
        user.email = email
        db.add(user)
        db.commit()

        return redirect(url_for("profile"))
# Profile Edit


# Profile Delete
@app.route("/profile/delete", methods=["GET", "POST"])
def profile_delete():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token = session_token).first()

    if request.method == "GET":
        if user:
            return render_template("profile_delete.html", user = user)
        else:
            return redirect(url_for("index"))
    elif request.method == "POST":
        db.delete(user)
        db.commit()
        return redirect(url_for("index"))
# Profile Delete


# All Users
@app.route("/users", methods=["GET"])
def all_users():
    users = db.query(User).all()
    return render_template("users.html", users = users)
# All Users


# User Details
@app.route("/user/<user_id>", methods=["GET"])
def user_details(user_id):
    user = db.query(User).get(int(user_id))
    return render_template("user_details.html", user = user)
# User Details


if __name__ == '__main__':
    app.run()
