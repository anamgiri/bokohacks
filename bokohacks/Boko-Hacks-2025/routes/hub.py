from flask import Blueprint, render_template, session, redirect, url_for, current_app

hub_bp = Blueprint("hub", __name__)

@hub_bp.route("/hub")
def hub():
    try:
        if "user" in session:
            return render_template("hub.html", username=session["user"])
        else:
            current_app.logger.info("User not logged in, redirecting to login page.")
            return redirect(url_for("login.login"))
    except Exception as e:
        # Log the error if any exception occurs
        current_app.logger.error(f"Error accessing hub page: {str(e)}")
        return redirect(url_for("error_page"))  # Redirect to an error page or handle as you see fit
