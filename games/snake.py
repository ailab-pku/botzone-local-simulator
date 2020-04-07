# -*- coding: utf-8 -*-
import copy
import random

DIR = [(-1, 0), (0, 1), (1, 0), (0, -1)]
EMPTY, OBSTACLE = 0, 9
SNAKE0, SNAKE0_HEAD, SNAKE0_TAIL = 1, 2, 3
SNAKE1, SNAKE1_HEAD, SNAKE1_TAIL = -1, -2, -3


class Snake:
    def __init__(self, height=None, width=None, obstacles=None):
        self.height, self.width = height, width
        if self.height is None or self.width is None:
            self.height, self.width = random.randint(10, 16), random.randint(10, 12)
        self.obstacles = obstacles
        self.board, self.snake_0, self.snake_1 = self.__init_map()
        self.round = 0
        self.winner = None
        self.done = False
        self.last_action = None
    
    def __init_map(self):
        board = [[EMPTY] * self.width for _ in range(self.height)]
        if self.obstacles is None:
            self.obstacles = self.__generate_obstacles()
        for x, y in self.obstacles:
            board[x][y] = OBSTACLE
        
        snake_0, snake_1 = [(0, 0)], [(self.height - 1, self.width - 1)]
        board[0][0] = SNAKE0_HEAD
        board[self.height - 1][self.width - 1] = SNAKE1_HEAD
        return board, snake_0, snake_1
    
    def __generate_obstacles(self):
        num_obstacles = self.height * self.width // 10
        while True:
            obstacles = []
            vis = [[0] * self.width for _ in range(self.height)]
            for _ in range(num_obstacles // 2):
                x, y = random.randint(0, self.height - 1), random.randint(0, self.width - 1)
                while vis[x][y] == 1 or (x == 0 and y == 0) or (x == self.height - 1 and y == self.width - 1):
                    x, y = random.randint(0, self.height - 1), random.randint(0, self.width - 1)
                vis[x][y] = 1
                obstacles.append((x, y))
                if x != self.height - x - 1 or y != self.width - y - 1:
                    vis[self.height - x - 1][self.width - y - 1] = 1
                    obstacles.append((self.height - x - 1, self.width - y - 1))
            Snake.dfs(0, 0, vis)
            if sum(sum(vis, [])) == self.height * self.width:
                break
        return obstacles

    @staticmethod
    def dfs(x, y, vis):
        vis[x][y] = 1
        for dx, dy in DIR:
            tx, ty = x + dx, y + dy
            if tx >= 0 and tx < len(vis) and ty >= 0 and ty < len(vis[0]) and vis[tx][ty] == 0:
                Snake.dfs(tx, ty, vis)

    def state(self, player):
        board = copy.deepcopy(self.board)
        if player == SNAKE0:
            return board
        else:
            for i in range(self.height):
                for j in range(self.width):
                    if board[i][j] != EMPTY and board[i][j] != OBSTACLE:
                        board[i][j] *= -1
        return board

    def reward(self, player):
        if self.done is False:
            return 0
        return 1 if player == self.winner else -1
    
    def step(self, action):
        # whether grow
        if self.round > 9 and (self.round - 9) % 3 != 0:
            self.board[self.snake_0[-1][0]][self.snake_0[-1][1]] = EMPTY
            self.snake_0.pop(-1)
            self.board[self.snake_1[-1][0]][self.snake_1[-1][1]] = EMPTY
            self.snake_1.pop(-1)
        
        for snake in (SNAKE0, SNAKE1):
            current_action = action[0 if snake == SNAKE0 else 1]
            if current_action >= 0 and current_action <= 3 and snake == SNAKE1 and self.snake_0[0][0] == self.snake_1[0][0] + DIR[current_action][0] and self.snake_0[0][1] == self.snake_1[0][1] + DIR[current_action][1]:
                self.__lose(SNAKE0)
                self.__lose(SNAKE1)
                continue
            if self.__validate_action(current_action, snake):
                self.__snake_move(current_action, snake)
            else:
                self.__lose(snake)
        self.round += 1
        self.last_action = action

    def reset(self):
        self.board, self.snake_0, self.snake_1 = self.__init_map()
        self.round = 0
        self.winner = None
        self.done = False
        self.last_action = None

    def render(self):
        print("round: {round}, last action: {last_action}".format(round=self.round, last_action=self.last_action))
        for row in self.board:
            render = [Snake.render_mapping(position) for position in row]
            print(" ".join(render))
        print("done: {done}".format(done=self.done))
    
    @staticmethod
    def render_mapping(value):
        if value == EMPTY:
            return "."
        elif value == OBSTACLE:
            return "X"
        elif value > 0:
            return "0"
        else:
            return "1"

    def __validate_action(self, action, player):
        if action < 0 or action > 3:
            return False
        snake = self.snake_0 if player == SNAKE0 else self.snake_1
        nx, ny = snake[0][0] + DIR[action][0], snake[0][1] + DIR[action][1]
        if nx < 0 or nx >= self.height or ny < 0 or ny >= self.width:
            return False
        if self.board[nx][ny] == OBSTACLE:
            return False
        if (nx, ny) in self.snake_0 or (nx, ny) in self.snake_1:
            return False
        return True
    
    def __snake_move(self, action, player):
        snake = self.snake_0 if player == SNAKE0 else self.snake_1
        # head
        nx, ny = snake[0][0] + DIR[action][0], snake[0][1] + DIR[action][1]
        snake.insert(0, (nx, ny))
        self.board[nx][ny] = SNAKE0_HEAD if player == SNAKE0 else SNAKE1_HEAD
        self.board[snake[1][0]][snake[1][1]] = SNAKE0 if player == SNAKE0 else SNAKE1
        # tail
        tail_x, tail_y = snake[-1][0], snake[-1][1]
        self.board[tail_x][tail_y] = SNAKE0_TAIL if player == SNAKE0 else SNAKE1_TAIL

    def __game_over(self):
        self.done = True

    def __lose(self, player):
        if self.winner is None:
            if player == SNAKE0:
                self.winner = SNAKE1
            else:
                self.winner = SNAKE0
        elif self.winner == player:
            self.winner = None
        self.__game_over()

# demo
# if __name__ == "__main__":
#     import random

#     game = Reversi()
#     while not game.done:
#         game.render()
#         available_action = game.available_action()
#         if len(available_action) > 0:
#             action = random.choice(game.available_action())
#         else:
#             action = -1 # no position to step
#         game.step(action)
#     game.render()
#     black_score, white_score = game.reward(BLACK), game.reward(WHITE)
#     print("BLACK:", black_score, "WHITE:", white_score)
#     if black_score == white_score:
#         print("DRAW")
#     elif black_score > white_score:
#         print("BLACK wins")
#     else:
#         print("WHITE wins")
