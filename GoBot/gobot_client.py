from sys import argv
from socket import socket as Socket, AF_INET, SOCK_STREAM, error as SocketError
from GoBot_API import GoBot

class GoBotClient:

    def __init__(self, IP='127.0.0.1', port=5005):
        self.IP = IP
        self.port = port
        self.player = None
        self.turn = 2

    def start_game(self, player, size):
        self.player = player
        print 'beginning game as player %d' % player
        self.GoBot = GoBot(0 if player == 2 else 1)
        
        if player == 2:
            self.make_move('pass')

    def made_move(self, i, j):
        self.turn = 1 if self.turn == 2 else 2

    def passed_turn(self):
        self.turn = 1 if self.turn == 2 else 2

    def make_move(self, move):
        if self.turn == self.player:
            if move != 'pass':
                gobot_move = self.GoBot.make_move((move[1], move[0]))
            else:
                gobot_move = self.GoBot.make_move('pass')
            self.send('MAKEMOVE %d %d' % (gobot_move[1], gobot_move[0]))

    def run(self):
        self.connect_to_server()
        while True:
            self.listen()
       
    def receive(self, data):
        print 'receiving [%s]' % data
        data = data.split()
        if not data:
            return
        message = data[0]
        if message == 'BEGINGAME':
            self.start_game(int(data[1]), int(data[2]))
        elif message == 'MADEMOVE':
            i, j = map(int, data[1:3])
            self.made_move(i, j)
            if self.turn == self.player:
                self.make_move((i, j))
        elif message == 'PASSEDTURN':
            self.passed_turn()
            if self.turn == self.player:
                self.make_move('pass')
        elif message == 'GAMEOVER':
            a, b = map(int, data[1:3])
            self.game_over(a, b)

    def send(self, data):
        print 'sending %s' % data
        self.skt.send(data)

    def connect_to_server(self):
        BUFFER_SIZE = 1024

        self.skt = Socket(AF_INET, SOCK_STREAM)
        self.skt.connect((self.IP, self.port))
        self.skt.setblocking(0)
    
    def listen(self):
        BUFFER_SIZE = 1024

        try:
            data = self.skt.recv(BUFFER_SIZE)
        except SocketError:
            pass
        else:
            if not data:
                return
            for line in data.split('\n'):
                self.receive(line)


if __name__ == '__main__':
    IP = '18.111.55.149'
    port = 5005
    if len(argv) >= 2:
        port = int(argv[1])
    if len(argv) >= 3:
        IP = argv[2]

    client = GoBotClient(IP=IP, port=port)
    client.run()