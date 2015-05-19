from socket import socket as Socket, AF_INET, SOCK_STREAM, error as SocketError
import Tkinter as tk
from go_board import Board
from go_gui import BoardGui

size = 19

class GoClient:

    def __init__(self):
        self.root = tk.Tk()
        self.board = Board(size)
        self.players = []

    def start_game(self, player):
        self.players.append(player)
        print 'beginning game as player %d' % player

    def made_move(self, i, j):
        self.board.place_piece(i, j)
        self.gui.made_move()

    def on_click(self, i, j):
        if self.board.turn in self.players:
            self.send('MAKEMOVE %d %d' % (i, j))
            # self.receive('MADEMOVE %d %d' % (i, j))

    def run(self):
        # self.start_game(1)
        # self.start_game(2)
        self.connect_to_server()
        # print 'received data:', data
        self.make_display()

    def make_display(self):
        self.root.title('Python Go')

        self.gui = BoardGui(parent=self.root, board=self.board, players=self.players)
        self.gui.on_click.append(self.on_click)
        self.gui.pack(side='top', fill='both', expand='true', padx=4, pady=4)

        # root.resizable(0,0)
        self.root.mainloop()

    def receive(self, data):
        print 'receiving %s' % data
        data = data.split()
        message = data[0]
        if message == 'BEGINGAME':
            self.start_game(int(data[1]))
        elif message == 'MADEMOVE':
            i, j = map(int, data[1:3])
            self.made_move(i, j)

    def send(self, data):
        print 'sending %s' % data
        self.skt.send(data)

    def connect_to_server(self):
        TCP_IP = '127.0.0.1'
        TCP_PORT = 5005
        BUFFER_SIZE = 1024

        self.skt = Socket(AF_INET, SOCK_STREAM)
        self.skt.connect((TCP_IP, TCP_PORT))
        self.skt.setblocking(0)
        def listen():
            try:
                data = self.skt.recv(BUFFER_SIZE)
            except SocketError:
                pass
            else:
                self.receive(data)
            self.root.after(500, listen)

        listen()


if __name__ == '__main__':
    client = GoClient()
    client.run()