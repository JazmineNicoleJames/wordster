from flask import Flask, render_template, request, redirect, flash
import requests
from wonderwords import RandomWord
import secret
from models import db, connect_db, User, Game, Guess, Word
""" from flask_debugtoolbar import DebugToolbarExtension """

app = Flask(__name__)

app.config['SECRET_KEY'] = 'itsmylittlesecretokay'
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS']=False
""" toolbar = DebugToolbarExtension(app) """

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///wordster'

connect_db(app)

with app.app_context():
    db.create_all()


api_key = secret.API_KEY_SERVICE

r = RandomWord()
word = r.random_words(1, word_min_length=5, word_max_length=5)[0]
print(word)


url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={api_key}'


response = requests.get(url)
print(response)



if response.status_code == 200:
  data = response.json()
  print(data)
  if data:
    if 'def' in data[0]:
      definition = data[0]['def'][0]['sseq'][0][0][1]
      print("**************")
      print(definition)
  




@app.route('/')
def home_page():
    return render_template('index.html', word=word)