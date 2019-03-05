from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField,SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo,ValidationError
from flaskvm.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Demo')
    basic = SubmitField('Basic')
    pro = SubmitField('Pro')
    premium = SubmitField('Premium')

    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username taken')
    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('email already registered')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')



class UpdateAccountForm(FlaskForm):
    username = StringField('Username:',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email:',
                        validators=[DataRequired(), Email()])
    plan = SelectField('Select Plan:', choices = [('basic', 'BASIC'),('pro', 'PRO'),('premium', 'PREMIUM')])
    
    picture = FileField('Update Profile Picture:', validators=[FileAllowed(['jpg', 'png'])])

    submit = SubmitField('Update')
    submit_plan = SubmitField('Upgrade Plan')

    def validate_username(self,username):
        if username.data!=current_user.username :
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username taken')
    def validate_email(self,email):
        if email.data!=current_user.email :
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('email already registered')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')


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


class GetReportForm(FlaskForm):
    brand = SelectField('Brands', choices = [('xiaomi', 'Xiaomi'),('samsung', 'Samsung'),('nokia', 'Nokia'),('vivo','Vivo'),('oppo','Oppo')])
    location = StringField('Location',validators=[DataRequired()])
    submit1 = SubmitField("Get Report")
