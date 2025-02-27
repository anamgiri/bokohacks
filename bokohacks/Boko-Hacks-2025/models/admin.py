'''Foreign Key Constraint & Cascade Deletion
 Remove Default Admin Accounts at Initialization
Ensure Proper Indexing for Faster Lookups
 Prevent Boolean-Based Attacks on is_default'''



from extensions import db
from sqlalchemy.orm import validates

class Admin(db.Model):
    __tablename__ = 'admin_credentials'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False, unique=True, index=True)
    is_default = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        """Convert admin object to dictionary securely"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'is_default': self.is_default
        }

    def __repr__(self):
        return f'<Admin {self.id}>'

    @validates('is_default')
    def validate_is_default(self, key, value):
        """Ensure 'is_default' is only True for at most one admin account"""
        if value:
            existing_admin = Admin.query.filter_by(is_default=True).first()
            if existing_admin:
                raise ValueError("Only one admin can have 'is_default' set to True.")
        return value

    @classmethod
    def remove_default_admin(cls):
        """Remove any existing default admin accounts at initialization"""
        default_admins = cls.query.filter_by(is_default=True).all()
        for admin in default_admins:
            db.session.delete(admin)
        db.session.commit()
