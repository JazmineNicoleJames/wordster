from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import Column, Integer, String, ForeignKey

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    """ User information. """
    __tablename__ = 'users'

    id = db.Column(db.Integer,
                    primary_key = True,
                    autoincrement = True)

    first_name = db.Column(db.String(30),       
                            nullable = False)

    username = db.Column(db.String(30),
                        nullable = False,
                        unique = True)

    password = db.Column(db.Text,
                        nullable=False)

    highest_score = db.Column(db.Integer, default = 0)


    @classmethod 
    def signup(cls, first_name, username, password, highest_score):

        hashed = bcrypt.generate_password_hash(password).decode('UTF8')
        print('hashed', hashed)
        user = User(first_name=first_name, 
                    username=username.lower(), 
                    password=hashed,
                    highest_score=0
                    )
        
        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.
        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:

            is_auth = bcrypt.check_password_hash(user.password, password)

            return user

        return None


class Word(db.Model):
    """ Words each game has. """

    __tablename__ = 'words'

    id = db.Column(db.Integer,
                    primary_key = True,
                    autoincrement = True)
    
    word = db.Column(db.Text)

    definition = db.Column(db.String)




class Game(db.Model):
    """ Game that users can play. """
    __tablename__ = 'game'

    id = db.Column(db.Integer,
                        primary_key = True,
                        autoincrement = True)
    
    attempts_remaining = db.Column(db.Integer)

    words_guessed = db.Column(db.Text,
                                autoincrement = True)

    score = db.Column(db.Integer)

    


class Guess(db.Model):
    """ Guesses that each game has. """
    __tablename__ = 'guesses'

    id = db.Column(db.Integer,
                        primary_key = True,
                        autoincrement = True)
    
    word_guessed = db.Column(db.Text)

    correct_indices = db.Column(db.Integer,
                                autoincrement = True)
    
    existing_letters = db.Column(db.Integer,
                                autoincrement = True)



def connect_db(app):

    db.app = app
    db.init_app(app)