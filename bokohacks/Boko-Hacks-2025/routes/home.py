from flask import Blueprint, render_template, current_app

home_bp = Blueprint("home", __name__)

@home_bp.route("/")
def home():
    try:
        return render_template("home.html")
    except Exception as e:
        # Log any potential errors (optional, depending on your logging setup)
        current_app.logger.error(f"Error rendering home page: {str(e)}")
        return render_template("error.html"), 500
