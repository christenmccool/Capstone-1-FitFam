from app import app
from db import db

from models.user import User
from models.family import Family, User_Family
from models.quote import Quote
from models.workout import Workout
from models.result import Result, ResComment
from models.workout import Workout_from_db


from flask import jsonify
import requests
from secret import API_KEY
from datetime import date, timedelta

db.session.rollback()
db.session.commit()

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

db.session.commit()



SUGARWOD_BASE_URL = "https://api.sugarwod.com/v2"

def add_quotes_from_db():
    quote = Quote(quote='The only person you are destined to become is the person you decide to be.', author='Ralph Waldo Emerson', date=date(2020,1,1))
    db.session.add(quote)
    db.session.commit()

def add_workouts_from_db():

    # "hero" benchmark workouts
    url = SUGARWOD_BASE_URL + '/benchmarks/category/heroes?page[skip]=0&page[limit]=100'
    response = requests.get(url, params= {"apiKey": API_KEY})
    workout_list = response.json().get('data')

    for workout in workout_list:
        wo_info = workout.get("attributes")
        wo = Workout_from_db(title=wo_info['name'], description=wo_info['description'], score_type=wo_info['score_type'])
        db.session.add(wo)
    
    # "girl" benchmark workouts
    url = SUGARWOD_BASE_URL + '/benchmarks/category/girls'
    response = requests.get(url, params= {"apiKey": API_KEY})
    workout_list = response.json().get('data')

    for workout in workout_list:
        wo_info = workout.get("attributes")
        wo = Workout_from_db(title=wo_info['name'], description=wo_info['description'], score_type=wo_info['score_type'])
        db.session.add(wo)
    
    # benchmark workouts from the Crossfit Games
    url = SUGARWOD_BASE_URL + '/benchmarks/category/games?page[skip]=0&page[limit]=100'
    response = requests.get(url, params= {"apiKey": API_KEY})
    workout_list = response.json().get('data')

    for workout in workout_list:
        wo_info = workout.get("attributes")
        wo = Workout_from_db(title=wo_info['name'], description=wo_info['description'], score_type=wo_info['score_type'])
        db.session.add(wo)


    # past 5 weeks of Slate workouts
    TODAY = date.today()

    count = 5
    last_day = TODAY
    while count > 0:
        last_day_str = last_day.strftime('%Y%m%d')

        six_days_prior = last_day - timedelta(days=6)
        six_days_prior_str = six_days_prior.strftime('%Y%m%d')

  
        url = SUGARWOD_BASE_URL + f"/workouts?dates={six_days_prior_str}-{last_day_str}"
        response = requests.get(url, params= {"apiKey": API_KEY})
        workout_list = response.json().get('data')

        for workout in workout_list:
            wo_info = workout.get("attributes")
            wo = Workout_from_db(title=wo_info['title'], description=wo_info['description'], score_type=wo_info['score_type'], source='slate', date=wo_info['scheduled_date'])
            db.session.add(wo)
        
        last_day = last_day - timedelta(days=7)
        count -= 1


    # default workout
    workout = Workout_from_db(title='Choose your own adventure', description='Pick your favorite way to be active and enjoy some time moving!', score_type='None', source='none', date=date(2020,1,1))
    db.session.add(workout)

    db.session.commit()

add_quotes_from_db()
add_workouts_from_db()