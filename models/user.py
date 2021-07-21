from db import db
from flask_bcrypt import Bcrypt 

bcrypt = Bcrypt()

class User(db.Model):
    """User in the database."""

    __tablename__ = "users"

    id = db.Column(
        db.Integer, 
        primary_key=True
    )

    username = db.Column(
        db.String(20), 
        nullable=False, 
        unique=True
    )

    email = db.Column(
        db.String(40), 
        nullable=False, 
        unique=True
    )

    password = db.Column(
        db.Text, 
        nullable=False    
    )

    first_name = db.Column(
        db.String(30), 
        nullable=False
    )

    last_name = db.Column(
        db.String(30), 
        nullable=False
    )

    nickname = db.Column(
        db.String(20)    
    )

    bio = db.Column(
        db.String(200)
    )

    image_url = db.Column(
        db.Text, 
        nullable=False, 
        default="/static/images/user.png"
    )

    account_type = db.Column(
        db.Text
    )

    role = db.Column(
        db.Text,
        default = 'user'
    )

    primary_family_id = db.Column(
        db.Integer,
        db.ForeignKey('families.id')
    )

    @classmethod
    def register(cls, username, email, password, first_name, last_name):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_password = bcrypt.generate_password_hash(password).decode("utf8")

        user = User(
            username=username,
            email=email,
            password=hashed_password,
            first_name = first_name,
            last_name = last_name
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Search for a user with matching `username` and `password`.

        If username isn't found or if password is wrong, returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    
    @classmethod
    def change_password(cls, username, password, newpassword1, newpassword2):
        """Search for a user with matching `username` and `password`.

        Changes password and returns user object with new password.

        If username isn't found or if password is wrong, returns False.
        """

        user = cls.authenticate(username, password)

        if user and newpassword1 == newpassword2:
            new_hashed_password = bcrypt.generate_password_hash(newpassword1).decode('UTF-8')
            user.password = new_hashed_password
            db.session.add(user)
            return user

        return False

