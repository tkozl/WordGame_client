from engine import Player, Action, getKey
from network import Client, Answer, isRspCorrect
from time import sleep


def main() -> None:
    print('Loading database...')
    try:
        file = open('slowa.txt', 'r', encoding='utf-8')
        database = file.read()
        file.close()
    except Exception:
        print('Failed to load the database')
        exit(1)
    database = database.split('\n')

    try:
        # Saved servers
        # Format of servers.txt:
        # <server name>:<server ip>:<port>:<auth type (1-user and password in one message, 2-separate messsages)>:<optional-username>:<optional-password>
        file = open('servers.txt', 'r', encoding='utf-8')
        servers = file.read()
        file.close()
        servers = servers.split('\n')
        for i in range(0, len(servers)):
            servers[i] = servers[i].split(':')
    except Exception:
        servers = ''

    print('Success')
    
    ip, port, user, password = '', '', '', ''
    authType = 1
    if len(servers) > 0:
        print('\nPlease select the server')
        print("Type 'n' or 'n.' where 'n' is the server number and '.' (dot) means that saved credentials will be ignored")
        i = 0
        for server in servers:
            i += 1
            print(f'[{i}] {server[0]}\n    Address: {server[1]}:{server[2]}')
            if i == 9:
                break
        print(f'[{i+1}] Other')
        select = 0
        while select not in range(1, i + 2):
            anotherAuth = False
            select = input('Your choice: ')
            if len(select) == 2:
                if select[1] == '.':
                    anotherAuth = True
                select = select[0]
            try:
                select = int(select)
            except Exception:
                select = -1
        if select != i + 1:
            server = servers[select - 1]
            ip = server[1]
            port = int(server[2])
            if not anotherAuth:
                try:
                    user = server[4]
                    password = server[5]
                except Exception:
                    pass
            authType = int(server[3])
    
    if len(ip) == 0:
        ip = input('Server IP: ')
    if len(str(port)) == 0:
        port = int(input('Server port: '))
    if len(user) == 0:
        user = input('Username: ')
    if len(password) == 0:
        password = input('Password: ')
    client = Client(ip, port, user, password, authType)
    keyType = None

    def connect() -> int:
        i = 0
        print(f'Connecting to {ip}:{str(port)}...')
        while True:
            res, keyType = client.connect()
            if res == Answer.SUCCESS:
                print('Success')
                print('Key type:', keyType)
                break
            elif res == Answer.ERROR:
                print(f'Unknown error: {keyType}')
                input()
                exit(1)
            elif res == Answer.BAD_LOGIN:
                print('Authentication failed')
                input()
                exit(1)
            elif res == Answer.NO_CONNECTION:
                if i > 2:
                    print('Timeout. Trying again in 2 sec...')
                client.disconnect()
                i += 1
                sleep(2)
        return keyType
    
    def response() -> str:
        result = None
        rsp = ''
        while result != Answer.SUCCESS or len(rsp) == 0:
            result, rsp = client.listen()
            if result == Answer.NO_CONNECTION or len(rsp) == 0 and result != Answer.TIME_OUT:
                connect()
        i = 0
        while not isRspCorrect(rsp) and i < 4 or rsp == '':
            if rsp == 'EMPTY MESSAGE':
                rsp = ''
            i += 1
            result, arsp = client.listen()
            if result != Answer.SUCCESS:
                #print(rsp)
                return rsp
            elif arsp != 'EMPTY MESSAGE':
                rsp += arsp
        #print(rsp)
        return rsp
    
    def send(msg :str) -> None:
        result = False
        while not result:
            result = client.send(msg)
            if not result:
                connect()
    
    endSuc = True
    rsp = ' '
    while True:
        if endSuc:
            keyType = connect()
        print('\nWaiting for instructions from server...')
        isMask = False
        while not isMask:
            if endSuc:
                rsp = response()
            isMask, endSuc = True, True
            if rsp == '':
                isMask = False
                continue
            
            try:
                mask = rsp.split('\n')
            except Exception:
                mask = rsp
            mask = mask[0]
            for char in mask:
                if char not in ('1', '2', '3', '4'):
                    print(f'Unexpected response: \'{rsp}\' len: {len(rsp)}')
                    isMask = False
                    break
        
        print('\nReceived game data from server')
        print('Mask:', mask)
        print('Preparing the game...')
        key = getKey(keyType)
        player = Player(database, mask, key)
        print('Player ready. Number of matching words:', player.words.numberOfWords)
        a = 0
        
        endSuc = False
        while not endSuc:
            a += 1
            print('\nAttempt', a)

            decision = player.decision()
            send(decision)

            decision = decision.split('\n')
            if player.lastAction == Action.LETTER:
                print('Trying with letter', decision[1])
            elif player.lastAction == Action.WORD:
                print('Trying with word', decision[1])

            rsp = response()

            result = player.loadServerResponse(rsp)
            rsp = rsp.split('\n')
            if result == Answer.IGNORED:
                print('Request ignored by server')

            elif result == Answer.INCORRECT:
                print('Bad try')

            elif result == Answer.CORRECT:
                pos = 1
                for char in rsp[1]:
                    if char == '1':
                        print('Letter appears at position', pos)
                    pos += 1

            elif result == Answer.END:
                print('End of the game')
                endSuc = True
                break

            elif result == Answer.GUESSED:
                print('Guessed the word')
                endSuc = True
                break
            
            elif result == Answer.ERROR:
                print(f'Unknown error: {rsp}')
                break
            
            if not endSuc:
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

        if endSuc:
            print('\nThe correct answer is', player.correctWord)
            print(f'Score: {player.finalPoints} points')
        else:
            print('\nEnd of the game becouse of error')
        print('\n===================================================\n')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    input('\nPress Enter to exit...')
