from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flasgger import Swagger
from datetime import timedelta

app = Flask(__name__)

# --- Config ---
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost:3306/notes_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = "super-secret"
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# --- Swagger Config ---
swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "Notes API",
        "description": "API untuk manajemen catatan dengan autentikasi JWT",
        "version": "1.0.0"
    },
    "basePath": "/",
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Token. Format: Bearer {token}"
        }
    }
})

# --- Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# --- Routes ---
@app.route("/register", methods=["POST"])
def register():
    """
    Register User
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        schema:
          id: Register
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: testuser
            password:
              type: string
              example: 123456
    responses:
      201:
        description: User registered successfully
    """
    data = request.get_json()
    hashed_pw = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    new_user = User(username=data["username"], password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    """
    Login User
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        schema:
          id: Login
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: testuser
            password:
              type: string
              example: 123456
    responses:
      200:
        description: Login success, return JWT token
    """
    data = request.get_json()
    user = User.query.filter_by(username=data["username"]).first()
    if user and bcrypt.check_password_hash(user.password, data["password"]):
        token = create_access_token(identity=user.id)
        return jsonify({"token": token})
    return jsonify({"message": "Invalid credentials"}), 401

@app.route("/notes", methods=["POST"])
@jwt_required()
def create_note():
    """
    Create Note
    ---
    tags:
      - Notes
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          id: Note
          required:
            - title
            - content
          properties:
            title:
              type: string
              example: My First Note
            content:
              type: string
              example: This is my note
    responses:
      201:
        description: Note created
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    new_note = Note(title=data["title"], content=data["content"], user_id=user_id)
    db.session.add(new_note)
    db.session.commit()
    return jsonify({"message": "Note created"}), 201

@app.route("/notes", methods=["GET"])
@jwt_required()
def get_notes():
    """
    Get All Notes
    ---
    tags:
      - Notes
    security:
      - Bearer: []
    responses:
      200:
        description: List of notes
    """
    user_id = get_jwt_identity()
    notes = Note.query.filter_by(user_id=user_id).all()
    result = [{"id": n.id, "title": n.title, "content": n.content} for n in notes]
    return jsonify(result)

@app.route("/notes/<int:note_id>", methods=["PUT"])
@jwt_required()
def update_note(note_id):
    """
    Update Note
    ---
    tags:
      - Notes
    security:
      - Bearer: []
    parameters:
      - in: path
        name: note_id
        required: true
        type: integer
      - in: body
        name: body
        schema:
          required:
            - title
            - content
          properties:
            title:
              type: string
              example: Updated Note
            content:
              type: string
              example: Updated content
    responses:
      200:
        description: Note updated
    """
    user_id = get_jwt_identity()
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()
    if not note:
        return jsonify({"message": "Note not found"}), 404

    data = request.get_json()
    note.title = data["title"]
    note.content = data["content"]
    db.session.commit()
    return jsonify({"message": "Note updated"})

@app.route("/notes/<int:note_id>", methods=["DELETE"])
@jwt_required()
def delete_note(note_id):
    """
    Delete Note
    ---
    tags:
      - Notes
    security:
      - Bearer: []
    parameters:
      - in: path
        name: note_id
        required: true
        type: integer
    responses:
      200:
        description: Note deleted
    """
    user_id = get_jwt_identity()
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()
    if not note:
        return jsonify({"message": "Note not found"}), 404

    db.session.delete(note)
    db.session.commit()
    return jsonify({"message": "Note deleted"})

@app.route("/health", methods=["GET"])
def health():
    """
    Health Check
    ---
    tags:
      - Health
    responses:
      200:
        description: API is running
    """
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
