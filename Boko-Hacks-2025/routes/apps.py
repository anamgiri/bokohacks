from flask import Blueprint, render_template, session, jsonify
import re

apps_bp = Blueprint("apps", __name__)

# Define a map of app names to templates
template_map = {
    "notes": "notes.html",
    "upload": "files.html",
    "chat": "chat.html",
    "api": "api.html",
    "admin_login": "admin_login.html",
    "admin_register": "admin_register.html",
    "admin-dashboard": "admin_hub.html",
    "401k": "401k.html",
    "news": "news.html",
}

def get_template_for_app(app_name):
    """Return the template for the given app name"""
    return template_map.get(app_name)

@apps_bp.route("/apps/<app_name>")
def load_app(app_name):
    """Load a template for a specific app"""
    # Special handling for 'admin' app name
    if app_name == "admin":
        return render_template(
            "admin.html",
            is_logged_in=session.get('admin_logged_in', False),
            is_default_admin=session.get('is_default_admin', False)
        )

    # Validate app_name and look up corresponding template
    template_name = get_template_for_app(app_name)
    if template_name:
        return render_template(template_name)

    # Return a generic error page if app not found
    return render_template("error.html", message="Application not found."), 404
