from db import db
from datetime import datetime


class Workout(db.Model):
    """Workout in the database."""

    __tablename__ = "workouts"

    id = db.Column(
        db.Integer, 
        primary_key=True
    )

    family_id = db.Column(
        db.Integer,
        db.ForeignKey('families.id')
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

    primary = db.Column(
        db.Boolean,
        default = True
    )

    score_type = db.Column(
        db.Text
    )

    date_posted = db.Column(
        db.Date,
        nullable = False,
        default=datetime.now()
    )

    family = db.relationship('Family', backref='workout')
    results = db.relationship('Result', backref='workout', cascade = "all,delete")

    def serialize(self):
        return {"id": self.id,
                "family_id": self.family_id,
                "title": self.title,
                "description": self.description,
                "score_type": self.score_type,
                "source": self.source,
                "date": self.date_posted.strftime('%Y%m%d') if self.date_posted else None
                }


class Workout_from_db(db.Model):
    """Workout from the SugarWOD database."""

    __tablename__ = "workouts_from_db"

    id = db.Column(
        db.Integer, 
        primary_key=True
    )

    title = db.Column(
        db.Text    
    )

    description = db.Column(
        db.Text
    )

    movements = db.Column(
        db.JSON
    )

    score_type = db.Column(
        db.Text
    )

    source = db.Column(
        db.Text
    )

    date = db.Column(
        db.Date
    )

    def serialize(self):
        return {"id": self.id,
                "title": self.title,
                "description": self.description,
                "score_type": self.score_type,
                "source": self.source,
                "date": self.date.strftime('%Y%m%d') if self.date else None
                }