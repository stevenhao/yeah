import socket
from go_board import Board
import random, string

def generate_id(N):
    return ''.join(random.choice(string.letters) for i in xrange(N))

class GoServer:

    def __init__(self, IP='127.0.0.1', port=5005, BUFFER_SIZE=1024):
        self.TCP_IP = IP
        self.TCP_PORT = port
        self.BUFFER_SIZE = BUFFER_SIZE
        self.board = Board()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.TCP_IP, self.TCP_PORT))
        s.listen(1)
        self.s = s

    def receive_players(self):
        self.conn = [None]*2
        self.addr = [None]*2

        for i in range(2):
            conn, addr = self.s.accept()
            print 'made connection %d: %s ' % (i, addr)
            self.conn[i] = conn
            self.addr[i] = addr

        self.game_num = {} # maps connection number {0, 1} to game number {1, 2}
        self.conn_num = {} # maps game number {1, 2} to connection number {0, 1}

        first_player_num = random.randint(1, 2)
        self.game_num[0] = first_player_num
        self.game_num[1] = 2 if first_player_num == 1 else 1

        self.conn_num[1] = 0 if first_player_num == 1 else 1
        self.conn_num[2] = 1 if first_player_num == 1 else 0

    def terminate(self):
        self.s.close()
        for conn in self.conn:
            if conn:
                conn.close()

    def run_game(self):
        for i in range(2):
            self.send('BEGINGAME ' + str(self.game_num[i])+ '\n', i)
        
        while True:
            curr_player = self.board.turn
            curr_conn_num = self.conn_num[curr_player]
            data = self.conn[curr_conn_num].recv(self.BUFFER_SIZE)
            if data.startswith('MAKEMOVE'):
                tokens = data.split()
                if len(tokens) == 3:
                    try:
                        i = int(tokens[1])
                        j = int(tokens[2])
                    except ValueError:
                        continue

                    if self.board.place_piece(i, j):
                        self.send_all('MADEMOVE ' + str(i) + ' ' + str(j) + '\n')
            elif data.startswith('PASSTURN'):
                if self.board.pass_turn():
                    self.send_all('PASSEDTURN' + '\n')
                    if self.board.gameover:
                        self.send_all('GAMEOVER' + '\n')
                        break

    def send(self, message, player):
        self.conn[player].send(message)

    def send_all(self, message):
        for conn in self.conn:
            conn.send(message)


            






server = GoServer(IP='18.111.55.149')
try:
    server.receive_players()
    server.run_game()
except:
    print 'broke oops'
    server.terminate()
