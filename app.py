from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['MONGO_URI'] = 'mongodb+srv://mohitrathod723:mohit99@cluster0.9xj2jcf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'

# Initialize MongoDB
client = MongoClient(app.config['MONGO_URI'])
db = client['web_application']
collection = db['app_data']

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    try:
        user = db.users.find_one({'_id': ObjectId(user_id)})  # Use ObjectId to fetch user
        if user:
            return User(user['_id'], user['username'], user['password'])
    except Exception as e:
        print(f"Error loading user: {e}")
    return None

class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class SignInForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

@app.route('/')
def index():
    return redirect(url_for('signin'))

@app.route('/hello')
@login_required
def hello():
    return render_template('hello.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        existing_user = db.users.find_one({'username': username})
        if existing_user:
            flash('Username already exists. Please use another username.')
            return redirect(url_for('signup'))
        db.users.insert_one({'username': username, 'password': password})
        flash('Account created successfully! Please log in.')
        return redirect(url_for('signin'))
    return render_template('signup.html', form=form)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SignInForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = db.users.find_one({'username': username})
        if user:
            if user['password'] == password:
                login_user(User(user['_id'], user['username'], user['password']))
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('hello'))
            else:
                flash('Incorrect username or password. Please try again.')
        else:
            flash('No user found. Please sign up first.')
    return render_template('signin.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('signin'))

if __name__ == '__main__':
    app.run(debug=True)
