'''Prevent Path Traversal & Malicious File Names
 Enforce File Type Restrictions
 Store Only Secure File Paths
 Ensure Proper Foreign Key Constraints & Cascade Deletion
 Index User ID for Faster Lookups'''



'''Fixes
🚀 Prevent Path Traversal & Injection Attacks

Uses secure_filename() to prevent malicious file names like ../../etc/passwd.
🔐 Restrict File Uploads to Specific Types

is_allowed_file() ensures only safe file types can be uploaded.
⚡ Prevent Overwriting Files

If a file with the same name exists, it renames the new file to avoid overwriting.
🛠️ Secure File Storage

Files are stored in a predefined safe directory (UPLOAD_FOLDER), avoiding arbitrary file uploads to sensitive system locations.
🔄 Enforce Database Integrity

ondelete="CASCADE" ensures that when a user is deleted, their files are automatically removed.
⚡ Indexing for Faster Queries

Adding index=True on user_id speeds up file lookups.
'''

from extensions import db
from datetime import datetime
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'txt'}  # Define allowed file types
UPLOAD_FOLDER = '/secure/upload/directory'  # Set a safe directory for storing files

class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False, unique=True)  # Prevent duplicate file paths
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'file_path': self.file_path,
            'uploaded_at': self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
            'user_id': self.user_id
        }

    def __repr__(self):
        return f'<File {self.filename}>'

    @staticmethod
    def is_allowed_file(filename):
        """Check if the file has an allowed extension."""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @staticmethod
    def secure_save_file(uploaded_file):
        """Securely save the uploaded file and return the stored file path."""
        if not File.is_allowed_file(uploaded_file.filename):
            raise ValueError("Invalid file type. Allowed types: png, jpg, jpeg, pdf, txt")
        
        filename = secure_filename(uploaded_file.filename)  # Prevent path traversal attacks
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        # Ensure the filename does not already exist to avoid overwriting files
        if os.path.exists(file_path):
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(os.path.join(UPLOAD_FOLDER, f"{base}_{counter}{ext}")):
                counter += 1
            filename = f"{base}_{counter}{ext}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)

        uploaded_file.save(file_path)
        return file_path
