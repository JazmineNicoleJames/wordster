from app import app, db, check_correct_indices, check_existing_letters, session
from unittest import TestCase
from flask import Flask, request, redirect, jsonify
from models import User, Game, Word, Guess
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///wordster' 



class WordleTestCase(TestCase):

    def setUp(self):

        self.app = app.test_client()
        db.create_all()

        self.test_user = User(first_name = 'Testttt',
                            username = 'T',
                            password = 'testing')
        db.session.add(self.test_user)
        
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


    def test_signup(self):
        """ Test signing up a new user. """

        with app.test_client() as client:
            res = client.post('/signup', 
            data = dict(first_name = 'Jazzzzzzzzzzz',
                        last_name = 'James',
                        username = 'jazzzzzzzjam',
                        password = 'testpw',
                        follow_redirects=True))

            self.assertEqual(res.status_code, 200)
            
    def test_signup_fail(self):
        """ Test if signing up properly fails. """

        with app.test_client() as client:
            res2 = client.post('/signup',
            data = dict(first_name = 'Jaz',
                        last_name = 'James',
                        username = 'jazzzzzzzjam',
                        password = 'testing',
                        follow_redirects=True))

            self.assertEqual(res2.status_code, 200)


    def test_login(self):
        """Test login."""
        
        with app.test_client() as client:
            res = client.get('/login',
            data =dict(username = 'T',
                        password = 'testing',
                        follow_redirects = True))        
            html = res.get_data(as_text = True)

            self.assertEqual(res.status_code, 200)

    def test_login_fail(self):
        """ Test if the login is incorrect, it will inform."""

        with app.test_client() as client:
            res = client.get('/login',
            data =dict(username = 'falalalalalala',
                        password = 'testing',
                        follow_redirects = True)) 

            self.assertEqual(res.status_code, 200)

    def test_get_word(self):
        """ Test generating a random word. """

        with app.test_client() as client:
            res = client.get('/get_word')
            data = res.get_json()

            self.assertEqual(res.status_code, 200)
            self.assertIn('wordToGuess', data)


    def test_start_game(self):
        """ Test starting a game. """

        with app.test_client() as client:
            headers = {'Accept': 'application/json'}
            res = client.get('/start', headers=headers)
            
            self.assertEqual(res.status_code, 200)

    
    def test_check_correct_indices(self):
        """ Test that correct indices returns the correct indices of the word guessed compared to target word. """
       
        final_word = 'chair'
        word = 'chair'
        current_guess_idx = 0
        score = 13
        guessKey = 0
        result = check_correct_indices(final_word, word, current_guess_idx)
        
        self.assertEqual(result, [0, 1, 2, 3, 4])


    def test_check_existing_letters(self):
        """ Test that the existing letters returns the letters that exist in the guessed word compared to the word to target word. """

        final_word = 'chair'
        word = 'chair'
        current_guess_idx = 0
        result = check_existing_letters(final_word, word, current_guess_idx)
      
        self.assertEqual(result, [0, 1, 2, 3, 4])


    def test_check_correct_word(self):
        """ Test route checking word that is correct. """

        with app.test_client() as client:
            with client.session_transaction() as session:
                session['status'] = 'active'
                session['word'] = 'chair'
                session['final_word'] = 'chair'
                session['current_guess_idx'] = 1
                session['score'] = 13 
                session['guessKey'] = 0
                session['guesses_dict'] = {}
                guessKey = session.get('guessKey')
                guesses_dict = session.get('guesses_dict')

                guesses_dict[guessKey] =  {'word': 'chair',
                                'correct_indices': [0, 1, 2, 3, 4],
                                'existing_letters': [0, 1, 2, 3, 4]}               
            
            data ={
                    'finalWord': 'chair', 
                    'word': 'chair',
                    'score': 13,
                    'guessesKey': guessKey,
                    'current_guess_idx': 1
            }

            response = client.post('/check_word', json = data)
            result = response.get_json()

            self.assertEqual(response.status_code, 200)


    def test_check_wrong_word(self):
        """ Test route checking word that has no correct indices or existing letters. """

        with app.test_client() as client:
            with client.session_transaction() as session:
                session['status'] = 'active'
                session['word'] = 'chair'
                session['final_word'] = 'bents'
                session['current_guess_idx'] = 1
                session['score'] = 13 
                session['guessKey'] = 1
                session['attemptsRemaining'] = 5
                session['guesses_dict'] = {}

                guessKey = session.get('guessKey')
                attemptsRemaining = session.get('attemptsRemaining')
                guessKey = session.get('guessKey')
                guesses_dict = session.get('guesses_dict')
                
                guesses_dict[guessKey] =  {'word': 'bents',
                                'correct_indices': [],
                                'existing_letters': []}                

            data ={
                    'finalWord': 'bents', 
                    'word': 'chair',
                    'score': 13,
                    'guessesKey': guessKey,
                    'current_guess_idx': 1,
                    'attemptsRemaining': attemptsRemaining - 1
            }

            response = client.post('/check_word', json = data)
            result = response.get_json()
            html = response.get_data(as_text = True)


            self.assertEqual(response.status_code, 200)
            self.assertIn('"solved": false', html)
            self.assertIn('"attemptsRemaining": 4', html)


    def test_end_game(self):
        """ Testing the end of game. """

        with app.test_client() as client:
            with client.session_transaction() as session:        
                session['score'] = 0
                session['definition'] = 'example definition'
                session['correct_indices'] = [0, 1, 2, 3, 4]
                session['word'] = 'words'

        response = client.post('/end-game')
        data = response.get_json()

        self.assertEqual(response.content_type, 'application/json')




    def tearDown(self):

        db.session.remove()
        sql = text('DROP TABLE IF EXISTS "user" CASCADE')
        db.session.execute(sql)
        db.session.commit()
