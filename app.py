from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'texts.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['APPLICATION_NAME'] = 'Orbit11'
db = SQLAlchemy(app)

# Text model
class Text(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    x_position = db.Column(db.Integer, nullable=False)
    y_position = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(50), nullable=True, default='rgba(255, 255, 255, 0.9)')
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)

# Ensure database and tables are created
def init_db():
    with app.app_context():
        # Drop all existing tables to recreate with new schema
        db.drop_all()
        # Create all tables
        db.create_all()

# Initialize the database
init_db()

# Garder une trace des utilisateurs connectés
connected_users = set()

@app.route('/')
def serve_frontend():
    return send_from_directory('.', 'index.html')

@app.route('/save_text', methods=['POST'])
def save_text():
    data = request.json
    
    # Validate text length
    if len(data['text']) > 50:
        return jsonify({"status": "error", "message": "Le texte ne peut pas dépasser 50 caractères"}), 400
        
    # Check if text with this ID already exists
    existing_text = Text.query.get(data['id'])
    
    if not existing_text:
        new_text = Text(
            id=data['id'],
            content=data['text'], 
            x_position=data['x'], 
            y_position=data['y'],
            color=data.get('color', 'rgba(255, 255, 255, 0.9)'),
            likes=0,
            dislikes=0
        )
        db.session.add(new_text)
        db.session.commit()
        return jsonify({"status": "success"}), 200
    
    return jsonify({"status": "already_exists"}), 200

@app.route('/update_text_position', methods=['POST'])
def update_text_position():
    data = request.json
    # Find the text by ID and update its position
    text = Text.query.get(data['id'])
    
    if text:
        text.x_position = data['x']
        text.y_position = data['y']
        
        db.session.commit()
        return jsonify({"status": "success"}), 200
    
    # If no text found, create a new one
    new_text = Text(
        id=data['id'],
        content=data['text'], 
        x_position=data['x'], 
        y_position=data['y'],
        likes=0,
        dislikes=0
    )
    db.session.add(new_text)
    db.session.commit()
    
    return jsonify({"status": "created"}), 200

@app.route('/update_text_color', methods=['POST'])
def update_text_color():
    data = request.json
    # Find the text by ID and update its color
    text = Text.query.get(data['id'])
    
    if text:
        text.color = data['color']
        
        db.session.commit()
        return jsonify({"status": "success"}), 200
    
    return jsonify({"status": "not_found"}), 404

@app.route('/like_text', methods=['POST'])
def like_text():
    data = request.json
    text = Text.query.get(data['id'])
    
    if text:
        text.likes += 1
        db.session.commit()
        return jsonify({
            "status": "success", 
            "likes": text.likes, 
            "dislikes": text.dislikes
        }), 200
    
    return jsonify({"status": "not_found"}), 404

@app.route('/dislike_text', methods=['POST'])
def dislike_text():
    data = request.json
    text = Text.query.get(data['id'])
    
    if text:
        text.dislikes += 1
        db.session.commit()
        return jsonify({
            "status": "success", 
            "likes": text.likes, 
            "dislikes": text.dislikes
        }), 200
    
    return jsonify({"status": "not_found"}), 404

@app.route('/delete_text', methods=['POST'])
def delete_text():
    data = request.json
    # Find and delete text by ID
    text = Text.query.get(data['id'])
    
    if text:
        db.session.delete(text)
        db.session.commit()
        return jsonify({"status": "success"}), 200
    
    return jsonify({"status": "not_found"}), 404

@app.route('/get_texts', methods=['GET'])
def get_texts():
    texts = Text.query.all()
    return jsonify([{
        'id': text.id, 
        'content': text.content, 
        'x': text.x_position, 
        'y': text.y_position,
        'color': text.color,
        'likes': text.likes,
        'dislikes': text.dislikes
    } for text in texts])

@app.route('/user_count')
def get_user_count():
    return jsonify({'count': len(connected_users)})

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    connected_users.add(request.sid)
    emit('user_count', {'count': len(connected_users)}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    connected_users.remove(request.sid)
    emit('user_count', {'count': len(connected_users)}, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port)
