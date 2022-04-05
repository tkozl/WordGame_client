from engine import Player, generateMask, randomWord, getKey, randomWord
import time


# Testing effectiveness of alghoritm in the game.
# testSize is number of solo-games to play
def testPlayer(testSize :int, typeOfKey :int, comment='') -> None:
    file = open('slowa.txt', 'r', encoding='utf-8')
    database = file.read()
    file.close()
    database = database.split('\n')

    key = getKey(typeOfKey)

    avg = 0
    sum = 0
    sump = 0
    suc = 0
    timeouts = 0
    initDurSum = 0
    longestInit = 0
    total = 0
    for i in range(1, testSize + 1):
        word = randomWord(database)
        mask = generateMask(word, key)

        lastTime = time.time()

        player = Player(database, mask, key)

        points = 0
        a = 0
        while a < 10:
            a += 1
            total += 1

            decision = player.decision()

            dur = time.time() - lastTime
            if dur > 1.8:
                timeouts += 1
            if a == 1:
                initDurSum += dur
                if dur > longestInit:
                    longestInit = dur
            lastTime = time.time()

            decision = decision.split('\n')
            if decision[0] == '=':
                if decision[1] == word:
                    points += 5
                    resp = '=\n' + str(points) + '\n?'
                    player.loadServerResponse(resp)
                    suc += 1
                    break
                else:
                    resp = '!'
                    player.loadServerResponse(resp)
            elif decision[0] == '+':
                letter = decision[1]
                if letter in word:
                    pos = ''
                    for l in word:
                        if l == letter:
                            pos += '1'
                            points += 1
                        else:
                            pos += '0'
                    resp = '=\n' + pos
                    player.loadServerResponse(resp)
                else:
                    player.loadServerResponse('!')
            player.nextRound()
        
        sum += a
        avg = sum / i
        sump += points
        print('')
        print(comment)
        print('Words:', i)
        print('Average tries:', round(avg, 2))
        print('Average points:', round(sump / i, 2))
        print('The longest init time:', round(longestInit, 2), 'sec')
        print('Average init time:', round(initDurSum / i, 2), 'sec')
        print('Efficiency:', round(suc / i * 100, 2), '%')
        print('Timeouts:', timeouts, '/', total)


if __name__ == '__main__':
    try:
        testPlayer(1000, 1, 'if unknownChars <= 1 or numberOfWords < 5:')
    except KeyboardInterrupt:
        pass
