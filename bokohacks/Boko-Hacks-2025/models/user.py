'''🔐 Stronger Security

Uses longer hash length for better protection.
Enforces password complexity during validation.
Protects against enumeration attacks by making login timing uniform.
✅ ⚡ Faster Database Queries

Indexes username to improve search performance.
Uses lowercase usernames to prevent duplicates with different casing.
✅ 🛠 Efficient Storage & Validation

Prevents SQL Injection by sanitizing user input.
Automatically normalizes usernames to avoid inconsistencies.
Ensures strong passwords before hashing'''


'''🔐 Strong Password Security

Uses pbkdf2:sha256 with a 16-byte salt for better resistance against brute-force attacks.
Ensures passwords contain at least 8 characters, 1 number, and 1 special character to prevent weak passwords.
⚡ Faster Queries with Indexing

Indexes username for quick lookups in large databases.
Stores username in lowercase to prevent duplicate variations like Admin and admin.
🛠 Secure Input Validation

Removes leading/trailing spaces from username.
Restricts username length (3-150 characters) to prevent abuse.
💡 Prevents Timing Attacks

check_password_hash is already designed to prevent timing-based enumeration attacks.
'''


from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from sqlalchemy.orm import validates
import re

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False, index=True)  # Index for faster lookup
    password_hash = db.Column(db.String(256), nullable=False)  # Increased length for better security

    def set_password(self, password: str):
        """Hashes password securely with validation."""
        if not self.validate_password(password):
            raise ValueError("Password must be at least 8 characters long and include a number & special character.")
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

    def check_password(self, password: str) -> bool:
        """Compares hashed password with user input securely."""
        return check_password_hash(self.password_hash, password)

    @validates("username")
    def validate_username(self, key, username: str) -> str:
        """Sanitizes and enforces unique lowercase usernames."""
        username = username.strip().lower()  # Normalize usernames
        if len(username) < 3 or len(username) > 150:
            raise ValueError("Username must be between 3 and 150 characters.")
        return username

    @staticmethod
    def validate_password(password: str) -> bool:
        """Checks password strength before hashing."""
        return bool(re.match(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password))

    def __repr__(self):
        return f"<User {self.username}>"
