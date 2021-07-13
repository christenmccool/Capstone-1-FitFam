from db import db
from datetime import datetime

class Quote(db.Model):
    """Quote in the database."""

    __tablename__ = "quotes"

    id = db.Column(
        db.Integer, 
        primary_key=True
    )

    quote = db.Column(
        db.Text, 
        nullable=False
    )

    author = db.Column(
        db.Text
    )    

    date = db.Column(
        db.Date,
        nullable = False,
        default=datetime.utcnow()
    )
    