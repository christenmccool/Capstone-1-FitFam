from app import app
from db import db

from models.user import User
from models.family import Family, User_Family
from models.quote import Quote
from models.workout import Workout
from models.result import Result, ResComment
from datetime import date, timedelta


db.session.commit()

db.drop_all()
db.create_all()


user1 = User.register(username='bobby', password='password', email='bob@mail.com', first_name='bob', last_name='jones')
user2 = User.register(username='jane', password='password', email='jane@mail.com', first_name='jane', last_name='jones')
user3 = User.register(username='sammy', password='password', email='sam@mail.com', first_name='sam', last_name='smith')

user1.account_type = 'fam'
user2.account_type = 'fam'
user3.account_type = 'fam'

user1.role = 'user'
user2.role = 'user'
user3.role = 'user'

users = [user1, user2, user3]
db.session.add_all(users)
db.session.commit()

family1 = Family(name="fitfam1")
family2 = Family(name="fitfam2")

families = [family1, family2]
db.session.add_all(families)
db.session.commit()

family1.users.append(user1)
family1.users.append(user2)
family2.users.append(user2)
family2.users.append(user3)

user1.primary_family_id = family1.id
user2.primary_family_id = family1.id
user3.primary_family_id = family2.id


yesterday = date.today() - timedelta(days=1)
yesterday.strftime('%m%d%y')

workout1 = Workout(source='misc', title='Try hard', description='Do this for time', score_type='Time', date_posted=yesterday)
db.session.add(workout1)
db.session.commit()

result1 = Result(user_id=1, family_id=1, workout_id=workout1.id, score='10', comment='I did great', date_completed=yesterday)
db.session.add(result1)

res_comment1 = ResComment(user_id=1, result_id=result1.id, res_comment='Wow!!', date=yesterday)
db.session.add(res_comment1)

quote1 = Quote(quote='Do your best', author='me', date=yesterday)
db.session.add(quote1)

db.session.commit()