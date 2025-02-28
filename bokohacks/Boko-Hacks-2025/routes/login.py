from flask import Blueprint, render_template, request, flash, redirect, session, url_for
from models.user import User
from extensions import db
from werkzeug.security import check_password_hash  # Ensure password hash is checked securely

login_bp = Blueprint("login", __name__)

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Ensure username and password are provided
        if not username or not password:
            flash("Username and password are required.", "error")
            return redirect(url_for("login.login"))
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):  # Assuming check_password is secure
            session["user"] = user.username
            flash("Login successful!", "success")
            return redirect(url_for("hub.hub"))
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html")

@login_bp.route("/logout")
def logout():
    # Clear session data
    session.pop("user", None)
    session.pop('_flashes', None)  # Clear flash messages as well
    flash("You have been logged out.", "info")
    return redirect(url_for("login.login"))
