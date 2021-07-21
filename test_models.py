"""View tests."""

#    FLASK_ENV=production python -m unittest test_views.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError

from db import db, connect_db
from models.user import User
from models.family import Family, User_Family
from models.workout import Workout
from models.result import Result

os.environ['DATABASE_URL'] = "postgres:///fitfam-test"
from app import app



db.drop_all()
db.create_all()


class ModelTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        User_Family.query.delete()
        Result.query.delete()
        Workout.query.delete()
        User.query.delete()
        Family.query.delete()
        db.session.commit()

        self.client = app.test_client()

        self.testuser = User.register(username="testuser",
                                    email="test@test.com",
                                    password="password",
                                    first_name="Bob",
                                    last_name="Smith")

        self.testfamily = Family(name="testfam")
        db.session.add(self.testfamily)
        db.session.commit()

        self.testfamily.users.append(self.testuser)
        self.testuser.primary_family_id = self.testfamily.id

        self.testworkout = Workout(family_id = self.testfamily.id, title='Run 5 miles', description='Keep a steady pace', score_type='Time')
        db.session.add(self.testworkout)
        db.session.commit()

    def test_register(self):
        """Test if User.register creates a User"""

        testuser2 = User.register(username="testuser2",
                                  email="test@test2.com",
                                  password="password",
                                  first_name="Sally",
                                  last_name="Jones")
                                  

        db.session.commit()

        self.assertIsInstance(testuser2, User)


    def test_post_result(self):
        """Test if User.register creates a User"""

        testResult = Result(user_id=self.testuser.id, workout_id=self.testworkout.id, score="60", comment="Felt great")       
        
        db.session.add(testResult)         
        db.session.commit()

        self.assertIsInstance(testResult, Result)