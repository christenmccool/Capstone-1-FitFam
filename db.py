from flask_sqlalchemy import SQLAlchemy 
import requests
from secret import API_KEY


db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)


from datetime import datetime, date
from models.quote import Quote
from models.workout import Workout


#Update FitFam db daily with quote and workouts

TODAY = date.today()
TODAY_STR = TODAY.strftime('%Y%m%d')

QUOTE_BASE_URL = "https://zenquotes.io/api/"

def update_quote_db():
    """Get a reandom quote from the ZenQuotes API and store it in the db under today's date"""
    url = QUOTE_BASE_URL + '/random'

    response = requests.get(url)
    quote = response.json()[0]

    db_quote = Quote(quote=quote['q'], author=quote['a'], date=TODAY)
    db.session.add(db_quote)
    db.session.commit()
    
SUGARWOD_BASE_URL = "https://api.sugarwod.com/v2"


def update_slate_workout_db():
    """Get today's Slate workout from the SugarWOD API and store it in the db under today's date"""
    url = SUGARWOD_BASE_URL + '/workouts'
    response = requests.get(url, params= {"apiKey": API_KEY, "dates":TODAY_STR})

    data = response.json().get('data')
    if data:
        for entry in data:
            workout = entry['attributes']
            db_workout = Workout(source='slate', title=workout['title'], description=workout['description'], score_type=workout['score_type'])
            db.session.add(db_workout)
        db.session.commit()
    

def update_hq_workout_db():
    """Get today's Crossfit HW workout from the SugarWOD API and store it in the db under today's date"""
    url = SUGARWOD_BASE_URL + '/workoutshq'
    response = requests.get(url, params= {"apiKey": API_KEY, "dates":TODAY_STR})

    data = response.json().get('data')
    if data:
        workout = data[0]['attributes'] 

        db_workout = Workout(source='hq', title=workout['title'], description=workout['description'], score_type=workout['score_type'])
        db.session.add(db_workout)
        db.session.commit()


def update_db():
    quote = Quote.query.filter(Quote.date == TODAY).first()

    if not quote:
        update_quote_db()
   
    slate = Workout.query.filter(Workout.date_posted == TODAY, Workout.source=='slate').first()

    if not slate:
        update_slate_workout_db()

    crossfithq = Workout.query.filter(Workout.date_posted == TODAY, Workout.source=='hq').first()

    if not crossfithq:
        update_hq_workout_db()



