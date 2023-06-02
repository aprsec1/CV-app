from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DateField, FormField, FieldList
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from CV.models import User
from CV import app, db

with app.app_context():
    db.create_all()


class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    #validation:
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken, please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already taken, please choose a different one.')


class PersonalForm(FlaskForm):
    first_name = StringField('First Name', validators=[Length(min=2, max=60)])
    last_name = StringField('Last Name', validators=[Length(min=2, max=60)])
    address = StringField('Address', validators=[Length(min=2, max=60)])
    birth_date = DateField('Birth Date', format='%Y-%m-%d')
    about = TextAreaField('About', validators=[Length(max=240)])
    submit = SubmitField('Add Info')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update profile picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    #validation:

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already taken, please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already taken, please choose a different one.')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class WorkExperienceForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired(), Length(min=2, max=100)])
    job_title = StringField('Job Title', validators=[DataRequired(), Length(min=2, max=100)])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d')
    #description = StringField('Description')
    submit = SubmitField('Add Experience')


class MultipleWorkExperienceForm(FlaskForm):
    work_experiences = FieldList(FormField(WorkExperienceForm), min_entries=1)
    submit = SubmitField('Submit')

class CertificationForm(FlaskForm):
    cert_name = StringField('Certification Name', validators=[DataRequired(), Length(min=2, max=100)])
    institution = StringField('Institution', validators=[DataRequired(), Length(min=2, max=100)])
    date_earned = DateField('Date Earned', format='%Y-%m-%d', validators=[DataRequired()])
    date_expired = DateField('Date Expired', format='%Y-%m-%d')
    submit = SubmitField('Add Certification')


class EducationForm(FlaskForm):
    institution_name = StringField('Institution Name', validators=[DataRequired(), Length(min=2, max=100)])
    degree = StringField('Degree', validators=[DataRequired(), Length(min=2, max=100)])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Add Education')

"""
def work_experience_form_factory(num_forms):
    work_experience_forms = []
    for i in range(num_forms):
        work_experience_forms.append(WorkExperienceForm())
    return work_experience_forms


def certification_form_factory(num_forms):
    certification_forms = []
    for i in range(num_forms):
        certification_forms.append(CertificationForm())
    return certification_forms


def education_form_factory(num_forms):
    education_forms = []
    for i in range(num_forms):
        education_forms.append(EducationForm())
    return education_forms

"""