from flask import Blueprint, render_template, request, flash, redirect, url_for, session , jsonify 
from models.user import User
from extensions import db 
import base64 , time 




register_bp = Blueprint("register", __name__)



from flask import Blueprint, request, jsonify

register_bp = Blueprint("register", __name__)

@register_bp.route("/register/verify-captcha", methods=["POST", "GET"])
def verify_captcha():
    if request.method == "POST":
        # Parse JSON data from the request
        data = request.get_json()
        print (data)

        # Check if data exists and contains "score"
        if not data or "score" not in data:
            return jsonify({"error": "Invalid request"}), 400

        score = data["score"]
        print (score)
        
        if score >= 2:  
            return jsonify({"message": "Captcha verified"}), 200
        else:
            return jsonify({"message": "Captcha failed"}), 400

    return "Captcha route"

@register_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if password meets complexity requirements
        if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char in "!@#$%^&*()-_=+[]{};:'\",.<>?/|\\`~" for char in password):
            flash("Password must be at least 8 characters long, contain at least one number, and one special character.", "error")
            return redirect(url_for("register.register"))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.", "error")
            return redirect(url_for("register.register"))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("login.login"))

    return render_template("register.html")
