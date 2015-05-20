class Board:

    def __init__(self, size=19):
        self.size = size
        self.board = [[0 for i in range(size)] for j in range(size)]
        self.turn = 2
        self.passed_last_turn = False
        self.gameover = False
        self.prev_states = {}

    @staticmethod
    def hash_board(board):
        coeff = 1
        total = 0
        for row in board:
            for cell in row:
                total += cell*coeff
                coeff *= 3
        return total + 1

    def check_state(self, board):
        hash_value = Board.hash_board(board)
        return (hash_value, hash_value not in self.prev_states)

    def add_state(self, hash_value):
        self.prev_states[hash_value] = True

    def score(self):
        board = self.board
        size = self.size

        scores = [0,0]
        checked = [[False for i in range(size)] for j in range(size)]
        for i in range(size):
            for j in range(size):
                if checked[i][j]:
                    continue

                if board[i][j] > 0:
                    checked[i][j] = True
                    scores[board[i][j] - 1] += 1
                    continue

                num_pieces, player = self._score_empty_group(checked, i, j)

                if 1 <= player <= 2:
                    scores[player - 1] += num_pieces
        return scores

    '''
        Returns a tuple of size 2:
        The first element is the number of points in the group of empty spaces
        The second element is -1 if the group is adjacent to only checked locations and board edges
        The second element is 0 if the group is adjacent to both players
        Otherwise, the second element is the player num of the adjacent player
    '''
    def _score_empty_group(self, checked, i, j):
        if not self.in_bounds(i, j):
            return (0, -1)

        if self.board[i][j]:
            return (0, self.board[i][j])

        if checked[i][j]:
            return (0, -1)

        checked[i][j] = True
        
        state = -1
        count = 1
        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_i, new_j = (i + di, j + dj)
            new_count, new_state = self._score_empty_group(checked, new_i, new_j)
            count += new_count
            if new_state == -1 or state == 0:
                continue
            elif new_state == 0:
                state = 0
            elif state == -1:
                state = new_state
            elif state != new_state:
                state = 0
            else:
                continue

        return (count, state)


    def get(self, i, j):
        return self.board[i][j]

    '''
        Returns hash_value of new gamestate is valid and unique
        Returns 0 otherwise
    '''
    def valid_move(self, i, j):
        if self.gameover:
            return False
        if self.in_bounds(i, j) and not self.get(i, j):
            hash_value = self._check_suicides_and_ko(i, j)
            if hash_value:
                return hash_value
        return 0

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
        hash_value = self.valid_move(i, j)
        if not hash_value:
            return False

        self.add_state(hash_value)

        board[i][j] = self.turn

        self._elim_pieces(i, j)
        self._next_turn()

        self.passed_last_turn = False
        return True

    def _elim_pieces(self, i, j):
        if self.turn == 1:
            self._elim_pieces_player(2, i, j, True, elim=True)
        else:
            self._elim_pieces_player(1, i, j, True, elim=True)

    '''
        Returns hash_value of new gamestate if gamestate is valid and unique
        Otherwise, returns 0

        Requires (i,j) to be valid not considering suicides and ko. 
    '''
    def _check_suicides_and_ko(self, i, j):
        if self.turn == 1:
            first, second = (1, 2)
        else:
            first, second = (2, 1)

        self.board[i][j] = first
        result, hash_value = self._elim_pieces_player(second, i, j, True, elim=False) # checks if can eliminate opponent's piece
        if result:
            self.board[i][j] = 0
            if hash_value:
                return hash_value
            else:
                return 0
            
        result, hash_value = self._elim_pieces_player(first, i, j, False, elim=False) # checks if can eliminate one's own piece
        self.board[i][j] = 0

        if result and hash_value:
            return hash_value
        else:
            return 0

    '''
        When elim is True, eliminates "player"'s pieces around i0,j0 if the group has no liberties
        When elim is False:
            If is_opponent is True:
                Returns (True, hash_value) if the state will eliminate opponent's pieces
                Returns (True, None) if the state is the same as a previous gamestate
                Returns (False, None) if the state will not eliminate opponent's pieces
            If is_opponent is False:
                Returns (True, hash_value) if the state does not eliminate one's own pieces
                Returns (True, None) if the state is the same as a previous gamestate
                Returns (False, None) if the state will eliminate one's own pieces
    '''
    def _elim_pieces_player(self, player, i0, j0, is_opponent, elim=True):
        board = self.board
        width = len(board)

        checked = [[False for i in range(width)] for j in range(width)]

        to_eliminate = []
        check_squares = [(0,1), (0,-1), (-1, 0), (1, 0)] if is_opponent else [(0,0)]
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
        
        if not elim:
            if is_opponent:
                if len(to_eliminate) == 0:
                    return (False, None)
            else:
                if len(to_eliminate) != 0:
                    return (False, None)

        for i, j in to_eliminate:
            board[i][j] = 0

        if elim:
            return

        hash_value, is_unique_state = self.check_state(board)
        for i,j in to_eliminate:
            board[i][j] = player
        if is_unique_state:
            return (True, hash_value)
        else:
            return (True, None)



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









