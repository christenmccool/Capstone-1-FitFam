from db import db
from datetime import datetime


class Workout(db.Model):
    """Workout in the database."""

    __tablename__ = "workouts"

    id = db.Column(
        db.Integer, 
        primary_key=True
    )

    source = db.Column(
        db.Text, 
    )

    title = db.Column(
        db.Text
    )

    description = db.Column(
        db.Text
    )

    score_type = db.Column(
        db.Text
    )

    date_posted = db.Column(
        db.Date,
        nullable = False,
        default=datetime.now()
    )

    
