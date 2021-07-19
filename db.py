from flask_sqlalchemy import SQLAlchemy 
import requests
from secret import API_KEY


db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)


#Get the default daily quote and workout from the database
#Get a random quote from the ZenQuotes API if it is not already stored in the database
#Get the daily workout from the SugarWOD API if it is not already stored in the database
from datetime import date
from models.quote import Quote
from models.workout import Workout_from_db

TODAY = date.today()

TODAY_STR = TODAY.strftime('%Y%m%d')
QUOTE_BASE_URL = "https://zenquotes.io/api/"
SUGARWOD_BASE_URL = "https://api.sugarwod.com/v2"

def update_db():
    DEFAULT_QUOTE = Quote.query.filter(Quote.date == TODAY).first()

    if not DEFAULT_QUOTE: 
        url = QUOTE_BASE_URL + '/random'
        response = requests.get(url)
        try:
            quote = response.json()[0]
            DEFAULT_QUOTE = Quote(quote=quote['q'], author=quote['a'], date=TODAY)
            db.session.add(DEFAULT_QUOTE)
            db.session.commit()
        except:
            DEFAULT_QUOTE = Quote.query.filter(Quote.date == date(2020,1,1)).first()
            
    slate_workout_list = Workout_from_db.query.filter(Workout_from_db.date == TODAY, Workout_from_db.source == 'slate').all()
    if slate_workout_list:
        DEFAULT_WORKOUT = slate_workout_list[1] if len(slate_workout_list)>1 else slate_workout_list[0]

    else:
        try:
            url = SUGARWOD_BASE_URL + '/workouts'
            response = requests.get(url, params= {"apiKey": API_KEY, "dates": TODAY_STR})
            workout_list = response.json().get('data')
            if data:
                for workout in workout_list:
                    wo_info = workout.get("attributes")
                    wo = Workout_from_db(title=wo_info['title'], description=wo_info['description'], score_type=wo_info['score_type'], source='slate', date=TODAY)
                    db.session.add(wo)
                db.session.commit()
                DEFAULT_WORKOUT = workout_list[1] if len(workout_list)>1 else workout_list[0]
        except:
            DEFAULT_WORKOUT = Workout_from_db.query.filter(Workout_from_db.date == date(2020,1,1)).first()

    return {"DEFAULT_QUOTE": DEFAULT_QUOTE, "DEFAULT_WORKOUT": DEFAULT_WORKOUT}

