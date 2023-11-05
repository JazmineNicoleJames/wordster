from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    """ User information. """
    ___tablename___ = 'users'

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

    highest_score = db.Column(db.Integer,
                            default = 0)

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.
        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Game(db.Model):
    """ Game that users can play. """
    ___tablename___ = 'game'

    id = db.Column(db.Integer,
                        primary_key = True,
                        autoincrement = True)

    word_id = db.Column(db.Integer,
                            db.ForeignKey('word.id'))

    user_id = db.Column(db.Integer,
                        db.ForeignKey('user.id'))
    
    attempts_remaining = db.Column(db.Integer)

    score = db.Column(db.Integer)

    user = db.relationship("User", backref="game")

    current_word = db.relationship("Word", backref="game")




class Guess(db.Model):
    """ Guesses that each game has. """
    ___tablename___ = 'guesses'

    id = db.Column(db.Integer,
                        primary_key = True,
                        autoincrement = True)

    game_id = db.Column(db.Integer,
                        db.ForeignKey('game.id'))
    
    word_guessed = db.Column(db.Text)

    correct_letters = db.Column(db.Integer,
                                autoincrement = True)
    
    correct_position = db.Column(db.Integer,
                                autoincrement = True)




class Word(db.Model):
    """ Words each game has. """

    ___tablename___ = 'words'

    id = db.Column(db.Integer,
                    primary_key = True,
                    autoincrement = True)
    
    word = db.Column(db.Text)

    definition = db.Column(db.String)


def connect_db(app):

    db.app = app
    db.init_app(app)