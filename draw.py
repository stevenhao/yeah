import Tkinter as tk
import board

class BoardGuiTk(tk.Frame):
    bgcolor = "yellow"
    @property
    def canvas_size(self):
        return (self.columns * self.square_size,
                self.rows * self.square_size)

    def __init__(self, parent, board, square_size=64):
        self.board = board
        self.rows = len(board.board)
        self.columns = len(board.board)
        self.square_size = square_size
        self.parent = parent

        canvas_width, canvas_height = self.canvas_size

        tk.Frame.__init__(self, parent)

        self.canvas = tk.Canvas(self, width=canvas_width, height=canvas_height, background="grey")
        self.canvas.pack(side="top", fill="both", anchor="c", expand=True)

        self.canvas.bind("<Configure>", self.refresh)
        self.canvas.bind("<Button-1>", self.click)

        self.statusbar = tk.Frame(self, height=64)
        self.button_quit = tk.Button(self.statusbar, text="New", fg="black", command=self.reset)
        self.button_quit.pack(side=tk.LEFT, in_=self.statusbar)

        self.label_status = tk.Label(self.statusbar, text="   White's turn  ", fg="black")
        self.label_status.pack(side=tk.LEFT, expand=0, in_=self.statusbar)

        self.button_quit = tk.Button(self.statusbar, text="Quit", fg="black", command=self.parent.destroy)
        self.button_quit.pack(side=tk.RIGHT, in_=self.statusbar)
        self.statusbar.pack(expand=False, fill="x", side='bottom')


    def click(self, event):
        pass

    def place_piece(self, i, j):
        if self.board.place_piece(i, j):
            refresh()
        
    def addpiece(self, name, image, row=0, column=0):
        '''Add a piece to the playing board'''
        self.canvas.create_image(0,0, image=image, tags=(name, "piece"), anchor="c")
        self.placepiece(name, row, column)

    def placepiece(self, name, row, column):
        '''Place a piece at the given row/column'''
        self.pieces[name] = (row, column)
        x0 = (column * self.square_size) + int(self.square_size/2)
        y0 = ((7-row) * self.square_size) + int(self.square_size/2)
        self.canvas.coords(name, x0, y0)

    def refresh(self, event={}):

        '''Redraw the board'''
        if event:
            xsize = int((event.width) / (self.columns + 1))
            ysize = int((event.height) / (self.rows + 1))
            self.square_size = min(xsize, ysize)


        self.canvas.delete("square")
        self.canvas.delete("bg")
        margin = self.square_size / 2
        marginx = (event.width - self.rows * self.square_size) / 2
        marginy = (event.height - self.rows * self.square_size) / 2   
        self.canvas.create_rectangle(marginx - margin, marginy - margin, marginx + self.rows*self.square_size + margin, marginy + self.columns*self.square_size + margin,
                                     fill=self.bgcolor, width=0, tags="bg")     
        for row in range(self.rows):
            for col in range(self.columns):
                x1 = (col * self.square_size) + marginx
                y1 = ((self.rows-1-row) * self.square_size) + marginy
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", tags="square", width=2)

        self.canvas.tag_raise("piece")
        self.canvas.tag_lower("square")
        self.canvas.tag_lower("bg")
    
    def draw_pieces(self):
        self.canvas.delete("piece")
        for coord, piece in self.chessboard.iteritems():
            x,y = self.chessboard.number_notation(coord)
            if piece is not None:
                filename = "img/%s%s.png" % (piece.color, piece.abbriviation.lower())
                piecename = "%s%s%s" % (piece.abbriviation, x, y)

                if(filename not in self.icons):
                    self.icons[filename] = ImageTk.PhotoImage(file=filename, width=32, height=32)

                self.addpiece(piecename, self.icons[filename], x, y)
                self.placepiece(piecename, x, y)
  
    def reset(self):
        self.chessboard.load(board.FEN_STARTING)
        self.refresh()
        self.draw_pieces()
        self.refresh()

def display(board):
    root = tk.Tk()
    root.title("Simple Python Chess")

    gui = BoardGuiTk(root, board)
    gui.pack(side="top", fill="both", expand="true", padx=4, pady=4)
    # gui.draw_pieces()

    #root.resizable(0,0)
    root.mainloop()

if __name__ == "__main__":
    size = 19
    display(board.Board(size))
