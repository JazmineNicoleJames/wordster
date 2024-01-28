from flask import Flask, render_template, request, redirect, flash, session, g, jsonify
import requests
from routes.auth import auth_bp
from routes.game import game_bp
from models import db, connect_db, User, Game, Guess, Word, bcrypt
from dotenv import load_dotenv
import os


app = Flask(__name__)
app.register_blueprint(auth_bp)
app.register_blueprint(game_bp)

app.config['SECRET_KEY'] = 'itsmylittlesecretokay'
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS']=False

database_url = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url

connect_db(app)

with app.app_context():
    db.create_all()


app.app_context().push()


if __name__ == '__main__':
    app.run(debug=True)