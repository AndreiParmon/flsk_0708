from datetime import datetime
from . import db


class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
