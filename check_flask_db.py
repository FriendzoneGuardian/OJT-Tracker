import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ojt_tracker.db'
db = SQLAlchemy(app)

class OJTEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    total_hours = db.Column(db.Float)

with app.app_context():
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    # This will show where it's actually looking
    try:
        count = OJTEntry.query.count()
        print(f"OJTEntry count: {count}")
        entries = OJTEntry.query.all()
        for e in entries:
            print(f"  ID: {e.id}, Date: {e.date}, Hours: {e.total_hours}")
    except Exception as e:
        print(f"Error querying DB: {e}")
