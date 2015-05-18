import Tkinter as tk
import board
from PIL import ImageTk

class BoardGuiTk(tk.Frame):
    bgcolor = "yellow"
    @property
    def canvas_size(self):
        return (self.columns * self.square_size,
                self.rows * self.square_size)

    def __init__(self, parent, board, square_size=64, min_square_size=30):
        self.board = board
        self.rows = len(board.board)
        self.columns = len(board.board)
        self.square_size = square_size
        self.parent = parent

        self.icons = {}

        min_canvas_width, min_canvas_height = self.rows * min_square_size, self.columns * min_square_size
        canvas_width, canvas_height = self.canvas_size

        tk.Frame.__init__(self, parent)

        self.canvas = tk.Canvas(self, width=min_canvas_width, height=min_canvas_height, background="grey")
        self.canvas.pack(side="top", fill="both", anchor="c", expand=True)

        self.canvas.bind("<Configure>", self.refresh)
        self.canvas.bind("<Button-1>", self.click)

        self.statusbar = tk.Frame(self, height=64)
        self.button_quit = tk.Button(self.statusbar, text="New", fg="black", command=self.reset)
        self.button_quit.pack(side=tk.LEFT, in_=self.statusbar)

        self.button_save = tk.Button(self.statusbar, text="Save", fg="black", command=self.reset)
        self.button_save.pack(side=tk.LEFT, in_=self.statusbar)

        self.label_status = tk.Label(self.statusbar, text="   White's turn  ", fg="black")
        self.label_status.pack(side=tk.LEFT, expand=0, in_=self.statusbar)

        self.button_quit = tk.Button(self.statusbar, text="Quit", fg="black", command=self.parent.destroy)
        self.button_quit.pack(side=tk.RIGHT, in_=self.statusbar)
        self.statusbar.pack(expand=False, fill="both", side='bottom')


    def click(self, event):
        margin = self.square_size / 2
        marginx = (self.width - (self.rows - 1) * self.square_size) / 2
        marginy = (self.height - (self.columns - 1) * self.square_size) / 2
        radius = self.square_size / 4 
        
        near_i = (event.y - marginy)/float(self.square_size)
        near_j = (event.x - marginx)/float(self.square_size)
        round_i = int(near_i) if near_i - int(near_i) < .5 else int(near_i) + 1
        round_j = int(near_j) if near_j - int(near_j) < .5 else int(near_j) + 1
        if abs(near_i - round_i) > radius/float(self.square_size) or abs(near_j - round_j) > radius/float(self.square_size):
            return
        else:
            self.board.place_piece(round_i,round_j)
        self.refresh()
        
    def refresh(self, event={}):

        '''Redraw the board'''
        if event:
            xsize = int((event.width) / (self.columns))
            ysize = int((event.height-30) / (self.rows))
            self.width = event.width
            self.height = event.height
            self.square_size = min(xsize, ysize)
        if self.board.turn == 1:
            self.label_status['text'] = "   White's turn  "
        else:
            self.label_status['text'] = "   Black's turn  "
        self.canvas.delete("square")
        self.canvas.delete("bg")
        margin = self.square_size / 2
        marginx = (self.width - (self.rows - 1) * self.square_size) / 2
        marginy = (self.height - (self.columns - 1) * self.square_size) / 2   
        self.canvas.create_rectangle(marginx - margin, marginy - margin, marginx + (self.rows-1)*self.square_size + margin, marginy + (self.columns-1)*self.square_size + margin,
                                     fill=self.bgcolor, width=0, tags="bg")     
        for row in range(self.rows - 1):
            for col in range(self.columns - 1):
                x1 = (col * self.square_size) + marginx
                y1 = (row * self.square_size) + marginy

                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", tags="square", width=2)

        self.draw_pieces()
        self.canvas.tag_raise("piece")
        self.canvas.tag_lower("square")
        self.canvas.tag_lower("bg")
    
    def draw_pieces(self):
        self.canvas.delete("piece")
        radius = self.square_size/3
        margin = self.square_size / 2
        marginx = (self.width - (self.rows - 1) * self.square_size) / 2
        marginy = (self.height - (self.columns - 1) * self.square_size) / 2   
        for i in range(self.rows):
            for j in range(self.columns):
                if self.board.board[i][j] == 0:
                    continue
                # piece = self.board.board[x][y]
                # filename = "img/white.png" if piece == 1 else "img/black.png"
                # piecename = "white" if piece == 1 else "black"
                # piecename += " " + str(x) + " " + str(y)

                # if(filename not in self.icons):
                #     self.icons[filename] = ImageTk.PhotoImage(file=filename, width=32, height=32)
                # self.addpiece(piecename, self.icons[filename], x, y)
                if self.board.board[i][j] == 1:
                    self.canvas.create_oval(marginx + j*self.square_size - radius, marginy + i*self.square_size - radius, \
                 marginx + j*self.square_size + radius, marginy + i*self.square_size + radius, tags = ("piece"), \
                 fill = "white", outline = "black")
                else: 
                    self.canvas.create_oval(marginx + j*self.square_size - radius, marginy + i*self.square_size - radius, \
                 marginx + j*self.square_size + radius, marginy + i*self.square_size + radius, tags = ("piece"), \
                 fill = "black")
  
    def reset(self):
        self.refresh()
        # self.draw_pieces()
        # self.refresh()

def display(board):
    root = tk.Tk()
    root.title("Python Go")

    gui = BoardGuiTk(root, board)
    gui.pack(side="top", fill="both", expand="true", padx=4, pady=4)

    #root.resizable(0,0)
    root.mainloop()

if __name__ == "__main__":
    size = 19
    board = board.Board(size)
    board.place_piece(0,0)
    display(board)
