import Tkinter as tk
from board import Board

class BoardGuiTk(tk.Frame):
    bgcolor = "yellow"
    @property
    def canvas_size(self):
        return (self.columns * self.square_size,
                self.rows * self.square_size)

    def __init__(self, parent, board, square_size=64, min_square_size=30):
        self.board = board
        self.rows = board.size
        self.columns = board.size
        self.square_size = square_size
        self.parent = parent
        self.hover = None

        self.icons = {}

        min_canvas_width, min_canvas_height = self.rows * min_square_size, self.columns * min_square_size
        canvas_width, canvas_height = self.canvas_size

        tk.Frame.__init__(self, parent)

        self.canvas = tk.Canvas(self, width=min_canvas_width, height=min_canvas_height, background="grey")
        self.canvas.pack(side="top", fill="both", anchor="c", expand=True)

        self.canvas.bind("<Configure>", self._refresh)
        self.canvas.bind("<Button-1>", self._mouse_click)
        self.canvas.bind("<Motion>", self._mouse_move)

        self.statusbar = tk.Frame(self, height=64)

        self.button_save = tk.Button(self.statusbar, text="Save", fg="black", command=self._refresh)
        self.button_save.pack(side=tk.LEFT, in_=self.statusbar)

        self.label_status = tk.Label(self.statusbar, text="   White's turn  ", fg="black")
        self.label_status.pack(side=tk.LEFT, expand=0, in_=self.statusbar)

        self.button_quit = tk.Button(self.statusbar, text="Quit", fg="black", command=self.parent.destroy)
        self.button_quit.pack(side=tk.RIGHT, in_=self.statusbar)
        self.statusbar.pack(expand=False, fill="both", side='bottom')


    def _screenLoc(self, i, j):
        x = j*self.square_size + self.marginx
        y = i*self.square_size + self.marginy
        return x, y

    def _gridLoc(self, x, y):
        i = float(y - self.marginy)/self.square_size
        j = float(x - self.marginx)/self.square_size
        return int(i + .5), int(j + .5)

    def _mouse_move(self, event):
        i, j = self._gridLoc(event.x, event.y)

        if self.board.in_bounds(i, j) and not self.board.get(i, j):
            self.hover = i, j
        else:
            self.hover = None
        self._draw_hover()

    def _mouse_click(self, event):
        i, j = self._gridLoc(event.x, event.y)

        self.board.place_piece(i, j)
        self._draw_pieces()
        
    def _refresh(self, event={}):
        if event:
            xsize = int((event.width) / (self.columns))
            ysize = int((event.height-30) / (self.rows))
            self.width = event.width
            self.height = event.height
            self.square_size = min(xsize, ysize)
            self.marginx = (self.width - (self.rows - 1) * self.square_size) / 2
            self.marginy = (self.height - (self.columns - 1) * self.square_size) / 2  
        
        if self.board.turn == 1:
            self.label_status['text'] = "   White's turn  "
        else:
            self.label_status['text'] = "   Black's turn  "

        self._draw_board()
        self._draw_hover()
        self._draw_pieces()
    
    def _draw_board(self):
        self.canvas.delete("line")
        self.canvas.delete("background") 

        margin = self.square_size / 2
        x0, y0 = self._screenLoc(0, 0)
        x1, y1 = self._screenLoc(self.rows - 1, self.columns - 1)
        self.canvas.create_rectangle(x0 - margin, y0 - margin, x1 + margin, y1 + margin,
                                     fill=self.bgcolor, width=0, tags="background")     

        for i in range(self.rows - 1):
            for j in range(self.columns - 1):
                x, y = self._screenLoc(i, j)
                self.canvas.create_rectangle(x, y, x + self.square_size, y + self.square_size, 
                                             outline="black", tags="line", width=2)      
        self.canvas.tag_lower("line")
        self.canvas.tag_lower("background")


    def _draw_hover(self):
        self.canvas.delete("hover")
        if self.hover:
            radius = self.square_size/3
            i, j = self.hover
            x, y = self._screenLoc(i, j)
            color = "white" if self.board.turn == 1 else "black"
            self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                            tags=("hover"), fill=color)
        self.canvas.tag_raise("hover")
        self.canvas.tag_raise("piece")

    def _draw_pieces(self):
        self.canvas.delete("piece")
        radius = self.square_size/3
        for i in range(self.rows):
            for j in range(self.columns):
                if self.board.board[i][j]:
                    x, y = self._screenLoc(i, j)
                    color = "white" if self.board.get(i, j) == 1 else "black"
                    outline_color = "gray"
                    self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                            tags=("piece"), fill=color, outline=outline_color, width=2)
        self.canvas.tag_raise("piece")
  
def display(board):
    root = tk.Tk()
    root.title("Python Go")

    gui = BoardGuiTk(root, board)
    gui.pack(side="top", fill="both", expand="true", padx=4, pady=4)

    # root.resizable(0,0)
    root.mainloop()

if __name__ == "__main__":
    size = 19
    board = Board(size)
    display(board)
