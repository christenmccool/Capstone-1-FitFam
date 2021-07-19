from db import db
from datetime import datetime

class Result(db.Model):
    """Workout result in the database."""

    __tablename__ = "results"

    id = db.Column(
        db.Integer, 
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id')
    )

    workout_id = db.Column(
        db.Integer,
        db.ForeignKey('workouts.id')
    )
    
    date_completed = db.Column(
        db.DateTime,
        nullable = False,
        default=datetime.now()
    )

    score = db.Column(
        db.Text
    )

    comment = db.Column(
        db.Text
    )

    user = db.relationship('User', backref='results')
    res_comments = db.relationship('ResComment', backref='result', cascade = "all,delete")


class ResComment(db.Model):
    """Workout result in the database."""

    __tablename__ = "res_comments"

    id = db.Column(
        db.Integer, 
        primary_key=True
    )

    result_id = db.Column(
        db.Integer,
        db.ForeignKey('results.id')
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id')
    )
    
    date = db.Column(
        db.DateTime,
        nullable = False,
        default=datetime.now()
    )

    res_comment = db.Column(
        db.Text
    )

    user = db.relationship('User')


    def serialize(self):
        return {"id": self.id,
                "result_id" : self.result_id,
                "user_id": self.user_id,
                "date": self.date.strftime('%B %d, %Y  %I:%M %p'),
                "res_comment": self.res_comment
                }
