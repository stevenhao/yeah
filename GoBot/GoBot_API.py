import numpy as np
import os
import cPickle

function_filename = 'function.save'

def load_function(filename):
    '''
        Input:
            filename: filename of pickled nnet function
        Output:
            nnet function
    '''
    f = file(filename, 'rb')
    loaded_obj = cPickle.load(f)
    f.close()

    return loaded_obj

go_bot_func = load_function(function_filename)
in_bounds = lambda x, y: 0 <= x < 19 and 0 <= y < 19

class GoBot:
    
    edge_array = [[1 for _ in range(19)] for __ in range(19)]
    

    def __init__(self, player):
        '''
            Input: player - 0 if GoBot plays black, 1 otherwise
        '''

        self.board = [[-1 for _ in range(19)] for __ in range(19)]
        self.group_map = [[-1 for _ in range(19)] for __ in range(19)]
        self.groups = []
        self.illegal = [[False for _ in range(19)] for __ in range(19)]
        self.empty_groups = []
        self.player = player

    def make_move(self, move):
        '''
            Input: 
                move: a 2-tuple representing the x, y position of the move, or 'pass'
            Output: 
                GoBot's move in response as a 2-tuple
        '''

        self.illegal = [[False for _ in range(19)] for __ in range(19)]
        if move != 'pass':
            self.update_board(move, 1 - self.player)
        else:
            self.fill_illegal(1 - self.player)

        gobot_move = self.get_response()

        self.update_board(gobot_move, self.player)

        return gobot_move

    def get_response(self):
        '''
            Output: a 2-tuple representing the move GoBot makes against the current gamestate
        '''
        input_arr = self.gamestate_to_input()

        move_arr = go_bot_func(input_arr.reshape(1, 8, 19, 19), input_arr[6].reshape(1, 19, 19))[0][0]

        best_move = np.argmax(move_arr)
        return (best_move%19, best_move/19)

    def update_board(self, move, player):
        '''
            Input:
                board: board[y][x] == 0 if (x, y) is black, 1 if (x, y) is white, -1 if empty
                group_map: group_map[y][x] == group_index of (x, y), -1 if (x, y) is empty
                groups: list of groups indexed by group_index
                        Each group contains (liberties, pieces)
                        liberites is a set of all (x, y) liberties of the group
                        pieces is a set of all stones in the group
                        elements can be None if group has been removed
                empty_groups: list of indices of all empty groups
                illegal: illegal[y][x] == 1 if move is illegal, 0 otherwise
                move: (x, y) of move
                player: 0 if black is moving, 1 if white is moving
        '''

        board = self.board
        group_map = self.group_map 
        groups = self.groups
        illegal = self.illegal
        empty_groups = self.empty_groups

        x, y = move
        opponent = 1 - player
        board[y][x] = player

        liberties = set()
        allies = set()
        enemies = set()
        for x2, y2 in [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]:
            if in_bounds(x2, y2):
                if board[y2][x2] == -1:
                    liberties.add((x2, y2))
                elif board[y2][x2] == player:
                    allies.add(group_map[y2][x2])
                else:
                    enemies.add(group_map[y2][x2])

        if len(allies) == 0:
            new_group = (liberties, set([move]))
            if empty_groups:
                group_ind = empty_groups.pop()
                groups[group_ind] = new_group
            else:
                groups.append(new_group)
                group_ind = len(groups) - 1

            group_map[y][x] = group_ind

        else:
            group_ind = min(allies)
            group_map[y][x] = group_ind

            new_liberties, new_pieces = groups[group_ind]
            for other_index in allies:
                if other_index == group_ind:
                    continue
                other_liberties, other_pieces = groups[other_index]
                new_liberties.update(other_liberties)
                new_pieces.update(other_pieces)
                temp = groups[other_index]
                for x2, y2 in other_pieces:
                    group_map[y2][x2] = group_ind

                groups[other_index] = None
                empty_groups.append(other_index)

            new_liberties.remove((x, y))

            new_pieces.add((x, y))
            new_liberties.update(liberties)

        captured = []
        for enemy in enemies:
            groups[enemy][0].remove((x, y))
            if len(groups[enemy][0]) == 0:
                pieces = groups[enemy][1]

                captured.extend(pieces)
                for x2, y2 in pieces:
                    board[y2][x2] = -1
                    group_map[y2][x2] = -1

                    for x3, y3 in [(x2-1, y2), (x2+1, y2), (x2, y2-1), (x2, y2+1)]:
                        if in_bounds(x3, y3) and board[y3][x3] == player:
                            groups[group_map[y3][x3]][0].add((x2, y2))

                groups[enemy] = None
                empty_groups.append(enemy)

        self.fill_illegal(player)

        if len(captured) == 1:
            x2, y2 = captured[0]

            is_ko = True
            for x3, y3 in [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]:
                if x2 == x3 and y2 == y3:
                    continue
                if not in_bounds(x3, y3):
                    continue
                if board[y3][x3] == player or board[y3][x3] == -1:
                    is_ko = False

            if is_ko:
                for x3, y3 in [(x2-1, y2), (x2+1, y2), (x2, y2-1), (x2, y2+1)]:
                    if x2 == x3 and y2 == y3:
                        continue
                    if not in_bounds(x3, y3):
                        continue
                    if board[y3][x3] == opponent or board[y3][x3] == -1:
                        is_ko = False

                if is_ko:
                    illegal[y2][x2] = True

    def fill_illegal(self, player):
        board = self.board
        illegal = self.illegal
        groups = self.groups
        group_map = self.group_map

        for x2 in range(19):
            for y2 in range(19):
                if board[y2][x2] != -1:
                    illegal[y2][x2] = True
                    continue

                is_illegal = True
                for x3, y3 in [(x2-1, y2), (x2+1, y2), (x2, y2-1), (x2, y2+1)]:
                    if not in_bounds(x3, y3):
                        continue
                    if board[y3][x3] == -1:
                        is_illegal = False
                        break
                    if board[y3][x3] == player:
                        if len(groups[group_map[y3][x3]][0]) == 1:
                            is_illegal = False
                            break
                        continue

                    if len(groups[group_map[y3][x3]][0]) >= 1:
                        is_illegal = False
                        break

                if is_illegal:
                    illegal[y2][x2] = True
                    continue

    def gamestate_to_input(self):
        '''
            Converts current gamestate into theano function input array.
        '''

        groups = self.groups
        group_map = self.group_map
        illegal = self.illegal
        board = self.board

        # Each array contains 3 19x19 boards - holding groups with 1, 2, >2 liberties respectively. 
        player_array = [[[0 for _ in range(19)] for __ in range(19)] for ___ in range(3)]
        opponent_array = [[[0 for _ in range(19)] for __ in range(19)] for ___ in range(3)]
        illegal_array = [[0 for _ in range(19)] for __ in range(19)]

        for x in range(19):
            for y in range(19):
                if illegal[y][x]:
                    illegal_array[y][x] = 1

                stone = board[y][x]

                if stone == -1:
                    continue

                num_liberties = len(groups[group_map[y][x]][0])
                liberty_index = 0 if num_liberties == 1 else (1 if num_liberties == 2 else 2)

                if stone == self.player:
                    player_array[liberty_index][y][x] = 1
                else:
                    opponent_array[liberty_index][y][x] = 1

        return np.array(player_array+opponent_array+[illegal_array, self.edge_array])

    def print_small_board(self):
        for i in range(19):
            text = ""
            for j in range(19):
                text += ('o' if self.illegal[i][j] else '-') if not (0 <= self.board[i][j] <= 1) else ('B' if self.board[i][j] == 0 else 'W')
            print text


