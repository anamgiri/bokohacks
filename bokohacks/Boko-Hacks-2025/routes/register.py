from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models.user import User
from extensions import db
import requests

register_bp = Blueprint("register", __name__)

RECAPTCHA_SECRET_KEY = 'your-recaptcha-secret-key'
RECAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'

def verify_captcha(response_token):
    payload = {
        'secret': RECAPTCHA_SECRET_KEY,
        'response': response_token
    }
    response = requests.post(RECAPTCHA_VERIFY_URL, data=payload)
    return response.json().get('success', False)

@register_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        captcha_response = request.form.get("captcha")
        stored_captcha = session.get("captcha_text")

        # CAPTCHA validation
        if not stored_captcha or captcha_response.upper() != stored_captcha:
            flash("Invalid CAPTCHA. Please try again.", "error")
            return redirect(url_for("register.register"))

        session.pop("captcha_text", None)

        # reCAPTCHA validation (if used)
        if not verify_captcha(captcha_response):
            flash("Invalid CAPTCHA. Please try again.", "error")
            return redirect(url_for("register.register"))

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.", "error")
            return redirect(url_for("register.register"))

        # Create new user
        try:
            new_user = User(username=username)
            new_user.set_password(password)  # Ensure password is hashed
            db.session.add(new_user)
            db.session.commit()

            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("login.login"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred. Please try again.", "error")
            return redirect(url_for("register.register"))

    return render_template("register.html")
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models.user import User
from extensions import db
import requests

register_bp = Blueprint("register", __name__)

RECAPTCHA_SECRET_KEY = 'your-recaptcha-secret-key'
RECAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'

def verify_captcha(response_token):
    payload = {
        'secret': RECAPTCHA_SECRET_KEY,
        'response': response_token
    }
    response = requests.post(RECAPTCHA_VERIFY_URL, data=payload)
    return response.json().get('success', False)

@register_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        captcha_response = request.form.get("captcha")
        stored_captcha = session.get("captcha_text")

        # CAPTCHA validation
        if not stored_captcha or captcha_response.upper() != stored_captcha:
            flash("Invalid CAPTCHA. Please try again.", "error")
            return redirect(url_for("register.register"))

        session.pop("captcha_text", None)

        # reCAPTCHA validation (if used)
        if not verify_captcha(captcha_response):
            flash("Invalid CAPTCHA. Please try again.", "error")
            return redirect(url_for("register.register"))

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.", "error")
            return redirect(url_for("register.register"))

        # Create new user
        try:
            new_user = User(username=username)
            new_user.set_password(password)  # Ensure password is hashed
            db.session.add(new_user)
            db.session.commit()

            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("login.login"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred. Please try again.", "error")
            return redirect(url_for("register.register"))

    return render_template("register.html")
