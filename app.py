from flask import Flask, session, g, render_template, redirect, url_for, flash, request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import extract

import requests
import calendar
from db import db, connect_db, update_db
import functools

from forms import SignupForm, LoginForm, ResultForm, UserEditForm
from secret import API_KEY

app = Flask(__name__)

connect_db(app)

from models.user import User
from models.family import Family, User_Family
from models.workout import Workout
from models.quote import Quote
from models.result import Result, ResComment
from datetime import datetime, date

# db.create_all()
# db.session.commit()

app.config['SECRET_KEY'] = 'allfoodfits'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///fitfam'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Make sure the database is updated with today's quote and workouts
TODAY = date.today()
update_db()

def check_loggedin(func):
    @functools.wraps(func)
    def wrapper_check_loggedin(*args, **kwargs):
        if not g.user:
            flash("Access unauthorized. Log in to account to access content.", "danger")
            return redirect(url_for('home'))
        value = func(*args, **kwargs)
        return value
    return wrapper_check_loggedin


@app.before_request
def add_to_g():
    """If a user is logged in, add curr_user User object to Flask global."""

    if 'curr_user' in session:
        g.user = User.query.get(session['curr_user'])
    else:
        g.user = None


@app.route('/')
def home():
    """Show homepage
    - anononymous users: sign up page
    Include a quote of the day from ZenQuotes API

    - logged in family account users: workout of the day page 
    - logged in individual account users: workout log
    """

    if g.user:
        if g.user.account_type == 'fam':
            return redirect(url_for('show_current_workout', family_id=g.user.primary_family_id))
        elif g.user.account_type == 'ind':
            return redirect(url_for('show_log', user_id=g.user.id))
        
    else:
        quote = Quote.query.filter(Quote.date == TODAY).first()
        print(quote)
        return render_template('home_anon.html', quote=quote)


@app.route('/families/<int:family_id>/workout')
@check_loggedin
def show_current_workout(family_id):
    """Show today's workout for a given family."""

    family = Family.query.get_or_404(family_id)

    workout = Workout.query.filter(Workout.source == family.workout_source, Workout.date_posted==TODAY).first()

    return redirect(url_for('show_workout', family_id=family_id, workout_id=workout.id))


@app.route('/families/<int:family_id>/workout/<int:workout_id>', methods=["GET", "POST"])
@check_loggedin
def show_workout(family_id, workout_id):
    """Show workout of the day for a given family."""

    family = Family.query.get_or_404(family_id)
    workout = Workout.query.get_or_404(workout_id)

    result_list = Result.query.filter(Result.workout_id==workout_id, Result.family_id==family_id).all()

    quote = Quote.query.filter(Quote.date == TODAY).first()

    form = ResultForm()

    if form.validate_on_submit():
        result = Result(user_id=g.user.id, family_id=family_id, workout_id=workout_id, score=form.score.data, comment=form.comment.data)
        db.session.add(result)
        db.session.commit()
        return redirect(url_for('show_workout', family_id=family_id, workout_id=workout_id))

    if family in g.user.families:
        return render_template('families/workout.html', family=family, workout=workout, quote=quote, form=form, result_list=result_list)


@app.route('/results/<int:result_id>', methods=["POST"])
def comment_on_result(result_id):
    """Comment on result."""
    if g.user:
        result = Result.query.get_or_404(result_id)
        res_comment = request.json.get('res_comment')

        res_comment = ResComment(result_id=result.id, user_id=g.user.id, res_comment=res_comment)
        db.session.add(res_comment)
        db.session.commit()
        res_comment_serialized = res_comment.serialize()
        res_comment_serialized["user_image_url"] = res_comment.user.image_url
        res_comment_serialized["username"] = res_comment.user.username
        return jsonify(result = res_comment_serialized)

@app.route('/users/<int:user_id>')
@check_loggedin
def show_user(user_id):

    """Show profile information for a given user."""
    user = User.query.get(user_id)

    return render_template('users/profile.html', user=user)



@app.route('/users/edit', methods=["GET", "POST"])
@check_loggedin
def edit_profile():
    """Update profile for current user."""

    form = UserEditForm(obj=g.user)

    families = [(f.id, f.name) for f in g.user.families]
    form.primary_family_id.choices = families

    if form.validate_on_submit():
        user = User.authenticate(g.user.username,
                                form.password.data)
        if user:
            flash("User updated.", "success")

            g.user.username=form.username.data or g.user.username
            g.user.email=form.email.data or g.user.email
            g.user.first_name=form.first_name.data or g.user.first_name
            g.user.last_name=form.last_name.data or g.user.last_name
            g.user.nickname=form.nickname.data
            g.user.bio=form.bio.data 
            g.user.image_url=form.image_url.data or User.image_url.default.arg
            g.user.account_type=form.account_type.data
            g.user.primary_family_id=form.primary_family_id.data

            db.session.commit()

            return redirect(url_for('show_user', user_id=user.id))
            
        flash("Incorrect password.", 'danger')

    return render_template('users/edit.html', form=form)

# def getWeek(date):
#     yesterday = date.today() - timedelta(days=1)
#     yesterday.strftime('%m%d%y')


@app.route('/users/<int:user_id>/log')
@check_loggedin
def show_log(user_id):

    """Show results a week log for a given user."""
    todays_date = date.today()

    cal = calendar.Calendar()
    weekList = cal.monthdatescalendar(todays_date.year, todays_date.month)

    week_num = 0
    for week in weekList:
        if todays_date in week:
            break
        week_num += 1

    print(weekList[week_num])

    week_log = []
    for weekday in weekList[week_num]:
        result = Result.query.filter(Result.user_id==g.user.id, 
                                extract('month', Result.date_completed)==weekday.month,
                                extract('day', Result.date_completed)==weekday.day,
                                extract('year', Result.date_completed)==weekday.year).all()
        log = {'day' : weekday, 'results' : result}
        week_log.append(log)

    return render_template('users/log.html', week_log=week_log)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user signup.

    Create new user and add to database. Redirect to home page.

    If form is not valid or there is already a user with username or email, redirect to form.
    """

    form = SignupForm()

    if form.validate_on_submit():
        try:
            user = User.register(form.username.data,
                        form.email.data,
                        form.password.data,
                        form.first_name.data,
                        form.last_name.data)
            user.account_type = form.account_type.data
            db.session.commit()
            
            existing_family_name = form.data.get('existing_family_name')
            new_family_name = form.data.get('new_family_name')

            if existing_family_name:
                family = Family.query.filter(Family.name == existing_family_name).first()
                if family == None:
                    flash(f"FitFam '{existing_family_name}' does not exist. Try again or create your own FitFam.", 'danger')
                    return redirect(url_for('signup'))
                else:
                    user.families.append(family)
                    user.role = 'user'
                    user.primary_family_id = family.id
                    db.session.commit()
            elif new_family_name:
                try:
                    family = Family(name=new_family_name)
                    db.session.add(family)
                    user.families.append(family)
                    user.role = 'admin'
                    user.primary_family_id = family.id
                    db.session.commit()
                except IntegrityError:
                    flash("Family name already taken.", 'danger')
                    # return redirect(url_for('signup'))
                    return render_template('users/signup.html', form=form)
            else:
                user.role = 'ind_user'
                db.session.commit()

        except IntegrityError:
            flash("Username or email already taken.", 'danger')
            return render_template('users/signup.html', form=form)
            # return redirect(url_for('signup'))

        session['curr_user'] = user.id
            
        flash(f"Welcome to FitFam, {user.username}!", "success")
        return redirect(url_for('home'))

    return render_template('users/signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login. 
    
    Authenticate username and password. Redirect to home page.

    If username or password are invalid, redirect to form.
    """
    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                form.password.data)
        if user:
            session['curr_user'] = user.id
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for('home'))

        flash("Invalid username or password.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle user logout."""

    if 'curr_user' in session:
        del session['curr_user' ]

    flash("User logged out.", 'success')

    return redirect(url_for('home'))



@app.route('/families')
def search_families():
    """Allow user to search for an existing FitFam
    """
    search = request.args.get('q')
    if not search:
        families = Family.query.all()
        families_serialized = [family.serialize() for family in families]

    else:
        families = Family.query.filter(Family.name.like(f"%{search}%")).all()

    if families:
        families_serialized = [family.serialize() for family in families]

        for family in families_serialized:
            count = User_Family.query.filter(User_Family.family_id == family['id']).count()
            family['count'] = count

    else:
        families_serialized = []
    
    return jsonify(results=families_serialized)















SUGARWOD_BASE_URL = "https://api.sugarwod.com/v2"

@app.route('/workout')
def workout():
    url = SUGARWOD_BASE_URL + '/workouts'
    response = requests.get(url, params= {"apiKey": API_KEY})
    workout = response.json()
    return workout


@app.route('/heroes')
def heroes():
    url = SUGARWOD_BASE_URL + '/benchmarks/category/heroes'
    response = requests.get(url, params= {"apiKey": API_KEY})
    heroes = response.json()
    return heroes

@app.route('/girls')
def girls():
    url = SUGARWOD_BASE_URL + '/benchmarks/category/girls'
    response = requests.get(url, params= {"apiKey": API_KEY})
    girls = response.json()
    return girls

@app.route('/movements')
def movements():
    url = SUGARWOD_BASE_URL + '/movements'
    response = requests.get(url, params= {"apiKey": API_KEY})
    movements = response.json()
    return movements




