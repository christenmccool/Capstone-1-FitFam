from db import db

class Family(db.Model):
    """Family in the database."""

    __tablename__ = "families"

    id = db.Column(
        db.Integer, 
        primary_key=True
    )

    name = db.Column(
        db.String(20),
        nullable=False,
        unique=True
    )

    workout_source = db.Column(
        db.Text,
        nullable=False,
        default='slate'
    )

    info = db.Column(
        db.Text
    )

    users = db.relationship('User', secondary='users_families', backref='families', cascade = "all,delete")

    def serialize(self):
        return {"id": self.id,
                "name" : self.name,
                "info": self.info
                }


class User_Family(db.Model):
    """User and family mapping."""

    __tablename__ = "users_families"

    id = db.Column(
        db.Integer, 
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id')
    )

    family_id = db.Column(
        db.Integer,
        db.ForeignKey('families.id')
    )

