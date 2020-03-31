# -*- coding: utf-8 -*-
import copy

BLACK = 1
WHITE = -1
EMPTY = 0


class Gomoku:
    def __init__(self, board_size=15, target_number=5):
        self.board_size = board_size
        self.target_number = target_number

        self.board = [[EMPTY] * self.board_size for _ in range(self.board_size)]
        self.round = 0
        self.current_player = BLACK
        self.winner = None
        self.done = False

    @property
    def current_player_name(self):
        return "BLACK" if self.current_player == BLACK else "WHITE"
    
    def state(self):
        return copy.deepcopy(self.board)
    
    def reward(self, player):
        if not self.done or self.winner is None:
            return 0
        else:
            if self.winner == BLACK:
                return 1 if player == BLACK else -1
            else:
                return -1 if player == BLACK else 1

    def step(self, action):
        # valid action
        if 0 <= action < self.board_size ** 2:
            row, col = action // self.board_size, action % self.board_size
            if self.board[row][col] != EMPTY:
                self.__lose()
                return
            # judge
            self.board[row][col] = self.current_player
            if self.__judge_win(row, col, self.current_player):
                self.done = True
                self.winner = self.current_player
            else:
                if len(self.available_action()) > 0:
                    self.__take_turn()
                else:
                    self.done = True
        # invalid action
        else:
            self.__lose()

    def reset(self):
        self.board = [[EMPTY] * self.board_size for _ in range(self.board_size)]
        self.round = 0
        self.current_player = BLACK
        self.winner = None
        self.done = False

    def render(self):
        print("round: {round}, player: {player}".format(round=self.round, player=self.current_player_name))
        print("  " + " ".join(["{column:02d}".format(column=i) for i in range(self.board_size)]))
        render_mapping = {BLACK: "B", WHITE: "W", EMPTY: "."}
        for i, row in enumerate(self.board):
            render = [render_mapping[position] for position in row]
            print("{row:02d} {row_board}".format(row=i, row_board="  ".join(render)))

    def __position_in_board(self, x, y):
        return x >= 0 and x < self.board_size and y >= 0 and y < self.board_size

    def __compute_number_in_row(self, x, y, direction_x, direction_y, player):
        i, j = 0, 0
        while i < self.target_number:
            tmp_x, tmp_y = x + i * direction_x, y + i * direction_y
            if not self.__position_in_board(tmp_x, tmp_y) or self.board[tmp_x][tmp_y] != player:
                break
            i += 1
        while j < self.target_number:
            tmp_x, tmp_y = x - j * direction_x, y - j * direction_y
            if not self.__position_in_board(tmp_x, tmp_y) or self.board[tmp_x][tmp_y] != player:
                break
            j += 1
        return i + j - 1

    def __judge_win(self, x, y, player):
        directions = ((1, 0), (0, 1), (1, 1), (1, -1))
        is_win = False
        for direction_x, direction_y in directions:
            is_win |= self.__compute_number_in_row(x, y, direction_x, direction_y, player) >= self.target_number
        return is_win

    def __take_turn(self):
        if self.current_player == BLACK:
            self.current_player = WHITE
        else:
            self.current_player = BLACK
        self.round += 1

    def __lose(self):
        if self.current_player == BLACK:
            self.winner = WHITE
        else:
            self.winner = BLACK
        self.done = True

    def available_action(self):
        available_action = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                action = i * self.board_size + j
                if self.board[i][j] == EMPTY:
                    available_action.append(action)
        return available_action

# demo
if __name__ == "__main__":
    import random

    game = Gomoku()
    while not game.done:
        game.render()
        available_action = game.available_action()
        action = random.choice(game.available_action())
        game.step(action)
    game.render()
    black_score, white_score = game.reward(BLACK), game.reward(WHITE)
    print("BLACK:", black_score, "WHITE:", white_score)
    if black_score == white_score:
        print("DRAW")
    elif black_score > white_score:
        print("BLACK wins")
    else:
        print("WHITE wins")
