'''Session Management:

Problem: You're storing user accounts in a dictionary (user_accounts) that is in-memory. This works for simple cases but will be lost when the server restarts, and it won't persist across multiple instances in a production environment.
Fix: Use a database or an external persistent storage system to store user accounts. If you plan on using this system long-term, integrating with SQLAlchemy would be more robust.
For example, you could modify the User model to include a 401k balance, and store the data in the database instead of the dictionary.

Sensitive Data in Sessions:

Problem: Storing the user’s username in the session is fine, but ensure sensitive data like password is never stored in the session. If you’re storing other user information (like 401k balance or funds), it would be safer to query this from the database rather than storing it directly in the session.
Fix: Continue storing minimal data (like username) in the session, but use database queries to retrieve sensitive financial information when needed.
Security:

Problem: There's no authentication or authorization checks to ensure users can't access or manipulate other users' accounts (e.g., modifying someone else’s 401k balance).
Fix: Ensure that user actions (like contributions or resets) are restricted to their own accounts, which seems to be in place already by the session check, but keep this in mind if you store the accounts in the database.
Error Handling:

Problem: While the API provides messages for invalid input and errors, some edge cases or potential issues (e.g., server errors or database failures) aren't fully handled.
Fix: Add more specific error messages for common failure scenarios and ensure transactions are atomic in case you decide to persist data in a database.
Performance:

Problem: time.sleep(2) is used in the /contribute route, which could slow down the system unnecessarily. While it's likely for simulation purposes, avoid using time.sleep in production code, as it blocks the thread and reduces throughput.
Fix: Remove or replace time.sleep with asynchronous handling if necessary.
Refactoring for Database: Since you are using Flask and SQLAlchemy, it would be better to integrate with a database to manage users and their 401k information. Here's how you could do it.

'''



from flask import Blueprint, render_template, jsonify, request, session
from extensions import db
from models.user import User
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

retirement_bp = Blueprint("retirement", __name__, url_prefix="/apps/401k")

@retirement_bp.route("/")
def retirement_dashboard():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
    return render_template("401k.html", username=session["user"])

@retirement_bp.route("/balance")
def get_balance():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
        
    username = session["user"]
    user = User.query.filter_by(username=username).first()

    if not user:
        # Initialize the user in the database if not found
        user = User(username=username, funds=10000, balance_401k=0)
        db.session.add(user)
        db.session.commit()

    return jsonify({"funds": user.funds, "401k_balance": user.balance_401k})

@retirement_bp.route("/contribute", methods=["POST"])
def contribute():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
        
    data = request.get_json()
    amount = data.get("amount", 0)
    
    username = session["user"]
    user = User.query.filter_by(username=username).first()

    if not user:
        # Initialize the user in the database if not found
        user = User(username=username, funds=10000, balance_401k=0)
        db.session.add(user)
        db.session.commit()
    
    if amount <= 0:
        return jsonify({
            "message": "Invalid contribution amount!", 
            "funds": user.funds,
            "401k_balance": user.balance_401k
        }), 400
    
    if amount > user.funds:
        return jsonify({
            "message": "Insufficient personal funds for this contribution!", 
            "funds": user.funds,
            "401k_balance": user.balance_401k
        }), 400

    # Perform the contribution
    company_match = amount * 0.5
    total_contribution = amount + company_match

    user.funds -= amount  # Deduct funds
    user.balance_401k += total_contribution  # Add to 401k balance

    try:
        db.session.commit()
        return jsonify({
            "message": f"Contributed ${amount}. Employer matched ${company_match}!",
            "funds": user.funds,
            "401k_balance": user.balance_401k
        })
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Failed to process contribution. Please try again."}), 500

@retirement_bp.route("/reset", methods=["POST"])
def reset_account():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
        
    username = session["user"]
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({
            "message": "Account not found!", 
            "funds": 0,
            "401k_balance": 0
        }), 404

    user.funds = 10000
    user.balance_401k = 0
    
    try:
        db.session.commit()
        return jsonify({
            "message": "Account reset successfully!",
            "funds": user.funds,
            "401k_balance": user.balance_401k
        })
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Failed to reset account. Please try again."}), 500
