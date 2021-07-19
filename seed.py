from app import app
from db import db

from models.user import User
from models.family import Family, User_Family
from models.quote import Quote
from models.workout import Workout
from models.result import Result, ResComment
from datetime import date, timedelta

# db.session.rollback()
# db.session.commit()

db.drop_all()
db.create_all()


user1 = User.register(username='bobby', password='password', email='bob@mail.com', first_name='bob', last_name='jones')
user2 = User.register(username='jane', password='password', email='jane@mail.com', first_name='jane', last_name='jones')
user3 = User.register(username='sammy', password='password', email='sam@mail.com', first_name='sam', last_name='smith')
user4 = User.register(username='jenny', password='password', email='jen@mail.com', first_name='sam', last_name='smith')

user1.account_type = 'fam'
user2.account_type = 'fam'
user3.account_type = 'fam'
user4.account_type = 'fam'

user1.image_url = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSnDY2gd9JvWpzPMPzwmdrnZh-57fTNks__tw&usqp=CAU'
user2.image_url = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTChbG6-n3v-V4Jw_7klbd9Awsbn2Fl3CHG8g&usqp=CAU'
user3.image_url = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRYBdNgEw3ZO6eVsOBTHN_XQe3as4eA1T34Nw&usqp=CAU'
user4.image_url = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQJ3FY6JZaTWFOznA8lUfj53yiOT7ceOtX5TA&usqp=CAU'

user1.role = 'admin'
user3.role = 'admin'

users = [user1, user2, user3]
db.session.add_all(users)
db.session.commit()

family1 = Family(name="fitfam1", workout_source='slate')
family2 = Family(name="fitfam2", workout_source='hq')

families = [family1, family2]
db.session.add_all(families)
db.session.commit()

family1.users.append(user1)
family1.users.append(user2)
family2.users.append(user2)
family2.users.append(user3)
family2.users.append(user4)


user1.primary_family_id = family1.id
user2.primary_family_id = family1.id
user3.primary_family_id = family2.id
user4.primary_family_id = family2.id


yesterday = date.today() - timedelta(days=1)

workout1 = Workout(family_id = family1.id, source='misc', title='Run 5 miles', description='Keep a steady pace', score_type='Time', date_posted=yesterday)
workout2 = Workout(family_id = family2.id, source='misc', title='Max back squat', description='Try to improve by 5 pounds', score_type='Load', date_posted=yesterday)
db.session.add(workout1)
db.session.add(workout2)
db.session.commit()

result1 = Result(user_id=1, workout_id=workout1.id, score='40 minutes', comment='I felt great!', date_completed=yesterday)
result2 = Result(user_id=2, workout_id=workout1.id, score='50 minutes', comment='I walked a lot.', date_completed=yesterday)
result3 = Result(user_id=1, workout_id=workout2.id, score='200', comment='Not a PR.', date_completed=yesterday)
db.session.add(result1)
db.session.add(result2)
db.session.add(result2)

db.session.commit()
res_comment1 = ResComment(user_id=2, result_id=result1.id, res_comment='Wow!! Invite me next time', date=yesterday)
db.session.add(res_comment1)

quote1 = Quote(quote='Do your best', author='me', date=yesterday)
db.session.add(quote1)

db.session.commit()