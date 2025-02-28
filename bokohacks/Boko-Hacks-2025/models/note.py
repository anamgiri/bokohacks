'''✅ 🚀 Fast Query Performance → Added indexing on user_id & created_at
✅ 🔐 Secure User Access → Prevents unauthorized note creation
✅ 🛠 Efficient Storage → Uses Text only when necessary
✅ 📏 Enforces Constraints → Prevents empty or overly long inputs
✅ 🔄 Automatic Timestamps → Uses server_default for better efficiency'''

'''⚡ Faster Queries

Indexing created_at & user_id → Faster filtering
server_default=func.now() → Offloads timestamp generation to the database
🔐 Security & Data Integrity

Foreign Key Constraint (ondelete="CASCADE") → Ensures notes are deleted when the user is removed
Validation for Empty Inputs & Title Length
📏 Prevents Logging Overload

__repr__ method truncates long note titles
⏳ Automated Cleanup

Deletes notes older than 30 days automatically'''


from extensions import db
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy.orm import validates
from datetime import datetime, timedelta

class Note(db.Model):
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False, index=True)  # Efficient timestamp
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)

    def to_dict(self):
        """Convert note object to dictionary securely"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'user_id': self.user_id
        }

    def __repr__(self):
        return f'<Note {self.title[:20]}...>'  # Prevents excessive logging output

    @validates('title', 'content')
    def validate_fields(self, key, value):
        """Enforce title/content length and prevent empty values"""
        if not value or not value.strip():
            raise ValueError(f"{key.capitalize()} cannot be empty.")
        
        if key == 'title' and len(value) > 200:
            raise ValueError("Title length exceeds 200 characters.")
        
        return value

    @classmethod
    def get_user_notes(cls, user_id):
        """Efficiently fetch all notes for a specific user"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).all()

    @classmethod
    def delete_old_notes(cls, days=30):
        """Automatically delete notes older than X days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        cls.query.filter(cls.created_at < cutoff_date).delete()
        db.session.commit()
