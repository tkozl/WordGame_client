from engine import Player, generateMask, randomWord, getKey, randomWord


def main() -> None:
    file = open('slowa.txt', 'r', encoding='utf-8')
    database = file.read()
    file.close()
    database = database.split('\n')

    key = getKey(1)

    print('Starting the game')
    word = randomWord(database)
    mask = generateMask(word, key)
    print('Mask:', mask)

    player = Player(database, mask, key)
    print('Class ready. Number of matching words:', player.words.numberOfWords)

    points = 0
    a = 0
    while a < 10:
        a += 1
        print('\nAttempt', a)

        decision = player.decision()
        decision = decision.split('\n')
        if decision[0] == '=':
            print('Trying with word', decision[1])
            if decision[1] == word:
                print('\nGuessed after', a, 'tries')
                points += 5
                resp = '=\n' + str(points) + '\n?'
                player.loadServerResponse(resp)
                break
            else:
                resp = '!'
                player.loadServerResponse(resp)
                print('Bad try')
        elif decision[0] == '+':
            letter = decision[1]
            print('Trying with letter', letter)
            if letter in word:
                index = -1
                pos = ''
                for l in word:
                    index += 1
                    if l == letter:
                        pos += '1'
                        print('Letter appears at position', index)
                        points += 1
                    else:
                        pos += '0'
                resp = '=\n' + pos
                player.loadServerResponse(resp)
            else:
                print('Letter doesn\'t appear')
                player.loadServerResponse('!')
        actWord = ''
        for l in player.words.word:
            if l in ('1', '2', '3', '4'):
                actWord += '_'
            else:
                actWord += l
        print('Actual word:', actWord)
        print('Actual mask:', player.words.word)
        print('Number of matching words:', player.words.numberOfWords)
        player.nextRound()
    
    print('\nThe correct answer is', word)
    print('Points:', points)


if __name__ == '__main__':
    main()
