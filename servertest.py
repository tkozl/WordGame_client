import socket

if __name__ == '__main__':
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 8888))          
    s.listen(5)
    clt,adr=s.accept()
    print(f"Connection to {adr} established")
    msg = clt.recv(1024)
    print(msg.decode('utf-8'))
    clt.send(bytes("+1","utf-8"))
    input()
    clt.send(bytes("11111","utf-8"))
    msg = clt.recv(1024)
    print(msg.decode('utf-8'))
    clt.send(bytes("=\n10000","utf-8"))
    msg = clt.recv(1024)
    print(msg.decode('utf-8'))
    clt.send(bytes("=\n01000","utf-8"))
    msg = clt.recv(1024)
    print(msg.decode('utf-8'))
    clt.send(bytes("=\n00100","utf-8"))
    msg = clt.recv(1024)
    print(msg.decode('utf-8'))
    clt.send(bytes("=\n00010","utf-8"))
    msg = clt.recv(1024)
    print(msg.decode('utf-8'))
    clt.send(bytes("!","utf-8"))
    msg = clt.recv(1024)
    print(msg.decode('utf-8'))
    clt.send(bytes("=\n69\n?","utf-8"))