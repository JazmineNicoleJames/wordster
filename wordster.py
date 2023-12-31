from random import choice
import string 


class Wordster():

    """ def __init__(self, word):
        self.word = word """

    def make_board(self):
        """Make and return a board."""


        board = []

        for y in range(5):
            row = [" "," "," "," "," "," "]
            board.append(row)

        return board

    def check_correct_word(self, finalWord, word):

        word_exists = finalWord in self.word
        valid_word = self.find(board, word.upper())

        if word_exists and valid_word:
            result = 'ok'
        elif word_exists and not valid_word:
            result = 'not-on-board'
        else:
            result = 'not-word'

        return result
