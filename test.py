import unittest
from engine import Words, Player, generateMask, getKey
from network import Answer, isRspCorrect, standardizeRsp


class Test_words(unittest.TestCase):

    def setUp(self):
        file = open('slowa.txt', 'r', encoding='utf-8')
        database = file.read()
        file.close()
        database = database.split('\n')
        self.word = 'narkobiznes'
        self.key = getKey(1)
        self.mask = generateMask(self.word, self.key)
        self.words = Words(database, self.mask, self.key)
    
    def test_wordsPattern(self):
        database = self.words.wordsList
        for word in database:
            self.assertEqual(len(word), self.words.len)
            for i in range(0, self.words.len):
                letter, group = word[i], int(self.mask[i])
                self.assertTrue(letter in self.key[group - 1])
        self.assertTrue(self.word in database)
    
    def test_setLetter(self):
        size = self.words.numberOfWords
        self.words.setLetter('r', '00100000000')
        self.assertTrue(self.words.numberOfWords < size)
        database = self.words.wordsList
        for word in database:
            self.assertEqual(word[2], 'r')
        self.assertTrue(self.word in database)


class Test_generateMask(unittest.TestCase):

    def test_mask(self):
        for i in 1, 2:
            key = getKey(i)

            file = open('slowa.txt', 'r', encoding='utf-8')
            allWords = file.read()
            file.close()
            allWords = allWords.split('\n')
            i = 0
            for word in allWords[:500]:
                i += 1
                mask = generateMask(word, key)
                self.assertEqual(len(mask), len(word))
                for char in mask:
                    self.assertTrue(char in ('1', '2', '3', '4'))


class Test_Player(unittest.TestCase):

    def setUp(self):
        file = open('slowa.txt', 'r', encoding='utf-8')
        self.database = file.read()
        file.close()
        self.database = self.database.split('\n')
        self.word = 'narkobiznes'
        self.key = getKey(1)
        self.mask = generateMask(self.word, self.key)
    
    def test_decision(self):
        player = Player(['narkobiznes'], self.mask, self.key)
        self.assertEqual(player.decision(), '=\nnarkobiznes\n')
        player = Player(self.database, self.mask, self.key)
        decision = player.decision()
        self.assertEqual(decision[:2], '+\n')
        self.assertEqual(len(decision), 4)
    
    def test_loadServerResponse(self):
        player = Player(self.database, self.mask, self.key)
        player.decision()
        response = '?\n'
        self.assertEqual(player.loadServerResponse(response), Answer.END)
        response = '#\n'
        self.assertEqual(player.loadServerResponse(response), Answer.IGNORED)
        response = '!\n'
        self.assertEqual(player.loadServerResponse(response), Answer.INCORRECT)
        response = '=\n00000000000\n'
        self.assertEqual(player.loadServerResponse(response), Answer.CORRECT)
        response = '='
        self.assertEqual(player.loadServerResponse(response), Answer.ERROR)
        response = '=\n10\n?'
        self.assertEqual(player.loadServerResponse(response), Answer.GUESSED)
        self.assertEqual(player.finalPoints, 10)
        self.assertEqual(player.correctWord, player.lastGuess * len('narkobiznes'))
        response = 'abc\n123\n?'
        self.assertEqual(player.loadServerResponse(response), Answer.END)
        player = Player(['narkobiznes'], self.mask, self.key)
        player.decision()
        response = '=\n10\n?'
        self.assertEqual(player.loadServerResponse(response), Answer.GUESSED)
        self.assertEqual(player.finalPoints, 10)
        self.assertEqual(player.correctWord, 'narkobiznes')


class Test_isRspCorrect(unittest.TestCase):

    def test_correctResponse(self):
        rsp = '+1\n'
        self.assertTrue(isRspCorrect(rsp))
        rsp = '+2\n'
        self.assertTrue(isRspCorrect(rsp))
        rsp = '-\n'
        self.assertTrue(isRspCorrect(rsp))

        rsp = '121311114111\n'
        self.assertTrue(isRspCorrect(rsp))
        rsp = '121311114111'
        self.assertTrue(isRspCorrect(rsp))

        rsp = '!\n'
        self.assertTrue(isRspCorrect(rsp))

        rsp = '?\n'
        self.assertTrue(isRspCorrect(rsp))

        rsp = '#\n'
        self.assertTrue(isRspCorrect(rsp))

        rsp = '=\n110110\n'
        self.assertTrue(isRspCorrect(rsp))
        rsp = '=\n110110'
        self.assertTrue(isRspCorrect(rsp))

        rsp = '=\n15\n?\n'
        self.assertTrue(isRspCorrect(rsp))

        rsp = 'slowo\n13\n?\n'
        self.assertTrue(isRspCorrect(rsp))
    
    def test_incorrectResponse(self):
        rsp = '+3\n'
        self.assertFalse(isRspCorrect(rsp))

        rsp = '=\n120110\n'
        self.assertFalse(isRspCorrect(rsp))

        rsp = '=\n'
        self.assertFalse(isRspCorrect(rsp))

        rsp = 'slowo\n13\n'
        self.assertFalse(isRspCorrect(rsp))
    

class Test_standardizeRsp(unittest.TestCase):

    def test_standardizeRsp(self):
        self.assertEqual(standardizeRsp('a\0b\0c\n'), 'a\nb\nc\n')
        self.assertEqual(standardizeRsp('\0\0abc\0'), 'abc\n')
        self.assertEqual(standardizeRsp('\0\0\0'), 'EMPTY MESSAGE')
        self.assertEqual(standardizeRsp('\n\n\n'), 'EMPTY MESSAGE')
        

if __name__ == '__main__':
    unittest.main()
