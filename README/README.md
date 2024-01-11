API = https://dictionaryapi.com/products/api-collegiate-dictionary

The title of my site is Wordster - https://wordster.onrender.com 

My site uses the python package Wonderwords to generate a random 5 letter word and also uses the dictionary API to get teh definition of the word.


Wordster is an educational word game where users have 6 tries to guess a 5 letter word. Users have the option to create an account to track their points, or they can play without logging in. 

If the user has created an account, there will be a welcome message and their highest score displayed.

The game board is set up as 6 rows with 5 empty boxes, with a keyboard beneath. As the user selects a letter, it will appear on the game board. Once one row is filled out and the user hits "Enter", the word will be submitted and each letter will be compared to the target word. If the guessed word and the target word match, the background color of the boxes will change green and the game will end. If the word is incorrect, but it has letters that exist in the same spot, the background of those boxes will change to green. If the letter exists in the word, but is in the incorrect spot, it will cahgne to orange. On the keyboard, each incorrectly guessed letters background will change to a purple- indicating that you have already guessed that letter. This logic repeats for each guess until the user runs out of guesses. At the end of the game, the keyboard will be removed and the definition of the word will appear.

