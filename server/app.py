from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime

# Import your model and database
from models import db, Message

# Initialize the Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Enable CORS
CORS(app)

# Initialize Flask-Migrate and SQLAlchemy
migrate = Migrate(app, db)
db.init_app(app)

# Define the routes

# GET /messages: returns an array of all messages as JSON, ordered by created_at in ascending order.
@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return jsonify([message.to_dict() for message in messages])

# POST /messages: creates a new message with a body and username from params, and returns the newly created post as JSON.
@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    body = data.get('body')
    username = data.get('username')
    
    if not body or not username:
        return jsonify({'error': 'Both body and username are required'}), 400
    
    new_message = Message(body=body, username=username)
    db.session.add(new_message)
    db.session.commit()
    
    return jsonify(new_message.to_dict()), 201

# PATCH /messages/<int:id>: updates the body of the message using params, and returns the updated message as JSON.
@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = db.session.get(Message, id)
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    data = request.get_json()
    body = data.get('body')
    
    if not body:
        return jsonify({'error': 'Body is required'}), 400
    
    message.body = body
    message.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(message.to_dict())

# DELETE /messages/<int:id>: deletes the message from the database.
@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = db.session.get(Message, id)
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    db.session.delete(message)
    db.session.commit()
    
    return jsonify({'message': 'Message deleted successfully'}), 200

# Run the application
if __name__ == '__main__':
    app.run(port=5555)
