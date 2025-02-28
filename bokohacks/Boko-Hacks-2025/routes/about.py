
from flask import Blueprint, render_template, make_response, current_app
from datetime import datetime

about_bp = Blueprint("about", __name__)

@about_bp.route("/about")
def about():
    # Render the template
    response = render_template("about.html")

    # Apply security headers
    response = make_response(response)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"  # Prevents clickjacking
    response.headers["X-XSS-Protection"] = "1; mode=block"  # Prevents reflected XSS
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"  # Enforces HTTPS

    # Optionally, you could cache the template if it's not dynamic
    response.cache_control.max_age = 3600  # Cache for 1 hour

    # Log the access (using current_app.logger)
    current_app.logger.info(f"About page accessed at {datetime.utcnow()}")

    return response
