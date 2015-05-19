class Board:

    def __init__(self, size=19):
        self.size = size
        self.board = [[0 for i in range(size)] for j in range(size)]
        self.turn = 2
        self.passed_last_turn = False
        self.gameover = False

    def get(self, i, j):
        return self.board[i][j]

    def valid_move(self, i, j):
        return self.in_bounds(i, j) and not self.get(i, j)

    def in_bounds(self, i, j):
        return 0 <= i < self.size and 0 <= j < self.size

    def pass_turn(self):
        if self.gameover:
            return False

        self._next_turn()

        if self.passed_last_turn:
            self.gameover = True
        self.passed_last_turn = True
        return True

    def place_piece(self, i, j):
        if self.gameover:
            return False

        board = self.board
        if not self.valid_move(i, j):
            return

        board[i][j] = self.turn

        self._elim_pieces(i, j)
        self._next_turn()

        self.passed_last_turn = False
        return True

    def _elim_pieces(self, i, j):
        if self.turn == 1:
            self._elim_pieces_player(2, i, j, True)
            self._elim_pieces_player(1, i, j, False)
        else:
            self._elim_pieces_player(1, i, j, True)
            self._elim_pieces_player(2, i, j, False)

    def _elim_pieces_player(self, player, i0, j0, check_adj):
        board = self.board
        width = len(board)

        checked = [[False for i in range(width)] for j in range(width)]

        to_eliminate = []
        check_squares = [(0,1), (0,-1), (-1, 0), (1, 0)] if check_adj else [(0,0)]
        for di,dj in check_squares:
            i,j = (i0+di, j0+dj)
            if not self.in_bounds(i, j) or checked[i][j]:
                continue
            if board[i][j] != player:
                checked[i][j] = True
                continue

            newly_checked = []
            if not self._elim_pieces_floodfill(i, j, checked, player, False, newly_checked):
                to_eliminate.extend(newly_checked)
        for i, j in to_eliminate:
            board[i][j] = 0

    def _elim_pieces_floodfill(self, i, j, checked, player, has_liberty, newly_checked):
        board = self.board

        if not self.in_bounds(i, j):
            return False

        if board[i][j] == 0:
            return True
        elif board[i][j] != player:
            return False

        if checked[i][j]:
            return False

        newly_checked.append((i, j))
        checked[i][j] = True
        found_liberty = False
        for di, dj in [(-1, 0), (1,0), (0, -1), (0, 1)]:
            new_i, new_j = (i + di, j + dj)
            found_new_liberty = self._elim_pieces_floodfill(
                new_i, new_j, checked, player, has_liberty, newly_checked)
            found_liberty = found_new_liberty or found_liberty
        if has_liberty or found_liberty:
            return True
        else:
            return False

    def _next_turn(self):
        self.turn = 2 if self.turn == 1 else 1



