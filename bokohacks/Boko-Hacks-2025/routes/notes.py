'''Problem: The create_note route does not sanitize user input, which leaves it vulnerable to XSS attacks. Users can inject malicious HTML or JavaScript in the title or content, which could be executed when the note is rendered.
   In the search_notes route, you are using string interpolation to build an SQL query. This allows for SQL injection, where a user could inject arbitrary SQL code into the query.
   There’s a potential access control vulnerability in the delete_note route. Right now, a user can delete any note if they know the note_id. You should ensure that users can only delete their own notes.
   The session validation for 'user' not in session works well but can be improved for better user feedback. You could return an error page or a redirection to the login page rather than just returning a JSON error.
   The /debug route exposes sensitive information like user and note data, which could be a security risk if it is accessible in a production environment.
   
'''







from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from extensions import db
from models.user import User
from models.note import Note
from datetime import datetime
from sqlalchemy import text
from werkzeug.utils import secure_filename
from flask import Markup

notes_bp = Blueprint('notes', __name__, url_prefix='/apps/notes')

@notes_bp.route('/create', methods=['POST'])
def create_note():
    """Create a new note - Secured against XSS"""
    if 'user' not in session:
        return redirect(url_for('login.login'))  # Redirect if not logged in
        
    current_user = User.query.filter_by(username=session['user']).first()
    if not current_user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    title = request.form.get('title')
    content = request.form.get('content')
    
    if not title or not content:
        return jsonify({'success': False, 'error': 'Title and content are required'}), 400
    
    # Sanitize input to prevent XSS
    title = Markup.escape(title)
    content = Markup.escape(content)
    
    try:
        note = Note(
            title=title,
            content=content,
            created_at=datetime.now(),
            user_id=current_user.id
        )
        
        db.session.add(note)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Note created successfully',
            'note': {
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'created_at': note.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'user_id': note.user_id
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@notes_bp.route('/search')
def search_notes():
    """Search notes with SQL injection prevention"""
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
        
    current_user = User.query.filter_by(username=session['user']).first()
    if not current_user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    query = request.args.get('q', '')
    
    try:
        # Use ORM to prevent SQL Injection
        result = db.session.query(Note).filter(
            Note.title.like(f"%{query}%") | Note.content.like(f"%{query}%")
        ).all()
        
        notes = [{'id': note.id, 'title': note.title, 'content': note.content} for note in result]
        
        return jsonify({
            'success': True,
            'notes': notes
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
