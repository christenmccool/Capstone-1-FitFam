from app import app
from db import db
from flask import jsonify
import requests
from secret import API_KEY
from datetime import datetime, date, timedelta


from models.workout import Workout_from_db

db.session.rollback()
db.session.commit()

db.drop_all()
db.create_all()

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