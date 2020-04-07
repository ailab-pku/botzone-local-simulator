# -*- coding: utf-8 -*-
import copy
import json
import random
import time

DX = [0, 1, 0, -1, 1, 1, -1, -1]
DY = [-1, 0, 1, 0, -1, 1, 1, -1]

STATIC_EMPTY = 0
STATIC_NORTH_WALL = 1
STATIC_EAST_WALL = 2
STATIC_SOUTH_WALL = 4
STATIC_WEST_WALL = 8
STATIC_GENERATOR = 16

CONTENT_EMPTY = 0
CONTENT_PLAYER1 = 1
CONTENT_PLAYER2 = 2
CONTENT_PLAYER3 = 4
CONTENT_PLAYER4 = 8
CONTENT_PLAYER_MASK = 1 | 2 | 4 | 8
CONTENT_SMALL_FRUIT = 16
CONTENT_LARGE_FRUIT = 32
PLAYER_ID_MASK = [CONTENT_PLAYER1, CONTENT_PLAYER2, CONTENT_PLAYER3, CONTENT_PLAYER4]

DIRECTION_STAY = -1
DIRECTION_UP = 0
DIRECTION_RIGHT = 1
DIRECTION_DOWN = 2
DIRECTION_LEFT = 3
DIRECTION_UR = 4
DIRECTION_DR = 5
DIRECTION_DL = 6
DIRECTION_UL = 7
DIRECTION_WALL = [STATIC_NORTH_WALL, STATIC_EAST_WALL, STATIC_SOUTH_WALL, STATIC_WEST_WALL]

DIRECTION_ENUMERATE_LIST = [
    [DIRECTION_UP, DIRECTION_RIGHT, DIRECTION_DOWN, DIRECTION_LEFT],
    [DIRECTION_UP, DIRECTION_RIGHT, DIRECTION_LEFT, DIRECTION_DOWN],
    [DIRECTION_UP, DIRECTION_DOWN, DIRECTION_RIGHT, DIRECTION_LEFT],
    [DIRECTION_UP, DIRECTION_DOWN, DIRECTION_LEFT, DIRECTION_RIGHT],
    [DIRECTION_UP, DIRECTION_LEFT, DIRECTION_RIGHT, DIRECTION_DOWN],
    [DIRECTION_UP, DIRECTION_LEFT, DIRECTION_DOWN, DIRECTION_RIGHT],
    [DIRECTION_RIGHT, DIRECTION_UP, DIRECTION_DOWN, DIRECTION_LEFT],
    [DIRECTION_RIGHT, DIRECTION_UP, DIRECTION_LEFT, DIRECTION_DOWN],
    [DIRECTION_RIGHT, DIRECTION_DOWN, DIRECTION_UP, DIRECTION_LEFT],
    [DIRECTION_RIGHT, DIRECTION_DOWN, DIRECTION_LEFT, DIRECTION_UP],
    [DIRECTION_RIGHT, DIRECTION_LEFT, DIRECTION_UP, DIRECTION_DOWN],
    [DIRECTION_RIGHT, DIRECTION_LEFT, DIRECTION_DOWN, DIRECTION_UP],
    [DIRECTION_DOWN, DIRECTION_UP, DIRECTION_RIGHT, DIRECTION_LEFT],
    [DIRECTION_DOWN, DIRECTION_UP, DIRECTION_LEFT, DIRECTION_RIGHT],
    [DIRECTION_DOWN, DIRECTION_RIGHT, DIRECTION_UP, DIRECTION_LEFT],
    [DIRECTION_DOWN, DIRECTION_RIGHT, DIRECTION_LEFT, DIRECTION_UP],
    [DIRECTION_DOWN, DIRECTION_LEFT, DIRECTION_UP, DIRECTION_RIGHT],
    [DIRECTION_DOWN, DIRECTION_LEFT, DIRECTION_RIGHT, DIRECTION_UP],
    [DIRECTION_LEFT, DIRECTION_UP, DIRECTION_RIGHT, DIRECTION_DOWN],
    [DIRECTION_LEFT, DIRECTION_UP, DIRECTION_DOWN, DIRECTION_RIGHT],
    [DIRECTION_LEFT, DIRECTION_RIGHT, DIRECTION_UP, DIRECTION_DOWN],
    [DIRECTION_LEFT, DIRECTION_RIGHT, DIRECTION_DOWN, DIRECTION_UP],
    [DIRECTION_LEFT, DIRECTION_DOWN, DIRECTION_UP, DIRECTION_RIGHT],
    [DIRECTION_LEFT, DIRECTION_DOWN, DIRECTION_RIGHT, DIRECTION_UP]
]


class PacmanPlayer:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.power_up_left = 0
        self.strength = 1
        self.dead = False


class Pacman:
    visited = None
    unvisited_count = None
    border_broken = None

    def __init__(
        self, seed=None, height=None, width=None, 
        generator_interval=None, large_fruit_duration=None, 
        large_fruit_enhancement=None, 
        static=None, content=None):
        self.seed = seed if seed is not None else int(time.time())
        random.seed(self.seed)
        self.height = height if height is not None else random.randint(0, 11)
        self.width = width if width is not None else random.randint(6, 11)
        self.generator_interval = generator_interval if generator_interval is not None else 20
        self.generator_turn_left = self.generator_interval
        self.large_fruit_duration = large_fruit_duration if large_fruit_duration is not None else 10
        self.large_fruit_enhancement = large_fruit_enhancement if large_fruit_enhancement is not None else 10

        self.static = [[STATIC_EMPTY] * self.width for _ in range(self.height)]
        self.content = [[CONTENT_EMPTY] * self.width for _ in range(self.height)]
        self.small_fruit_count, self.generator_count, self.alive_count = 0, 0, 0
        self.generators, self.players = [], []
        if static is not None and content is not None:
            self.__prepare_init_field(static, content)
        else:
            self.__init_field()
        self.static_copy, self.content_copy = copy.deepcopy(self.static), copy.deepcopy(self.content)
        self.round = 0
        self.winner = None
        self.done = False
        self.last_actions = None
    
    def state(self):
        state = {
            "players": [{"strength": self.players[_].strength, "power_up_left": self.players[_].power_up_left, "dead": self.players[_].dead} for _ in range(4)],
            "content": copy.deepcopy(self.content), 
            "static": copy.deepcopy(self.static),
            "generator_interval": self.generator_interval,
            "large_fruit_duration": self.large_fruit_duration,
            "large_fruit_enhancement": self.large_fruit_enhancement
        }
        return json.dumps(state)

    def reward(self, player):
        if self.done is False:
            return 0
        return 1 if player == self.winner else -1

    def reset(self):
        self.__prepare_init_field(self.static_copy, self.content_copy)
        self.generator_turn_left = self.generator_interval
        self.round = 0
        self.winner = None
        self.done = False
        self.last_actions = None

    def render(self):
        print(self.state())
    
    def __prepare_init_field(self, static, content):
        for r in range(self.height):
            for c in range(self.width):
                self.static[r][c] = static[r][c]
                self.content[r][c] = content[r][c]
                if self.static[r][c] & STATIC_GENERATOR:
                    self.generators.append((r, c))
                    self.generator_count += 1
                if self.content[r][c] & CONTENT_SMALL_FRUIT:
                    self.small_fruit_count += 1
                for i in range(4):
                    if self.content[r][c] & PLAYER_ID_MASK[i]:
                        self.players.append(PacmanPlayer(r, c))
                        self.alive_count += 1
    
    def __ensure_connected(self, r, c, height, width):
        Pacman.visited[r][c] = True
        Pacman.unvisited_count -= 1
        if Pacman.unvisited_count == 0:
            return True
        direction_list = random.choice(DIRECTION_ENUMERATE_LIST)
        for direction in direction_list:
            next_r, next_c = r + DY[direction], c + DX[direction]
            if next_r >= 0 and next_r < height and next_c >= 0 and next_c < width:
                if Pacman.visited[next_r][next_c] is False:
                    if self.static[next_r][next_c] & STATIC_GENERATOR:
                        Pacman.visited[next_r][next_c] = True
                        Pacman.unvisited_count -= 1
                        if Pacman.unvisited_count == 0:
                            return True
                        continue
                    self.static[r][c] &= ~DIRECTION_WALL[direction]
                    if direction == DIRECTION_UP:
                        self.static[next_r][next_c] &= ~STATIC_SOUTH_WALL
                    if direction == DIRECTION_DOWN:
                        self.static[next_r][next_c] &= ~STATIC_NORTH_WALL
                    if direction == DIRECTION_LEFT:
                        self.static[next_r][next_c] &= ~STATIC_EAST_WALL
                    if direction == DIRECTION_RIGHT:
                        self.static[next_r][next_c] &= ~STATIC_WEST_WALL
                    if self.__ensure_connected(next_r, next_c, height, width) is True:
                        return True
            elif Pacman.border_broken[direction] is False:
                Pacman.border_broken[direction] = True
                self.static[r][c] &= ~DIRECTION_WALL[direction]
        return False
    
    def __init_field(self):
        portion_x, portion_y = (self.height + 1) // 2, (self.width + 1) // 2
        for i in range(portion_x):
            for j in range(portion_y):
                self.static[i][j] = STATIC_NORTH_WALL | STATIC_EAST_WALL | STATIC_SOUTH_WALL | STATIC_WEST_WALL
        Pacman.unvisited_count = portion_x * portion_y
        # generator
        generator_x, generator_y = random.randint(0, portion_x - 2), random.randint(0, portion_y - 2)
        self.static[generator_x][generator_y] = STATIC_GENERATOR
        self.static[generator_x][self.width - 1 - generator_y] = STATIC_GENERATOR
        self.static[self.height - 1 - generator_x][generator_y] = STATIC_GENERATOR
        self.static[self.height - 1 - generator_x][self.width - 1 - generator_y] = STATIC_GENERATOR
        # connect regions
        Pacman.visited = [[False] * 12 for _ in range(12)]
        Pacman.border_broken = [False] * 4
        self.__ensure_connected(random.randint(0, portion_x - 1), random.randomint(0, portion_y - 1), portion_x, portion_y)
        if Pacman.border_broken[DIRECTION_LEFT] is False:
            self.static[random.randint(0, portion_x - 1)][0] &= ~STATIC_WEST_WALL
        if Pacman.border_broken[DIRECTION_RIGHT] is False:
            self.static[random.randint(0, portion_x - 1)][portion_y - 1] &= ~STATIC_EAST_WALL
        if Pacman.border_broken[DIRECTION_UP] is False:
            self.static[0][random.randint(0, portion_y - 1)] &= ~STATIC_NORTH_WALL
        if Pacman.border_broken[DIRECTION_DOWN] is False:
            self.static[portion_x - 1][random.randint(0, portion_y - 1)] &= ~STATIC_SOUTH_WALL
        # generate symmetric field
        for r in range(portion_x):
            for c in range(portion_y):
                n = bool(self.static[r][c] & STATIC_NORTH_WALL)
                e = bool(self.static[r][c] & STATIC_EAST_WALL)
                s = bool(self.static[r][c] & STATIC_SOUTH_WALL)
                w = bool(self.static[r][c] & STATIC_WEST_WALL)
                has_generator = bool(self.static[r][c] & STATIC_GENERATOR)
                if (c == 0 or c == portion_y - 1) and random.randint(0, 3) % 4 == 0:
                    if c == 0:
                        w = False
                    else:
                        e = False
                if (r == 0 or r == portion_x - 1) and random.randint(0, 3) % 4 == 0:
                    if r == 0:
                        n = False
                    else:
                        s = False
                if r * 2 + 1 == self.height:
                    s = n
                if c * 2 + 1 == self.width:
                    e = w
                self.static[r][c] = has_generator | (STATIC_NORTH_WALL if n else STATIC_EMPTY) | (STATIC_EAST_WALL if e else STATIC_EMPTY) | (STATIC_SOUTH_WALL if s else STATIC_EMPTY) | (STATIC_WEST_WALL if w else STATIC_EMPTY)
                self.static[r][self.width - 1 - c] = has_generator | (STATIC_NORTH_WALL if n else STATIC_EMPTY) | (STATIC_EAST_WALL if w else STATIC_EMPTY) | (STATIC_SOUTH_WALL if s else STATIC_EMPTY) | (STATIC_WEST_WALL if e else STATIC_EMPTY)
                self.static[self.height - 1 - r][c] = has_generator | (STATIC_NORTH_WALL if s else STATIC_EMPTY) | (STATIC_EAST_WALL if e else STATIC_EMPTY) | (STATIC_SOUTH_WALL if n else STATIC_EMPTY) | (STATIC_WEST_WALL if w else STATIC_EMPTY)
                self.static[self.height - 1 - r][self.width - 1 - c] = has_generator | (STATIC_NORTH_WALL if s else STATIC_EMPTY) | (STATIC_EAST_WALL if w else STATIC_EMPTY) | (STATIC_SOUTH_WALL if n else STATIC_EMPTY) | (STATIC_WEST_WALL if e else STATIC_EMPTY)
                self.content[r][c] = self.content[r][self.width - 1 - c] = self.content[self.height - 1 - r][c] = self.content[self.height - 1 - r][self.width - 1 - c] = CONTENT_EMPTY
        # wrap all generator
        for r in range(self.height):
            for c in range(self.width):
                if self.static[r][c] & STATIC_GENERATOR:
                    self.static[r][c] |= STATIC_NORTH_WALL | STATIC_EAST_WALL | STATIC_SOUTH_WALL | STATIC_WEST_WALL
                    for direction in (DIRECTION_UP, DIRECTION_RIGHT, DIRECTION_DOWN, DIRECTION_LEFT):
                        temp = self.static[(r + DY[direction] + self.height) % self.height][(c + DX[direction] + self.width) % self.width]
                        if direction == DIRECTION_UP:
                            temp |= STATIC_SOUTH_WALL
                        if direction == DIRECTION_RIGHT:
                            temp |= STATIC_WEST_WALL
                        if direction == DIRECTION_DOWN:
                            temp |= STATIC_NORTH_WALL
                        if direction == DIRECTION_LEFT:
                            temp |= STATIC_EAST_WALL
                        self.static[(r + DY[direction] + self.height) % self.height][(c + DX[direction] + self.width) % self.width] = temp
        # generate players
        while True:
            r, c = random.randint(0, portion_x - 1 - 1), random.randint(0, portion_y - 1 - 1)
            if self.static[r][c] & STATIC_GENERATOR:
                continue
            self.content[r][c] |= CONTENT_PLAYER1
            self.content[r][self.width -1 - c] |= CONTENT_PLAYER2
            self.content[self.height - 1 - r][c] |= CONTENT_PLAYER3
            self.content[self.height - 1 - r][self.width - 1 - c] |= CONTENT_PLAYER4
            break
        # generate large fruit
        while True:
            r, c = random.randint(0, portion_x - 1 - 1), random.randint(0, portion_y - 1 - 1)
            if (self.static[r][c] & STATIC_GENERATOR) or (self.content[r][c] & CONTENT_PLAYER1):
                continue
            self.content[r][c] |= CONTENT_LARGE_FRUIT
            self.content[r][self.width -1 - c] |= CONTENT_LARGE_FRUIT
            self.content[self.height - 1 - r][c] |= CONTENT_LARGE_FRUIT
            self.content[self.height - 1 - r][self.width - 1 - c] |= CONTENT_LARGE_FRUIT
            break
        # generate small fruit
        for r in range(portion_x - 1):
            for c in range(portion_y - 1):
                if (self.static[r][c] & STATIC_GENERATOR) or (self.content[r][c] & (CONTENT_PLAYER1 | CONTENT_LARGE_FRUIT)) or (random.random.randint(0, 2) % 3 != 0):
                    continue
                self.content[r][c] = self.content[r][self.width - 1 - c] = self.content[self.height - 1 - r][c] = self.content[self.height - 1 - r][self.width - 1 - c] = CONTENT_SMALL_FRUIT
                self.small_fruit_count += 1
        # collect filed information
        for r in range(self.height):
            for c in range(self.width):
                if self.static[r][c] & STATIC_GENERATOR:
                    self.generators.append((r, c))
                    self.generator_count += 1
                for i in range(4):
                    if self.content[r][c] & PLAYER_ID_MASK[i]:
                        self.players.append(PacmanPlayer(r, c))
                        self.alive_count += 1
    
    def __valid_action(self, player_id, action):
        if action == DIRECTION_STAY:
            return True
        player = self.players[player_id]
        return action >= DIRECTION_STAY and action <= DIRECTION_LEFT and \
            not (self.static[player.x][player.y] & DIRECTION_WALL[action]) and \
                not (self.static[(player.x + DY[action] + self.height) % self.height][(player.y + DX[action] + self.width) % self.width] & STATIC_GENERATOR)
    
    def step(self, actions):
        # invalid action
        for _ in range(4):
            player = self.players[_]
            if player.dead is False:
                action = actions[_]
                if action == DIRECTION_STAY:
                    continue
                if self.__valid_action(_, action) is False:
                    self.content[player.x][player.y] &= ~PLAYER_ID_MASK[_]
                    self.players[_].strength = 0
                    self.players[_].dead = True
                    self.alive_count -= 1
                else:
                    target = self.content[(player.x + DY[action] + self.height) % self.height][(player.y + DX[action] + self.width) % self.width]
                    if target & CONTENT_PLAYER_MASK:
                        for i in range(4):
                            if (target & PLAYER_ID_MASK[i]) and self.players[i].strength > player.strength:
                                actions[_] = DIRECTION_STAY
        # move
        for _ in range(4):
            player = self.players[_]
            if player.dead is True:
                continue
            action = actions[_]
            if action == DIRECTION_STAY:
                continue
            self.content[player.x][player.y] &= ~PLAYER_ID_MASK[_]
            self.players[_].x = (self.players[_].x + DY[action] + self.height) % self.height
            self.players[_].y = (self.players[_].y + DX[action] + self.width) % self.width
            self.content[player.x][player.y] |= PLAYER_ID_MASK[_]
        # battle
        for _ in range(4):
            player = self.players[_]
            if player.dead is True:
                continue
            # multiple players in one position
            current_position_players = []
            for i in range(4):
                if self.content[player.x][player.y] & PLAYER_ID_MASK[i]:
                    current_position_players.append(i)
            if len(current_position_players) > 1:
                for i in range(len(current_position_players)):
                    for j in range(len(current_position_players) - i - 1):
                        if self.players[current_position_players[j]].strength < self.players[current_position_players[j + 1]].strength:
                            current_position_players[j], current_position_players[j + 1] = current_position_players[j + 1], current_position_players[j]
                begin = 1
                while begin < len(current_position_players):
                    if self.players[current_position_players[begin - 1]].strength > self.players[current_position_players[begin]].strength:
                        break
                    begin += 1
                looted_strength = 0
                for i in range(begin, len(current_position_players)):
                    player_id = current_position_players[i]
                    tmp_player = self.players[player_id]
                    self.content[tmp_player.x][tmp_player.y] &= ~PLAYER_ID_MASK[player_id]
                    self.players[player_id].dead = True
                    self.alive_count -= 1
                    drop = tmp_player.strength // 2
                    self.players[player_id].strength -= drop
                    looted_strength += drop
                increase = looted_strength // begin
                for i in range(begin):
                    player_id = current_position_players[i]
                    self.players[player_id].strength += increase
        # generate fruit
        self.generator_turn_left -= 1
        if self.generator_turn_left == 0:
            self.generator_turn_left = self.generator_interval

            for i in range(self.generator_count):
                for direction in range(8):
                    r, c = (self.generators[i][0] + DY[direction] + self.height) % self.height, (self.generators[i][1] + DX[direction] + self.width) % self.width
                    if (self.static[r][c] & STATIC_GENERATOR) or (self.content[r][c] & (CONTENT_SMALL_FRUIT | CONTENT_LARGE_FRUIT)):
                        continue
                    self.content[r][c] |= CONTENT_SMALL_FRUIT
                    self.small_fruit_count += 1
        # eat fruit
        for _ in range(4):
            player = self.players[_]
            if player.dead is True:
                continue
            c = self.content[player.x][player.y]
            if c & CONTENT_PLAYER_MASK & ~PLAYER_ID_MASK[_]:
                continue
            if c & CONTENT_SMALL_FRUIT:
                self.content[player.x][player.y] &= ~CONTENT_SMALL_FRUIT
                self.players[_].strength += 1
                self.small_fruit_count -= 1
            elif c & CONTENT_LARGE_FRUIT:
                self.content[player.x][player.y] &= ~CONTENT_LARGE_FRUIT
                if player.power_up_left == 0:
                    self.players[_].strength += self.large_fruit_enhancement
                self.players[_].power_up_left += self.large_fruit_duration
        # large fruit duration decrease
        for _ in range(4):
            player = self.players[_]
            if player.dead is True:
                continue
            if player.power_up_left == 1:
                self.players[_].strength -= self.large_fruit_enhancement
            if player.power_up_left > 0:
                self.players[_].power_up_left -= 1

        self.last_actions = actions
        self.round += 1
        # only one player alive
        if self.alive_count <= 1:
            for _ in range(4):
                if self.players[_].dead is False:
                    self.players[_].strength += self.small_fruit_count
            self.__game_over()
        # round reach limit
        if self.round >= 100:
            self.__game_over()
    
    def __game_over(self):
        self.done = True
        for _ in range(4):
            if self.players[_].dead is False:
                self.winner = _
                return
        self.winner = None
