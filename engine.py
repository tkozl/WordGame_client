# Classes and functions used to making decisions in the game
# ===============================================================

import random
from network import Answer
from enum import Enum

# ===============================================================

class Action(Enum):
    LETTER = 1
    WORD = 2

# ===============================================================

# Represents list of words. This class filter this list basing on pattern and offering functions designed to guess words
class Words:
    
    # Constructor selects words from database matching to pattern (mask).
    # mask is a string of numbers from range(1,4), where every number represents a group of letters for each word's char.
    # For expmple 132 means 3-letter word where first letter is from group 1, second letter from group three and the last from group two. Chars from each group are included in key[group-1]
    def __init__(self, database :list, mask :str, key :list) -> None:
        if len(key) != 4:
            raise ValueError('key must have 4 groups')
        for letter in mask:
            if letter not in ('1', '2', '3', '4'):
                raise ValueError('mask should only contains digits from range 1-4')
        
        self.__alphabet = key[0] + key[1] + key[2] + key[3]
        self.__length = len(mask)
        self.__word = mask
        self.__key = key
        self.__matched = []

        self.__avilableWords = []
        for word in database:
            if len(word) == self.len:
                match = False
                for i in range(0, self.len):
                    letter, group = word[i], int(mask[i])
                    if letter not in key[group - 1]:
                        match = False
                        break
                    match = True
                if match == True:
                    self.__avilableWords.append(word)
        if self.numberOfWords == 0:
            raise ValueError('mask doesn\'t match any word in database')


    @property
    def len(self) -> int:
        return self.__length
    

    @property
    def wordsList(self) -> list:
        return self.__avilableWords
    

    @property
    def key(self) -> str:
        return self.__key
    

    @property
    def word(self) -> list:
        return self.__word
    

    @property
    def numberOfWords(self) -> int:
        return len(self.__avilableWords)
    

    @property
    def unknownChars(self) -> int:
        unknown = 0
        for letter in self.__word:
            if letter in ('1', '2', '3', '4'):
                unknown += 1
        return unknown
    

    @property
    def isBetterToGuessWord(self) -> bool:
        unknownChars = self.unknownChars
        numberOfWords = self.numberOfWords
        if unknownChars <= 1 or numberOfWords < 4:
            return True
        else:
            return False
    

    # Simpy remove word from list
    def excludeWord(self, word :str) -> None:
        self.__avilableWords.remove(word)
    

    # Remove all words that contains specified char
    def excludeLetter(self, letter :str) -> None:
        if len(letter) != 1:
            raise ValueError('Expected a letter')
        newWords = []
        wordsList = self.wordsList
        for word in wordsList:
            if letter not in word:
                newWords.append(word)
        self.__avilableWords = newWords
    

    # Set the letter in the word using posKey. posKey is a string of 0/1 chars where 1 means that the letter should be placed in this position.
    # For example we have the letter 'k' and posKey=100100. It means that 'k' should be placed on first and fourth position in word.
    def setLetter(self, letter :str, posKey :str) -> None:
        if len(letter) != 1:
            raise ValueError('Expected a letter')
        if len(posKey) != self.len:
            raise ValueError(f'Bad posKey len.\nposKey = {posKey}\nlen(posKey) = {len(posKey)} (expected: {self.len})')
        
        p = []
        for i in range(0, self.len):
            if posKey[i] == '1':
                p.append(i)
        
        for pos in p:
            if pos != self.len - 1:
                self.__word = self.__word[:pos] + letter + self.__word[(pos + 1):]
            else:
                self.__word = self.__word[:pos] + letter

        # Filter the list of words using new knowledge
        newWords = []
        wordsList = self.wordsList
        for word in wordsList:
            match = True
            for pos in p:
                if word[pos] != letter:
                    match = False
                    break
            if match == True:
                newWords.append(word)
        self.__avilableWords = newWords
        self.__matched.append(letter)
    

    # Choose the best letter to guess in actual situation.
    # If prob is set to True, alghoritm'll choose a letter witch the highest probability. In other case alghoritm'll try to choose the most tactical letter to exclude some words.
    def chooseLetter(self, prob = False) -> str:
        # Calculating frequency of occurrences for each letter from a game's alphabet
        freq = {} # dictionary freq means number of words containing letter from index
        freqAll = {} # means all occurrences of a char in available words
        for letter in self.__alphabet:
            freq[letter] = 0
            freqAll[letter] = 0
        for word in self.__avilableWords:
            done = []
            for letter in word:
                if letter not in self.__matched:
                    freqAll[letter] += 1
                    if letter not in done:
                        freq[letter] += 1
                    done.append(letter)

        # Choosing the best letter
        amount = self.numberOfWords
        occur = -1
        bestLetter = ''
        altLetter = ''
        for letter in freq:
            if prob:
                if freq[letter] > occur:
                    bestLetter, occur = letter, freq[letter]
            elif freqAll[letter] > occur:
                if freq[letter] == amount:
                    altLetter = letter
                else:
                    bestLetter, occur = letter, freqAll[letter]
        if len(bestLetter) != 0:
            return bestLetter
        else:
            return altLetter

# ===============================================================

# Represents player and supports making decisions about the game
class Player:

    def __init__(self, database :list, mask :str, key :list, rounds = 10) -> None:
        self.__words = Words(database, mask, key)
        self.__finalPoints = -1
        self.__correctWord = ''
        self.__round = 1
        self.__theLastRound = rounds
    

    @property
    def round(self) -> int:
        return self.__round


    @property
    def words(self) -> Words:
        return self.__words
    

    @property
    def lastAction(self) -> Action:
        return self.__lastAction
    

    @property
    def lastGuess(self) -> str:
        return self.__lastGuess
    

    @property
    def finalPoints(self) -> int:
        return self.__finalPoints
    

    @property
    def correctWord(self) -> str:
        return self.__correctWord
    

    def nextRound(self) -> None:
        self.__round += 1
    

    # Returns request that should be send to game server
    def decision(self) -> str:
        if self.words.isBetterToGuessWord == True:
            guess = random.choice(self.words.wordsList)
            self.__lastGuess = guess
            self.__lastAction = Action.WORD
            return '=\n' + guess + '\n'
        else:
            prob = False
            if self.round >= self.__theLastRound:
                prob = True
            letter = self.words.chooseLetter(prob)
            self.__lastGuess = letter
            self.__lastAction = Action.LETTER
            return '+\n' + letter + '\n'
    

    # Interprets server responses
    def loadServerResponse(self, answer :str) -> Answer:
        answer = answer.split('\n')
        if answer[0] == '?':
            self.__correctWord = '--unknown--'
            self.__finalPoints = self.words.len - self.words.unknownChars
            return Answer.END

        if answer[-1] == '' and len(answer) > 1:
            answer = answer[:-1]
        
        if answer[0] == '=':
            if len(answer) == 1:
                return Answer.ERROR
            if '?' in answer:
                try:
                    self.__finalPoints = int(answer[1])
                except Exception:
                    return Answer.ERROR
                if self.lastAction == Action.WORD:
                    self.__correctWord = self.lastGuess
                else:
                    correctWord = self.words.word
                    self.__correctWord = ''
                    for letter in correctWord:
                        if letter in ('1', '2', '3', '4'):
                            self.__correctWord += self.lastGuess
                        else:
                            self.__correctWord += letter
                return Answer.GUESSED
            elif self.lastAction == Action.LETTER:
                self.words.setLetter(self.lastGuess, answer[1])
                return Answer.CORRECT
            else:
                return Answer.ERROR
        
        elif answer[0] == '!':
            if self.lastAction == Action.WORD:
                self.words.excludeWord(self.lastGuess)
            elif self.lastAction == Action.LETTER:
                self.words.excludeLetter(self.lastGuess)
            return Answer.INCORRECT
        
        elif answer[0] == '#':
            return Answer.IGNORED
        
        else:
            if len(answer) < 3 or '?' not in answer:
                return Answer.ERROR
            self.__correctWord = answer[0]
            try:
                self.__finalPoints = int(answer[1])
            except Exception:
                return Answer.ERROR
            return Answer.END

# ===============================================================

# Returns one of keys using in game
def getKey(type :int) -> list:
    if type not in (1, 2):
        raise ValueError('Unsupported key type')
    
    key = []

    if type == 1:
        key.append(['w', 'e', 'ę', 'r', 'u', 'i', 'o', 'ó', 'a', 'ą', 's', 'ś', 'z', 'ż', 'ź', 'x', 'c', 'ć', 'v', 'n', 'ń', 'm'])
        key.append(['p', 'y', 'j', 'g', 'q'])
        key.append(['t', 'l', 'ł', 'b', 'd', 'h', 'k'])
        key.append(['f'])
    
    if type == 2:
        key.append(['a', 'c', 'e', 'm', 'n', 'o', 'r', 's', 'u', 'w', 'z', 'x', 'v'])
        key.append(['ą', 'ę', 'g', 'j', 'p', 'y', 'q'])
        key.append(['b', 'ć', 'd', 'h', 'k', 'l', 'ł', 'ń', 'ó', 'ś', 't', 'ź', 'ż', 'i'])
        key.append(['f'])
    
    return key

# ===============================================================

def randomWord(database :list) -> str:
    word = ''
    while len(word) < 5:
        word = random.choice(database)
    return word

# ===============================================================

# Generates mask using in class Words basing on word
def generateMask(word :str, key :list) -> str:
    mask = ''
    for letter in word:
        if letter in key[0]:
            mask += '1'
        elif letter in key[1]:
            mask += '2'
        elif letter in key[2]:
            mask += '3'
        elif letter in key[3]:
            mask += '4'
        else:
            err = letter
            err += ' doesn\'t appear in key'
            raise ValueError(err)
    return mask
