from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, RadioField, BooleanField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional


def contains_character(str, char_list):
    """Returns True if string str contains any of the characters in char_list"""
    for char in str:
        if char in char_list:
            return True
    return False

def illegal_character_check(form, field):
    """ValidationError raised if the field contains any illegal character"""

    illegal_characters = ['<', '>', '{', '}', '[', ']', '(', ')']

    if contains_character(field.data, illegal_characters):
        raise ValidationError(f"Special characters {(' ').join(illegal_characters)} not allowed in username.")

class SignupForm(FlaskForm):
    """Form for adding users."""

    username = StringField(
        'Username', 
        validators=[DataRequired(), Length(min=4, max=20), illegal_character_check]
    )

    email = StringField(
        'E-mail', 
        validators=[DataRequired(), Email(), Length(min=6, max=40), illegal_character_check]
    )

    password = PasswordField(
        'Password', 
        validators=[DataRequired(), Length(min=6, max=40), illegal_character_check]
    )

    first_name = StringField(
        'First Name', 
        validators=[DataRequired(), Length(min=1, max=30), illegal_character_check]
    )

    last_name = StringField(
        'Last Name', 
        validators=[DataRequired(), Length(min=1, max=30), illegal_character_check]
    )

    account_type = RadioField(
        "Account Type", 
        choices=[('ind', 'Individual'),  ('fam', 'Family')], 
        default='fam'
    )

    family_account_type = RadioField(
        "Family account type", 
        choices=[('existing', 'Join an Existing FitFam'),  ('new', 'Create a New FitFam')], 
        default='existing', 
        validators=[Optional()]
    )

    existing_family_name = StringField(
        'Existing FitFam name', 
        validators=[Length(min=4, max=25), Optional(), illegal_character_check]
    )
        
    new_family_name = StringField(
        'New FitFam name (no spaces)', 
        validators=[Length(min=4, max=25), Optional(), illegal_character_check]
    )


class ResultForm(FlaskForm):
    """Form for posting results."""

    score = StringField(
        'Score', 
        validators=[Optional(), Length(max=20), illegal_character_check]
    )

    comment = TextAreaField(
        'Comment', 
        validators=[Optional(), Length(max=400), illegal_character_check]
    )

    date_completed = DateField(
        'Date completed'    
    )

class ResCommentForm(FlaskForm):
    """Form for posting results."""

    res_comment = TextAreaField(
        'Comment', 
        validators=[DataRequired(), Length(max=400), illegal_character_check]
    )


class UserEditForm(FlaskForm):
    """Form for editing users."""

    username = StringField(
        'Username', 
        validators=[Length(min=4, max=20), illegal_character_check]
    )

    email = StringField(
        'E-mail', 
        validators=[Email(), Length(min=6, max=40), illegal_character_check]
    )

    first_name = StringField(
        'First Name', 
        validators=[Length(min=1, max=30), illegal_character_check]
    )

    last_name = StringField(
        'Last Name', 
        validators=[Length(min=1, max=30), illegal_character_check]
    )

    nickname = StringField(
        'Nickname', 
        validators=[Optional(), Length(min=1, max=20), illegal_character_check]
    )

    bio = TextAreaField(
        'Bio',
        validators=[Optional(), Length(max=200), illegal_character_check]
    )

    image_url = StringField(
        'Image URL',
        validators=[illegal_character_check]
    )

    account_type = SelectField(
        "Account Type", 
        choices=[('ind', 'Individual'),  ('fam', 'Family')], 
    )

    primary_family_id = SelectField(
        "Primary FitFam"
    )

    password = PasswordField(
        'Password', 
        validators=[DataRequired(), Length(min=6, max=40), illegal_character_check]
    )


class LoginForm(FlaskForm):
    """User login form."""

    username = StringField(
        'Username', 
        validators=[DataRequired(), Length(min=4, max=20), illegal_character_check]
    )

    password = PasswordField(
        'Password', 
        validators=[Length(min=6, max=40), illegal_character_check]
    )


class WorkoutAddForm(FlaskForm):
    """Form for adding workout."""

    # source = SelectField(
    #     'Workout source',
    #     choices = [('xx', 'Select a workout source...'), ('slate', 'Slate'), ('hq', 'Crossfit HQ'), ('self', 'Create your own')]
    # )

    title = StringField(
        'Title', 
        validators=[DataRequired(), Length(max=50)]
    )

    description = TextAreaField(
        'Description', 
        validators=[DataRequired(), Length(max=400)]
    )

    primary = BooleanField(
        'Primary workout',
        default = True
    )

    score_type = SelectField(
        'Score type',
        choices = [('Time', 'For Time'), ('Load', 'For Max Load'), ('Reps', 'For Max Reps'), ('Rounds + Reps', 'For Rounds plus Reps'), ('None', 'No score')],
        default = 'none'
    
    )

    date_posted = DateField(
        'Date'    
    )


class WorkoutEditForm(FlaskForm):
    """Form for editing workout."""

    title = StringField(
        'Title', 
        validators=[Length(max=50)]
    )

    description = TextAreaField(
        'Description', 
        validators=[Length(max=400)]
    )

    primary = BooleanField(
        'Primary workout'
    )

    score_type = SelectField(
        'Score type',
        choices = [('time', 'For Time'), ('Load', 'For Max Load'), ('Rounds + Reps', 'For Rounds plus Reps'), ('none', 'No score')]
    )

    date_posted = DateField(
        'Date'
    )



class ChangePasswordForm(FlaskForm):
    """Form for changing user password."""

    username = StringField(
        'Username', 
        validators=[DataRequired(), Length(min=4, max=20), illegal_character_check]
    )

    password = PasswordField(
        'OldPassword', 
        validators=[DataRequired(), Length(min=6, max=40), illegal_character_check]
    )

    newpassword1 = PasswordField(
        'New Password', 
        validators=[DataRequired(), Length(min=6, max=40), illegal_character_check]
    )

    newpassword2 = PasswordField(
        'New Password (confirm)', 
        validators=[DataRequired(), Length(min=6, max=40), EqualTo('newpassword1'), illegal_character_check]
    )

