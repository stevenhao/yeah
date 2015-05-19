import Tkinter as tk
from board import Board
import thread

class BoardGuiTk(tk.Frame):
    bgcolor = "DarkGoldenrod3"
    @property
    def canvas_size(self):
        return (self.columns * self.square_size,
                self.rows * self.square_size)

    def __init__(self, parent, board, square_size=40):
        self.board = board
        self.rows = board.size
        self.columns = board.size
        self.square_size = square_size
        self.parent = parent
        self.hover = None

        self.star_points = self._compute_star_points()

        canvas_width, canvas_height = self.canvas_size

        tk.Frame.__init__(self, parent)

        self.canvas = tk.Canvas(self, width=canvas_width, height=canvas_height, background="grey")
        self.canvas.pack(side="top", fill="both", anchor="c", expand=True)

        self.canvas.bind("<Configure>", self._refresh)
        self.canvas.bind("<Button-1>", self._mouse_click)
        self.canvas.bind("<Motion>", self._mouse_move)
        self.canvas.bind("<Enter>", self._mouse_enter)
        self.canvas.bind("<Leave>", self._mouse_leave)

        self.statusbar = tk.Frame(self, height=64)

        self.button_save = tk.Button(self.statusbar, text="Save", fg="black", command=self._refresh)
        self.button_save.pack(side=tk.LEFT, in_=self.statusbar)

        self.label_status = tk.Label(self.statusbar, text="   White's turn  ", fg="black")
        self.label_status.pack(side=tk.LEFT, expand=0, in_=self.statusbar)

        self.button_quit = tk.Button(self.statusbar, text="Quit", fg="black", command=self.parent.destroy)
        self.button_quit.pack(side=tk.RIGHT, in_=self.statusbar)
        self.statusbar.pack(expand=False, fill="both", side='bottom')

    def _mouse_leave(self, event):
        self.hover = None
        self._refresh()

    def _mouse_enter(self, event):
        self.parent.grab_set()
        self.cnt = 0

    def _mouse_move(self, event):
        i, j = self._gridLoc(event.x, event.y)

        if self.board.in_bounds(i, j) and not self.board.get(i, j):
            self.hover = i, j
        else:
            self.hover = None
        self._draw_hover()

    def _mouse_click(self, event):
        if not self.parent.focus_get():
            return
        i, j = self._gridLoc(event.x, event.y)

        if self.board.place_piece(i, j):
            self.hover = None
            self._refresh()

    def _compute_star_points(self):
        size = self.board.size
        if size == 19:
            return [(i, j) for i in [3, 9, 15] for j in [3, 9, 15]]

        corner_offset = 3

        rows, columns = self.rows, self.columns
        row_coordinates = [corner_offset, rows - 1 - corner_offset]
        column_coordinates = [corner_offset, columns - 1 - corner_offset]
        if rows % 2 == 1:
            row_coordinates += [rows / 2]
        if columns % 2 == 1:
            column_coordinates += [columns / 2]

        return [(i, j) for i in row_coordinates for j in column_coordinates]

    def _screenLoc(self, i, j):
        x = j*self.square_size + self.marginx
        y = i*self.square_size + self.marginy
        return x, y

    def _gridLoc(self, x, y):
        i = float(y - self.marginy)/self.square_size
        j = float(x - self.marginx)/self.square_size
        
        return int(round(i)), int(round(j))

        
    def _refresh(self, event={}):
        if event:
            xsize = int((event.width-30) / (self.columns))
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

        def draw_background():
            margin = self.square_size / 2
            x0, y0 = self._screenLoc(0, 0)
            x1, y1 = self._screenLoc(self.rows - 1, self.columns - 1)
            self.canvas.create_rectangle(x0 - margin, y0 - margin, x1 + margin, y1 + margin,
                                         fill=self.bgcolor, width=4, tags="background", outline="black")     

        def draw_grid():
            for i in range(self.rows):
                x0, y0 = self._screenLoc(i, 0)
                x1, y1 = self._screenLoc(i, self.columns - 1)
                self.canvas.create_line(x0, y0, x1, y1, tags="line")

            for j in range(self.columns):
                x0, y0 = self._screenLoc(0, j)
                x1, y1 = self._screenLoc(self.rows - 1, j)
                self.canvas.create_line(x0, y0, x1, y1, tags="line")

        def draw_stars():
            radius = self.square_size/10
            for i, j in self.star_points:
                x, y = self._screenLoc(i, j)
                self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                        fill="black", tags="star")

        self.canvas.delete("line")
        self.canvas.delete("background") 
        self.canvas.delete("star")
        draw_background()
        draw_grid()
        draw_stars()
        self.canvas.tag_lower("star")
        self.canvas.tag_lower("line")
        self.canvas.tag_lower("background")


    def _draw_hover(self):
        self.canvas.delete("hover")
        if self.hover:
            radius = max(1, self.square_size/3 - 2)
            i, j = self.hover
            x, y = self._screenLoc(i, j)
            color = "white" if self.board.turn == 1 else "black"
            self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                            tags="hover", fill=color)
        self.canvas.tag_raise("hover")
        self.canvas.tag_raise("piece")

    def _draw_pieces(self):
        self.canvas.delete("piece")
        radius = self.square_size/3
        for i in range(self.rows):
            for j in range(self.columns):
                if self.board.board[i][j]:
                    x, y = self._screenLoc(i, j)
                    color, outline_color = ("white", "gray") if self.board.get(i, j) == 1 else ("black", "black")
                    self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                            tags="piece", fill=color, outline=outline_color, width=1)
        self.canvas.tag_raise("piece")
  
def display(board):
    root = tk.Tk()
    root.title("Python Go")

    gui = BoardGuiTk(root, board)
    gui.pack(side="top", fill="both", expand="true", padx=4, pady=4)

    # root.resizable(0,0)
    root.mainloop()


if __name__ == '__main__':
    size = 19
    board = Board(size)
    display(board)
