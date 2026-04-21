from flask_sqlalchemy import SQLAlchemy

# This 'db' object will handle all our database actions
db = SQLAlchemy()

class Adoption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=True)
    # Optional: track which pet they want
    pet_name = db.Column(db.String(100), nullable=True)