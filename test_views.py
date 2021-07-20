"""View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


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
app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""
        User_Family.query.delete()
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

    def test_signup(self):
        """Test if user is added on signup"""

        with self.client as c:

            data={"username":"testuser2",
                  "email":"test2@test.com",
                  "password":"password",
                  "first_name":"Sally",
                  "last_name":"Jones",
                  "existing_family_name": "testfam"}


            resp = c.post("/signup", data=data)

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            u = User.query.filter(User.email == "test2@test.com").first()
            self.assertEqual(u.username, "testuser2")
    

    def test_signup_follows_redirects(self):
        """Test if signup follows redirects"""

        with self.client as c:

            data={"username":"testuser2",
                  "email":"test2@test.com",
                  "password":"password",
                  "first_name":"Sally",
                  "last_name":"Jones",
                  "existing_family_name": "testfam"}

            resp = c.post("/signup", data=data, follow_redirects=True)
            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)

            u = User.query.filter(User.email == "test2@test.com").first()
            self.assertIn(f'<strong><p class="m-0 text-end">testfam</p></strong>', html)



    def test_can_add_result(self):
        """Test if logged in user can add a result to family's workout"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['curr_user'] = self.testuser.id

            resp = c.post(f"/workouts/{self.testworkout.id}", data={"score":"60", "comment":"Felt great"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn('<div class="fw-bold">60</div>', html)
            self.assertIn('<div>Felt great</div>', html)

