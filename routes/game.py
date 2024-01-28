from flask import Flask, Blueprint, render_template, request, redirect, flash, session, g, jsonify
import requests
from wonderwords import RandomWord
from models import db, connect_db, User, Game, Guess, Word, bcrypt
from wordster import Wordster
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv('API_KEY')

game_bp = Blueprint('game', __name__)

r = RandomWord()

wordster = Wordster()


def setup_word_dict(final_word):

  word_dict = {}

  for char in final_word:
    word_dict[char] = word_dict.get(char, 0) + 1
  return word_dict
 


def check_correct_indices(final_word, word, current_guess_idx):
  return [(idx) for idx, (char, correct_char) in enumerate(zip(final_word, word)) if char == correct_char]



def check_existing_letters(final_word, word, current_guess_idx):
  return [(idx) for idx, char in enumerate(final_word) if char in word]

  

@game_bp.route('/start')
def start_game():
  """ Begin a game of Wordster."""

  users = User.query.all()
  random_word = get_random_word()
  print(random_word)

  try:
    session['guesses'] = []
    session['current_guess_idx'] = 0
    attempts_dict = session.get('attempts_dict', {'attempts_dict':[]})
    session['guesses_dict'] = {}
    session['attemptsRemaining'] = 6
    session['score'] = 12

    word = random_word
    word_split = [*word]
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={api_key}'


    session['word_split'] = word_split
    session['word'] = word

    board = wordster.make_board()

    session['board'] = board
    session['status'] = 'active'
    
    highest_score = session.get('highest_score', 0)
    user = session.get('user')
    
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
      
        if data:

          if 'def' in data[0] and 'dt' in data[0]['def'][0]['sseq'][0][0][1]:

            definition = data[0]['def'][0]['sseq'][0][0][1]['dt'][0]
            session['definition'] = definition

            return render_template('start.html', board=board, highest_score=highest_score, definition=definition, user=user, word=word, word_split=word_split)

    return redirect('/start')

  except Exception as e:
    print(f"An error occurred: {e}")
    flash("An error occurred. Please try again.")
    return redirect('/start')






def validate_word(word):
  url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={api_key}'
  response = requests.get(url)

  if response.status_code == 200:
    data = response.json()
    if word in response.text:
      return data
    else:
      return None
  else:
    return None

@game_bp.route('/validate_word', methods=['POST'])
def validate_word_route():
  """ Check if word(final_word) is a valid word in the dictionary. If not, do not submit word to be checked against target word."""

  data = request.get_json()
  final_word = data.get('finalWord')
  is_real_word = validate_word(final_word)

  if not is_real_word:
    return jsonify({'result': 'Invalid word. Please try again'})

  else:
   return jsonify({'isValid': is_real_word})


@game_bp.route('/check_word', methods=['GET','POST'])
def check_word():
  """ Check if a guessed word(final_word) matches the target word(word). """

  if session.get('status') == 'ended':
    return jsonify({'result':'Game has ended!'})

  data = request.get_json()
  word = session.get('word')
  final_word = data.get('finalWord')
  current_guess_idx = session.get('current_guess_idx')
  guesses_dict = session.get('guesses_dict')

  session['final_word'] = final_word

  correct_indices = check_correct_indices(final_word, word, current_guess_idx)
  session['correct_indices'] = correct_indices
  
  existing_letters = check_existing_letters(final_word, word, current_guess_idx)
  session['existing_letters'] = existing_letters
  
  session['incorrect_letters'] = []

  incorrect_letters = [char for idx, char in enumerate(final_word) if idx not in correct_indices and idx not in existing_letters]
  session['incorrect_letters'].extend(incorrect_letters)

  result = final_word == word
  
  final_word_split = [*final_word]
  word_length = len(final_word_split)

  if session['current_guess_idx'] < 30:
    guess_key = f'guess{current_guess_idx}'

    guesses_dict[guess_key] = {'word': final_word,
              'correct_indices': correct_indices,
              'existing_letters': existing_letters}

    session[guess_key] = guesses_dict[guess_key]
    possible_index = 5

    for i in range(0, possible_index, +1):
      guess_key = f'guess{i}'

      if guess_key in guesses_dict:
        session[guess_key] = guesses_dict[guess_key]

  else:
    print(f"Error: current_guess_idx ({current_guess_idx}) is out of range")
  

  guesses = session.get('guesses')
  session['current_guess_idx'] += 1

  correct_indices = session.get('correct_indices')
  if session['correct_indices']:
    correct_indices = [idx for idx in session['correct_indices']]

  definition = session.get('definition')
  status = session.get('status', 'active')
  guesses_dict = session.get('guesses_dict', {})

  for guessKey, guess in guesses_dict.items():
    session['guessKey'] = guessKey
    guessKey = session['guessKey']
    
    
  if status == 'active':

    score = session.get('score')
    guessKey = session.get('guessKey')

    if final_word == word:
        result = f'{final_word} is correct!'
        session['final_word'] = final_word
        session['score'] += 1

        if g.user:
          user = User.query.get(g.user.id)
          score = session.get('score')

          if score > user.highest_score:
            user.highest_score = score
            db.session.commit()

        response = ({'result':result, 
                    'solved': True, 
                    'score': session['score'], 
                    'definition': definition, 
                    'correct_indices': correct_indices,
                    'guessesKey': guessKey})    

    else:
      session['status'] = 'active'
      session['score'] -= 2
      session['attemptsRemaining'] -= 1

      attemptsRemaining = session['attemptsRemaining']

      result = "try again"

      response = ({'result':result, 
                  'solved': False, 
                  'score': session['score'], 
                  'word_to_guess': session['word'],
                  'definition': definition, 
                  'attemptsRemaining': attemptsRemaining,
                  'guesses': guesses_dict,
                  'correct_indices': correct_indices,
                  'existing_letters': existing_letters,
                  'current_guess_idx': session['current_guess_idx'],
                  'incorrect_letters': incorrect_letters 
                  })

  final_word = ''  

  return jsonify(response)


@game_bp.route('/end-game', methods=['GET', 'POST'])
def end_game():

  score = session.get('score')
  definition = session['definition']
  correct_indices = session['correct_indices']
  word = session.get('word')

  response = ({'score': score,
              'definition': definition,
              'correct_indices': correct_indices,
              'word': word})

  return jsonify(response)
  return "End of Game"



def get_random_word():

    word = r.random_words(1, word_min_length=5, word_max_length=5)[0]

    return word 