class Board:

    def __init__(self, size):
        self.size = size
        self.board = [[0 for i in range(size)] for j in range(size)]
        self.turn = 1

    def get(self, i, j):
        return self.board[i][j]

    def in_bounds(self, i, j):
        return 0 <= i < self.size and 0 <= j < self.size

    def place_piece(self, i, j):
        board = self.board
        if not self.in_bounds(i, j):
            return False
        if board[i][j] != 0:
            return False

        board[i][j] = self.turn

        self._elim_pieces()
        self.turn = 2 if self.turn == 1 else 1
        return True

    def _elim_pieces(self):
        if self.turn == 1:
            self._elim_pieces_player(2)
            self._elim_pieces_player(1)
        else:
            self._elim_pieces_player(1)
            self._elim_pieces_player(2)

    def _elim_pieces_player(self, player):
        board = self.board
        width = len(board)

        checked = [[False for i in range(width)] for j in range(width)]

        to_eliminate = []
        for i in range(width):
            for j in range(width):
                if checked[i][j]:
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
        for dx, dy in [(-1, 0), (1,0), (0, -1), (0, 1)]:
            new_i, new_j = (i + dx, j + dy)
            found_new_liberty = self._elim_pieces_floodfill(
                new_i, new_j, checked, player, has_liberty, newly_checked)
            found_liberty = found_new_liberty or found_liberty
        if has_liberty or found_liberty:
            return True
        else:
            return False





