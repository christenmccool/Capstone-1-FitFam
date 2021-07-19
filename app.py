from flask import Flask, session, g, render_template, redirect, url_for, flash, request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import extract
import requests
import calendar
from db import db, connect_db, update_db
import functools
from forms import SignupForm, LoginForm, ResultForm, ResCommentForm, UserEditForm, WorkoutAddForm, WorkoutEditForm
from secret import API_KEY
import os

app = Flask(__name__)
connect_db(app)

from models.user import User
from models.family import Family, User_Family
from models.workout import Workout, Workout_from_db
from models.quote import Quote
from models.result import Result, ResComment
from datetime import datetime, date

app.config['SECRET_KEY'] = 'allfoodfits'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///fitfam'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgres:///fitfam').replace("://", "ql://", 1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


#Get the default daily quote and workout from the database
TODAY = date.today()
default_values = update_db()
DEFAULT_QUOTE = default_values['DEFAULT_QUOTE']
DEFAULT_WORKOUT = default_values['DEFAULT_WORKOUT']


def check_logged_in(func):
    """Wrapper function to only allow acccess to a route if a user is logged in."""

    @functools.wraps(func)
    def wrapper_check_logged_in(*args, **kwargs):
        if not g.user:
            flash("Access unauthorized. Log in to account to access content.", "danger")
            return redirect(url_for('home'))
        value = func(*args, **kwargs)
        return value
    return wrapper_check_logged_in


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
        # if g.user.account_type == 'fam':
        #     return redirect(url_for('show_current_workout', family_id=g.user.primary_family_id))
        # elif g.user.account_type == 'ind':
        #     return redirect(url_for('show_log', user_id=g.user.id))
        return redirect(url_for('show_current_workout', family_id=g.user.primary_family_id))
    else:
        return render_template('home_anon.html', quote=DEFAULT_QUOTE)


@app.route('/families/<int:family_id>')
@check_logged_in
def show_current_workout(family_id):
    """Show family's current workout."""

    family = Family.query.get_or_404(family_id)

    workout = Workout.query.filter(Workout.family_id == family.id, Workout.date_posted==TODAY).order_by(Workout.primary.desc()).first()
    
    if not workout:
        workout = Workout(family_id=family.id, title=DEFAULT_WORKOUT.title, description=DEFAULT_WORKOUT.description, score_type=DEFAULT_WORKOUT.score_type, source=DEFAULT_WORKOUT.source, primary=True, date_posted=TODAY)
        db.session.add(workout)
        db.session.commit()

    return redirect(url_for('show_workout', workout_id=workout.id))


@app.route('/workouts/<int:workout_id>', methods=["GET", "POST"])
@check_logged_in
def show_workout(workout_id):
    """Show workout results and result comments.
    Post workout results for a given workout.
    """

    workout = Workout.query.get_or_404(workout_id)

    if workout.family in g.user.families:
        result_list = Result.query.filter(Result.workout_id==workout_id).all()

        form = ResultForm(date_completed=TODAY)

        if form.validate_on_submit():
            result = Result(user_id=g.user.id, workout_id=workout_id, score=form.score.data, comment=form.comment.data, date_completed=form.date_completed.data, )
            db.session.add(result)
            db.session.commit()
            return redirect(url_for('show_workout', workout_id=workout_id))

        workout_complete = False
        result = Result.query.filter(Result.user_id==g.user.id, Result.workout_id==workout.id).all()

        if result:
            workout_complete = True

        return render_template('families/workout.html', workout=workout, quote=DEFAULT_QUOTE, form=form, result_list=result_list, workout_complete=workout_complete)
        
    flash("Access unauthorized. You may only access content for your own family.", "danger")
    return redirect(url_for('home'))

@app.route('/results/<int:result_id>', methods=["POST"])
@check_logged_in
def comment_on_result(result_id):
    """Comment on result."""
    result = Result.query.get_or_404(result_id)

    if result.workout.family in g.user.families:
        res_comment = request.json.get('res_comment')

        res_comment = ResComment(result_id=result.id, user_id=g.user.id, res_comment=res_comment)
        db.session.add(res_comment)
        db.session.commit()

        res_comment_serialized = res_comment.serialize()
        res_comment_serialized["user_image_url"] = res_comment.user.image_url
        res_comment_serialized["username"] = res_comment.user.username
        return jsonify(result = res_comment_serialized)
    
    flash("Access unauthorized. You may only edit your own content.", "danger")
    return redirect(url_for('home'))

@app.route('/results/<int:result_id>/edit', methods=["GET", "POST"])
@check_logged_in
def edit_result(result_id):
    """Edit result."""

    result = Result.query.get_or_404(result_id)

    if result.user == g.user:

        form = ResultForm(obj=result)

        if form.validate_on_submit():
            result.score = form.score.data
            result.comment = form.comment.data
            result.date_completed = form.date_completed.data

            db.session.commit()
            return redirect(url_for('home'))

        return render_template('results/edit.html', form=form)

    flash("Access unauthorized. You may only edit your own content.", "danger")
    return redirect(url_for('home'))


@app.route('/results/<int:result_id>/delete', methods=["POST"])
@check_logged_in
def delete_result(result_id):
    """Delete result."""

    result = Result.query.get_or_404(result_id)

    if result.user == g.user:

        db.session.delete(result)
        db.session.commit()
        return redirect(url_for('home'))

    flash("Access unauthorized. You may only delete your own content.", "danger")
    return redirect(url_for('home'))

@app.route('/comments/<int:comment_id>/edit', methods=["GET", "POST"])
@check_logged_in
def edit_comment(comment_id):
    """Edit comment on a result."""

    res_comment = ResComment.query.get_or_404(comment_id)

    if res_comment.user == g.user:

        form = ResCommentForm(obj=res_comment)

        if form.validate_on_submit():
            res_comment.res_comment = form.res_comment.data
            db.session.commit()
            return redirect(url_for('home'))

        return render_template('results/edit.html', form=form)

    flash("Access unauthorized. You may only edit your own content.", "danger")
    return redirect(url_for('home'))

@app.route('/comments/<int:comment_id>/delete', methods=["POST"])
@check_logged_in
def delete_comment(comment_id):
    """Delete comment on a result."""

    res_comment = ResComment.query.get_or_404(comment_id)

    if res_comment.user == g.user:

        db.session.delete(res_comment)
        db.session.commit()
        return redirect(url_for('home'))
    
    flash("Access unauthorized. You may only delete your own content.", "danger")
    return redirect(url_for('home'))


@app.route('/users/<int:user_id>')
@check_logged_in
def show_user(user_id):
    """Show profile information for a given user."""
    user = User.query.get(user_id)

    return render_template('users/profile.html', user=user)


@app.route('/users/log')
@check_logged_in
def show_log():
    """Show workout log for current user."""

    results = Result.query.filter(Result.user_id==g.user.id).order_by(Result.date_completed).all()
    print(results)
    result_dates = [result.date_completed.date() for result in results]
    result_dates = set(result_dates)
    result_dates = list(result_dates)
    result_dates.sort()

    results_by_date = []
    
    for date in result_dates:
        results = Result.query.filter(Result.user_id==g.user.id,
                                extract('month', Result.date_completed)==date.month,
                                extract('day', Result.date_completed)==date.day,
                                extract('year', Result.date_completed)==date.year).all()

        results_by_date.append({"date": date, "results": results})

    return render_template('users/log.html', results_by_date=results_by_date)

@app.route('/users/plan')
@check_logged_in
def show_plan():
    """Show workout plan for current user."""

    cal = calendar.Calendar()
    weekList = cal.monthdatescalendar(TODAY.year, TODAY.month)

    week_num = 0
    for week in weekList:
        if TODAY in week:
            break
        week_num += 1

    week_log = []
    for weekday in weekList[week_num]:
        workouts = Workout.query.filter(Workout.family_id == g.user.primary_family_id, 
                                extract('month', Workout.date_posted) == weekday.month,
                                extract('day', Workout.date_posted) == weekday.day,
                                extract('year', Workout.date_posted) == weekday.year).order_by(Workout.primary.desc()).all()
        log = {'day' : weekday, 'workouts' : workouts}
        week_log.append(log)

    return render_template('users/plan.html', week_log=week_log)


@app.route('/families/<int:family_id>/admin')
@check_logged_in
def make_plan(family_id):
    """Show admin view of workout plan."""
    if g.user.role == 'admin' and g.user.primary_family_id==family_id:

        cal = calendar.Calendar()
        weekList = cal.monthdatescalendar(TODAY.year, TODAY.month)

        week_num = 0
        for week in weekList:
            if TODAY in week:
                break
            week_num += 1

        week_log = []
        for weekday in weekList[week_num]:
            workouts = Workout.query.filter(Workout.family_id == g.user.primary_family_id, 
                                    extract('month', Workout.date_posted) == weekday.month,
                                    extract('day', Workout.date_posted) == weekday.day,
                                    extract('year', Workout.date_posted) == weekday.year).order_by(Workout.primary.desc()).all()
            log = {'day' : weekday, 'workouts' : workouts}
            week_log.append(log)

        return render_template('admin/plan.html', week_log=week_log)
    
    flash("Admin access only.", 'danger')
    return redirect(url_for('home'))


@app.route('/workouts/<int:workout_id>/delete', methods=["POST"])
@check_logged_in
def delete_workout(workout_id):
    """Allow admin to delete a family's workout."""
    workout = Workout.query.get_or_404(workout_id)

    if g.user.role == 'admin' and g.user.primary_family_id==workout.family_id:
        db.session.delete(workout)
        db.session.commit()
        return redirect(url_for('make_plan', family_id=g.user.primary_family_id))

    flash("Admin access only.", 'danger')
    return redirect(url_for('home'))


@app.route('/workouts/<wo_date>/add', methods=["GET", "POST"])
@check_logged_in
def add_workout(wo_date):
    """Allow admin to add a workout."""

    if g.user.role == 'admin':

        wo_date = datetime.strptime(wo_date, '%Y-%m-%d').date()
        form = WorkoutAddForm(date_posted=wo_date)

        if form.validate_on_submit():

            workout = Workout(family_id=g.user.primary_family_id, title=form.title.data, description=form.description.data, primary=form.primary.data, score_type=form.score_type.data, date_posted=form.date_posted.data)
            db.session.add(workout)
            db.session.commit()
            return redirect(url_for('make_plan', family_id=workout.family_id))

        return render_template('admin/add.html', form=form, date=wo_date)
    
    flash("Admin access only.", 'danger')
    return redirect(url_for('home'))


@app.route('/workouts/add_from_db', methods=["POST"])
@check_logged_in
def add_workout_from_db():
    """Allow admin to add a workout from the database."""

    if g.user.role == 'admin':
        title = request.json.get('title')
        description = request.json.get('description')
        score_type = request.json.get('score_type')
        source = request.json.get('source')
        date = request.json.get('date')

        workout = Workout(family_id=g.user.primary_family_id, title=title, description=description, primary=True, score_type=score_type, source=source, date_posted=date)
        db.session.add(workout)
        db.session.commit()

        workout_serialized = workout.serialize()
        
        return jsonify(results=workout_serialized)

    flash("Admin access only.", 'danger')
    return redirect(url_for('home'))


@app.route('/workouts/<int:workout_id>/edit', methods=["GET", "POST"])
@check_logged_in
def edit_workout(workout_id):
    """Allow admin to edit a family's workout."""
    workout = Workout.query.get_or_404(workout_id)

    if g.user.role == 'admin' and g.user.primary_family_id==workout.family_id:

        form = WorkoutEditForm(obj=workout)

        if form.validate_on_submit():

            workout.title = form.title.data or workout.title
            workout.description = form.description.data or workout.description
            workout.date_posted = form.date_posted.data
            workout.primary = form.primary.data
            workout.score_type = form.score_type.data
    
            db.session.commit()
            return redirect(url_for('make_plan', family_id=workout.family_id))
            
        return render_template('admin/edit.html', form=form)
    
    flash("Admin access only.", 'danger')
    return redirect(url_for('home'))


@app.route('/users/edit', methods=["GET", "POST"])
@check_logged_in
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
                family = Family(name=f"{form.username.data}-ind")
                db.session.add(family)
                user.families.append(family)
                user.role = 'admin'
                user.primary_family_id = family.id
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
@check_logged_in
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



@app.route('/workouts')
@check_logged_in
def search_workouts():
    """Search workout database."""
    search_by_title = request.args.get('q')
    search_by_date = request.args.get('date')

    if search_by_title:
        workouts = Workout_from_db.query.filter(Workout_from_db.title.ilike(f"%{search_by_title}%")).all()

    if search_by_date:
        workouts = Workout_from_db.query.filter(Workout_from_db.date == search_by_date, Workout_from_db.source == 'slate').all()

        if not workouts:
            workouts =[]
            url = SUGARWOD_BASE_URL + '/workouts'
            response = requests.get(url, params= {"apiKey": API_KEY, "dates": search_by_date})
            workout_list = response.json().get('data')

            if workout_list:
                for workout in workout_list:
                    wo_info = workout.get("attributes")
                    wo = Workout_from_db(title=wo_info['title'], description=wo_info['description'], score_type=wo_info['score_type'], source='slate', date=wo_info['scheduled_date'])
                    db.session.add(wo)
                db.session.commit()
        
                workouts.append(wo)

    if workouts:
        workouts_serialized = [workout.serialize() for workout in workouts]

    else:
        workouts_serialized = []
    
    return jsonify(results=workouts_serialized)








