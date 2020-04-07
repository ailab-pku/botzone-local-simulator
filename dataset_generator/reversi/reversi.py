# -*- coding: utf-8 -*-
import copy

BLACK = 1
WHITE = -1
EMPTY = 0


class Reversi:
    def __init__(self, board_size=8):
        self.board_size = board_size
        self.board = [[EMPTY] * self.board_size for _ in range(self.board_size)]
        mid = self.board_size // 2
        self.board[mid-1][mid] = self.board[mid][mid-1] = BLACK
        self.board[mid-1][mid-1] = self.board[mid][mid] = WHITE
        self.num_black = self.num_white = 2
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
        if not self.done:
            return 0
        else:
            if player == BLACK:
                return self.num_black - self.num_white
            else:
                return self.num_white - self.num_black
    
    def step(self, action):
        # action pass
        if action == -1:
            if len(self.available_action(self.current_player)) != 0:
                self.__lose()
            else:
                self.__take_turn()
        # valid action
        elif 0 <= action < self.board_size ** 2:
            row, col = action // self.board_size, action % self.board_size
            if self.__process_action(action, self.current_player) is False:
                self.__lose()
            elif len(self.available_action(BLACK)) == 0 and len(self.available_action(WHITE)) == 0:
                self.__game_over()
            else:
                self.__take_turn()
        # invalid action
        else:
            self.__lose()

    def reset(self):
        self.board = [[EMPTY] * self.board_size for _ in range(self.board_size)]
        mid = self.board_size // 2
        self.board[mid - 1][mid] = self.board[mid][mid - 1] = BLACK
        self.board[mid - 1][mid - 1] = self.board[mid][mid] = WHITE
        self.num_black = self.num_white = 2
        self.round = 0
        self.current_player = BLACK
        self.winner = None
        self.done = False

    def render(self):
        print("round: {round}, player: {player}, #black: {num_black}, #white: {num_white}".format(
            round=self.round, player=self.current_player_name,
            num_black=self.num_black,num_white=self.num_white))
        print(" " + " ".join([str(i) for i in range(self.board_size)]))
        render_mapping = {BLACK: "B", WHITE: "W", EMPTY: "."}
        for i, row in enumerate(self.board):
            render = [render_mapping[position] for position in row]
            print("{row} {row_board}".format(row=i, row_board=" ".join(render)))
        available_action = self.available_action(self.current_player)
        if len(available_action) == 0:
            print("no available action for {player}".format(player=self.current_player_name))
        else:
            print("{player}'s available action(s):".format(player=self.current_player_name))
            print(" ".join(["({row}, {col})".format(row=a // self.board_size, col=a % self.board_size) for a in available_action]))

    @staticmethod
    def _next_position(row, col, direction):
        """Compute next position based on current position and direction
        4 3 2
        5 X 1
        6 7 0

        :param row: int, current row position
        :param col: int, current column position
        :param direction: int, direction defined above
        :return: tuple(int, int), next row and column position
        """
        if direction in (0, 6, 7):
            row += 1
        if direction in (0, 1, 2):
            col += 1
        if direction in (2, 3, 4):
            row -=1
        if direction in (4, 5, 6):
            col -= 1
        return row, col

    def __process_action(self, action, player, check_only=False):
        row, col = action // self.board_size, action % self.board_size
        if self.board[row][col] != EMPTY:
            return False
        flip_positions = []
        is_valid_action = False
        for direction in range(8):
            i, j = row, col
            num_flip = 0
            while True:
                i, j = self._next_position(i, j, direction)
                if i < 0 or i >= self.board_size or j < 0 or j >= self.board_size \
                    or self.board[i][j] == EMPTY:
                    num_flip = 0
                    break
                if self.board[i][j] == player:
                    break
                num_flip += 1
                flip_positions.append((i, j))
            if num_flip != 0:
                if check_only:
                    return True
                is_valid_action = True
                for flip_i, flip_j in flip_positions:
                    self.board[flip_i][flip_j] = player
                if player == BLACK:
                    self.num_black += num_flip
                    self.num_white -= num_flip
                else:
                    self.num_black -= num_flip
                    self.num_white += num_flip
            flip_positions = []
        if is_valid_action:
            self.board[row][col] = player
            if player == BLACK:
                self.num_black += 1
            else:
                self.num_white += 1
        return is_valid_action

    def __take_turn(self):
        if self.current_player == BLACK:
            self.current_player = WHITE
        else:
            self.current_player = BLACK
        self.round += 1

    def __game_over(self):
        self.done = True
        if self.winner is None:
            if self.num_black == self.num_white:
                self.winner = EMPTY
            elif self.num_black > self.num_white:
                self.winner = BLACK
            else:
                self.winner = WHITE

    def __lose(self):
        if self.current_player == BLACK:
            self.winner = WHITE
        else:
            self.winner = BLACK
        self.__game_over()

    def available_action(self, player=None):
        if player is None:
            player = self.current_player
        available_action = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                action = i * self.board_size + j
                if self.__process_action(action, player, check_only=True):
                    available_action.append(action)
        return available_action

# demo
if __name__ == "__main__":
    import random

    game = Reversi()
    while not game.done:
        game.render()
        available_action = game.available_action()
        if len(available_action) > 0:
            action = random.choice(game.available_action())
        else:
            action = -1 # no position to step
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
