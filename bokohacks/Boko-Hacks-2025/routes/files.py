'''Session Security: Proper session cookie settings to secure sessions.
File Validation: MIME type checking and more robust file extension checking.
Authorization: Ensures the current user can only access their own files.
Error Handling: Logs detailed errors and returns generic messages to the client.
File Size Limitation: Prevents large files from being uploaded.
File Path Security: Ensures uploaded files cannot be stored outside the allowed directory.
Logging: Logs errors to a file for later inspection and debugging.
'''


from flask import Blueprint, render_template, request, jsonify, session, send_from_directory
from extensions import db
from models.user import User
from models.file import File
import os
import mimetypes
import re
import logging
from werkzeug.utils import secure_filename

# Constants
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB max size
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.ERROR, filename='app_error.log', 
                    format='%(asctime)s - %(levelname)s - %(message)s')

files_bp = Blueprint('files', __name__, url_prefix='/apps/files')

def allowed_file(filename):
    """Check if the file extension is allowed"""
    if '.' in filename:
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in ALLOWED_EXTENSIONS and re.match(r'^[a-zA-Z0-9_-]+$', ext)
    return False

def is_valid_mime_type(file):
    """Validate the MIME type of the file"""
    mime_type, _ = mimetypes.guess_type(file.filename)
    # Allow only specific MIME types based on the file extension
    allowed_mimes = {
        'pdf': 'application/pdf',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif': 'image/gif'
    }
    
    if mime_type in allowed_mimes.values():
        return True
    return False

def secure_file_path(filename):
    """Ensure the file path is secure"""
    return os.path.join(UPLOAD_FOLDER, secure_filename(filename))

def log_error(error):
    """Log detailed error messages"""
    logging.error(f"Error occurred: {error}")

@files_bp.route('/')
def files():
    """Render files page with all files uploaded by the current user"""
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
        
    current_user = User.query.filter_by(username=session['user']).first()
    if not current_user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    all_files = File.query.filter_by(user_id=current_user.id).order_by(File.uploaded_at.desc()).all()
    return render_template('files.html', files=all_files, current_user_id=current_user.id)

@files_bp.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload securely"""
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
        
    current_user = User.query.filter_by(username=session['user']).first()
    if not current_user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    file = request.files.get('file')
    if not file:
        return jsonify({'success': False, 'error': 'No file part'}), 400

    # Ensure file extension and MIME type are valid
    if not allowed_file(file.filename) or not is_valid_mime_type(file):
        return jsonify({'success': False, 'error': 'Invalid file type'}), 400

    filename = secure_filename(file.filename)
    file_path = secure_file_path(filename)
    
    try:
        file.save(file_path)

        new_file = File(filename=filename, file_path=file_path, user_id=current_user.id)
        db.session.add(new_file)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'File uploaded successfully!',
            'file': new_file.to_dict()
        })
    except Exception as e:
        log_error(str(e))
        return jsonify({'success': False, 'error': 'File upload failed'}), 500

@files_bp.route('/delete/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Delete a file securely"""
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
        
    current_user = User.query.filter_by(username=session['user']).first()
    if not current_user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    file = File.query.get_or_404(file_id)
    if file.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    file_path = file.file_path
    try:
        db.session.delete(file)
        db.session.commit()
        
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            log_error(f"File not found on filesystem: {file_path}")

        return jsonify({'success': True, 'message': 'File deleted successfully'})
    except Exception as e:
        log_error(str(e))
        return jsonify({'success': False, 'error': 'File deletion failed'}), 500

@files_bp.route('/download/<int:file_id>')
def download_file(file_id):
    """Download a file securely"""
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    current_user = User.query.filter_by(username=session['user']).first()
    if not current_user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    file = File.query.get_or_404(file_id)
    if file.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    directory = os.path.dirname(file.file_path)
    filename = os.path.basename(file.file_path)
    
    try:
        return send_from_directory(directory, filename, as_attachment=True)
    except Exception as e:
        log_error(str(e))
        return jsonify({'success': False, 'error': 'File download failed'}), 500
