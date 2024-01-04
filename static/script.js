const apiUrl = 'http://localhost:5000/get_word'
let wordToGuess;
let wordArr = [];
let wordsGuessed = [];
let availableSpace = 0;
const gameBoard = document.getElementById('gameBoard');
let definition;
let keyboardRows = document.getElementById('keyboard');



window.addEventListener('keydown', function(event) {

    const keyPressed = event.key.toLowerCase();
    /* if (/^[a-z]$/.test(keyPressed)) { */
        handleKeyPress(keyPressed);
   /*  } */
});

    
const keyboardBtns = document.querySelectorAll('#keyboard button');

keyboardBtns.forEach(function(btn) {
    btn.addEventListener('click', function() {

        const key = btn.getAttribute('data-key');
        handleKeyPress(key);

        return key;
    });
})


function handleKeyPress(key) {

    const del = document.getElementById('del');
    
    if(key === 'enter' && wordArr.length === 5){

        let finalWord = wordArr.join('').replace(/\s*,\s*/g, "");
        wordsGuessed.push(finalWord);   
        checkWord(finalWord);
        wordArr = [];

        if(wordsGuessed.length === 6) {
            endGame();
        } 
    }
    
    if(wordArr.length <= 5 && key !== 'enter') {

        if(key !== del) {
            updateWordsGuessedArr(key);
        }
    }
}


function updateWordsGuessedArr(key) {
 
    let availableSpaceEl = document.getElementById(String(availableSpace));

    if(key === 'backspace' || key === 'del') {

        if(Array.isArray(wordArr) && wordArr.length > 0) {
            
            wordArr.pop();

            availableSpace = Math.max(0, availableSpace -1);
            let availableSpaceEl = document.getElementById(String(availableSpace));
            availableSpaceEl.innerHTML = '';
            
            return availableSpaceEl; 
        }
    }

    if((wordArr.length < 5 && key !== 'backspace') && key !== 'del') {

        if(key !== 'enter'){

            wordArr.push(key);
            availableSpaceEl.textContent = key;
            availableSpace = availableSpace + 1;

            return availableSpaceEl;
        }     
    }   
       
}


async function checkWord(finalWord){

    try {
        const resp = await fetch('/check_word', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({finalWord: finalWord}),
        });

        if(!resp.ok) {
            throw new Error('ERROR');
        }

        const data = await resp.json();
        let guesses = data.guesses;
        attemptsRemaining = data.attemptsRemaining;
        score = data.score;
     

        let resultContainer = document.getElementById('result-container');

        for(let guessKey in guesses){
            let targetLettersCount = {};
            let targetWord = data.word_to_guess;
            console.log('targetWord', targetWord)
            
            targetWord.split('').forEach((letter, index) => {
                let divNum = index;
                let correctIdxEl = document.querySelector(`.index-${divNum}-${index}`);
                
                if(correctIdxEl) {
                    targetLettersCount[letter] = (targetLettersCount[letter] || 0) + 1;
                    console.log('targetletterscount', targetLettersCount)
                }
            });

            let guess = guesses[guessKey]

            handleCorrectIndices(guessKey, guess, targetLettersCount)            
            handleExistingLetters(guessKey, guess, targetLettersCount)

        }
        console.log('data',data)
        if(data.incorrect_letters) {
            data.incorrect_letters.forEach((index) => {
                console.log('index', index)
                incorrectLetter = index;
                let selector = `button[data-key="${index}"]`
                let keyboardLetter = document.querySelector(selector)
                keyboardLetter.classList.add('incorrect')

            })
        }
        if(data.solved) {   
            data.correct_indices.forEach((index) => {
                let divNum = data.guessesKey.substring(5)
                let selector = `.index-${divNum}-${index}`;
                changeBackgroundColor(selector, 'green');
            });

            resultContainer.innerHTML = data.result 
            
            let defDiv = document.getElementById('definitionDiv')
            let definition = data.definition[1]
            defDiv.innerHTML = `Definition: ${definition.replace(/\{[^,}]*\}/g, '')}`   
            keyboardRows.remove()
            endGame();

        } else {           
            resultContainer.innerHTML = data.result
        }
        
    if(data.attemptsRemaining > 0){
        return;
    } else {
        resultContainer.innerHTML = 'Game Over';
        keyboardRows.remove();
        endGame();
    }
 
    } catch (error) {
        console.error('ERROR', error)
    }            
}



function handleCorrectIndices(guessKey, guess, targetLettersCount) {
    if (guess.correct_indices) {
        guess.correct_indices.forEach((index) => {
            let divNum = guessKey.substring(5);
            let selector = `.index-${divNum}-${index}`;
            let corrLetterEl = document.querySelector(selector);

            if (corrLetterEl) {
                let guessedLetter = corrLetterEl.innerHTML;

                if (targetLettersCount[guessedLetter] > 0 && guess.existing_letters) {
                    console.log('targetletterscount', targetLettersCount)
                    changeBackgroundColor(selector, 'green');
                    targetLettersCount[guessedLetter]--;
                    console.log('CORRECTINDICEStargetletterscount', targetLettersCount)

                }
            }
        });
    }
}



function handleExistingLetters(guessKey, guess, targetLettersCount) {

    if (guess.existing_letters && guess.correct_indices) {
        const commonElements = guess.correct_indices.filter(index => guess.existing_letters.includes(index))

        guess.existing_letters.forEach((index) => {
            let divNum = guessKey.substring(5);
            let selector = `.index-${divNum}-${index}`;
            let letterEl = document.querySelector(selector);

            if(!commonElements.includes(index)){

            if (letterEl) {
                let guessedLetter = letterEl.innerHTML;

                if (targetLettersCount[guessedLetter] > 0) {
                    changeBackgroundColor(selector, 'orange');
                    targetLettersCount[guessedLetter]--;
                }
            }
        }
        });
    }
}



function changeBackgroundColor(selector, color) {

    document.querySelectorAll(selector).forEach((div => {
        div.style.backgroundColor = color;
    }));
}


function wordsGuessedArr() {

    let numOfWords = wordsGuessed.length;

    return wordsGuessed[numOfWords -1];
}


function createBoard() {

    const numberOfGuesses = 6;
    const indicesPerGuess = 5;

    for (let guess = 0; guess < numberOfGuesses; guess++) {

        for (let index = 0; index < indicesPerGuess; index++) {
            let letter = document.createElement('div');
            letter.classList.add('letter', `index-${guess}-${index}`);
            letter.setAttribute('id', guess * indicesPerGuess + index);
            gameBoard.appendChild(letter);
        }
    }
}

const banner = document.createElement('div');
banner.classList.add('end-game-banner');
const container = document.getElementById('gameBoard');


function endGameBannerFailed(word){
    banner.textContent = `correct word:  ${word}`
    container.appendChild(banner);
}

function endGameBannerSolved(word){
    banner.textContent = `${word} is correct!`
    container.appendChild(banner);
}

async function endGame() {

    res = await axios.post('/end-game', {definition:definition, score:score});
    let word = res.data.word;
    let currentScoreDiv = document.getElementById('currentScore')

    if(currentScoreDiv) {
        currentScoreDiv.textContent = `SCORE: ${res.data.score}`;
    }
    if(res.data.correct_indices.length === 5){
        endGameBannerSolved(word)
    }
    else {
        endGameBannerFailed(word);
    }

    return res;
}


document.addEventListener("DOMContentLoaded", () => {
    createBoard();
})
