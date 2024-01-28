from flask import Flask, Blueprint, render_template, request, redirect, flash, session, g, jsonify
from forms import LoginForm, AddUserForm
from models import db, connect_db, User, Game, Guess, Word, bcrypt
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint('auth', __name__)
CURR_USER_KEY = "curr_user"

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id



def do_logout():
    """Logout user."""

    db.session.delete(g.user)

    if CURR_USER_KEY in session:

        del session[CURR_USER_KEY] 




@auth_bp.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None


@auth_bp.route('/')
def home_page():
    """ Home page. If user is logged in, redirect to game. """

    if g.user:
      return redirect('/start')

    return render_template('index.html')        


@auth_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    """ Login form. """

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
          session['curr_user'] = user.id
          return redirect('/start')
        else:
          flash('Invalid login. Please try again.')

    return render_template('login.html', form=form)




@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
  """ Create an account."""

  form = AddUserForm()

  if form.validate_on_submit():
    first_name = form.first_name.data
    username = form.username.data
    password = form.password.data
    hashed_password = bcrypt.generate_password_hash(password).decode('UTF8')
    
    try:
      user = User.signup(first_name=first_name, 
                      username=username,
                      password=hashed_password, 
                      highest_score=0)
      db.session.add(user) 
      db.session.commit()

      g.user = user
      session['curr_user'] = user.id
      flash(f'Hello, {user.first_name}, thanks for joining.')    

      return redirect('/start')

    except IntegrityError:
      db.session.rollback()
      flash('Username is already taken. Please choose a different username.', 'error')
 
  return render_template('signup.html', form=form)



@auth_bp.route('/logout')
def logout():
  del session['attemptsRemaining']
  do_logout()

  return redirect('/')