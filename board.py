class Board:

    def __init__(self, width):
        self.board = [[0 for _ in range(width)] for __ in range(width)]
        self.turn = 1

    def place_piece(self, pos_x, pos_y):
        board = self.board
        if (not 0 <= pos_x < len(board)) or (not 0 <= pos_y < len(board)):
            return False
        if board[pos_x][pos_y] != 0:
            return False

        board[pos_x][pos_y] = self.turn

        self.elim_pieces()
        self.turn = 2 if self.turn == 1 else 1
        return True

    def elim_pieces(self):
        if self.turn == 1:
            self.elim_pieces_player(2)
            self.elim_pieces_player(1)
        else:
            self.elim_pieces_player(1)
            self.elim_pieces_player(2)

    def elim_pieces_player(self, player):
        board = self.board
        width = len(board)

        checked = [[False for _ in range(width)] for __ in range(width)]

        to_eliminate = []
        for i in range(width):
            for j in range(width):
                if checked[i][j]:
                    continue
                if board[i][j] != player:
                    checked[i][j] = True
                    continue

                newly_checked = []
                if not self.elim_pieces_floodfill(i,j,checked,player,False,newly_checked):
                    to_eliminate.extend(newly_checked)
        for i,j in to_eliminate:
            board[i][j] = 0

    def elim_pieces_floodfill(self, pos_x, pos_y, checked, player, has_liberty, newly_checked):
        board = self.board
        width = len(board)

        if (not 0 <= pos_x < len(board)) or (not 0 <= pos_y < len(board)):
            return False

        if board[pos_x][pos_y] == 0:
            return True
        elif board[pos_x][pos_y] != player:
            return False

        if checked[pos_x][pos_y]:
            return False

        newly_checked.append((pos_x, pos_y))
        checked[pos_x][pos_y] = True
        found_liberty = False
        for i,j in [(-1, 0), (1,0), (0, -1), (0, 1)]:
            new_x, new_y = (pos_x + i, pos_y + j)
            found_new_liberty = self.elim_pieces_floodfill(new_x, new_y, checked, player, has_liberty, newly_checked)
            found_liberty = found_new_liberty or found_liberty
        if has_liberty or found_liberty:
            return True
        else:
            return False





