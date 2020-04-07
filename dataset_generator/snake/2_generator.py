import os
import sys
import json
import copy
import numpy as np

DIR = [(-1, 0), (0, 1), (1, 0), (0, -1)]
EMPTY, OBSTACLE = 0, 9
SNAKE0, SNAKE0_HEAD, SNAKE0_TAIL = 1, 2, 3
SNAKE1, SNAKE1_HEAD, SNAKE1_TAIL = -1, -2, -3


class SnakeDataGenerator:
    def __init__(self, init_data):
        self.init_data = json.loads(init_data)
        self.round = 0
        self.game_map, self.snake0, self.snake1 = self.init_map()
        
    def init_map(self):
        self.height, self.width = self.init_data["height"], self.init_data["width"]
        game_map = [[EMPTY] * self.height for _ in range(self.width)]
        for obstacle in self.init_data["obstacle"]:
            y, x = obstacle["x"], obstacle["y"]
            game_map[x - 1][y - 1] = OBSTACLE
        
        snake0, snake1 = [], []
        snake0_init, snake1_init = self.init_data["0"], self.init_data["1"]
        snake0.append((snake0_init["x"], snake0_init["y"]))
        game_map[snake0_init["y"] - 1][snake0_init["x"] - 1] = SNAKE0_HEAD
        snake1.append((snake1_init["x"], snake1_init["y"]))
        game_map[snake1_init["y"] - 1][snake1_init["x"] - 1] = SNAKE1_HEAD

        return game_map, snake0, snake1

    def get_state_action(self, resp):
        # snake0
        state0 = copy.deepcopy(self.game_map)
        action0 = resp["0"]
        # snake1
        state1 = copy.deepcopy(self.game_map)
        for i in range(self.width):
            for j in range(self.height):
                if state1[i][j] != EMPTY and state1[i][j] != OBSTACLE:
                    state1[i][j] *= -1
        action1 = resp["1"]

        # handle response
        # snake0
        x0, y0 = self.snake0[0][0], self.snake0[0][1]
        self.game_map[y0 - 1][x0 - 1] = SNAKE0
        self.snake0.insert(0, (x0 + DIR[action0][0], y0 + DIR[action0][1]))
        self.game_map[y0 + DIR[action0][1] - 1][x0 + DIR[action0][0] - 1] = SNAKE0_HEAD
        # snake1
        x1, y1 = self.snake1[0][0], self.snake1[0][1]
        self.game_map[y1 - 1][x1 - 1] = SNAKE1
        self.snake1.insert(0, (x1 + DIR[action1][0], y1 + DIR[action1][1]))
        self.game_map[y1 + DIR[action1][1] - 1][x1 + DIR[action1][0] - 1] = SNAKE1_HEAD

        if self.round > 9 and (self.round - 9) % 3 != 0:
            self.game_map[self.snake0[-1][1] - 1][self.snake0[-1][0] - 1] = EMPTY
            self.snake0.pop(-1)
            self.game_map[self.snake1[-1][1] - 1][self.snake1[-1][0] - 1] = EMPTY
            self.snake1.pop(-1)
        
        self.game_map[self.snake0[-1][1] - 1][self.snake0[-1][0] - 1] = SNAKE0_TAIL
        self.game_map[self.snake1[-1][1] - 1][self.snake1[-1][0] - 1] = SNAKE1_TAIL

        self.round += 1

        return {"0": state0, "1": state1}, {"0": action0, "1": action1}


def generate_data(path, bot_id):
    rounds, states, actions = [], [], []
    with open(path) as fp:
        matches = fp.readlines()
        for match_str in matches:
            try:
                match_round = 0
                match = json.loads(match_str)
                bot0, bot1 = match["players"][0]["bot"], match["players"][1]["bot"]
                if bot0 != bot_id and bot1 != bot_id:
                    continue
                index = "0" if bot0 == bot_id else "1"
                print("match_id:", match["_id"], "bot_id:", bot_id)

                init_data = match["initdata"]
                generator = SnakeDataGenerator(init_data)
                for i in range(1, len(match["log"]), 2):
                    responses = {snake: match["log"][i][snake]["response"]["direction"] for snake in ("0", "1")}
                    state, action = generator.get_state_action(responses)
                    # for r in state[index]:
                    #     print(r)
                    # print(action[index])
                    rounds.append(copy.deepcopy(match_round))
                    states.append(copy.deepcopy(state[index]))
                    actions.append(copy.deepcopy(action[index]))
                    
                    match_round += 1
            except Exception as e:
                pass
    return rounds, states, actions


if __name__ == "__main__":
    game = "Snake"

    bot_id = str(sys.argv[1])
    print("bot_id:", bot_id)

    for year in (2015, 2016, 2017, 2018, 2019, 2020):
        r, s, a = [], [], []
        for month in range(1, 12 + 1):
            directory = "./{game}-{year}-{month}".format(game=game, year=year, month=month)
            if not os.path.exists(directory):
                continue
            number_files = len(os.listdir(directory))
            i = 0
            for filename in os.listdir(directory):
                print("{current}/{total}, {year}.{month} processed...".format(current=i, total=number_files, year=year, month=month))
                absolute_path = os.path.join(directory, filename)
                rounds, states, actions = generate_data(absolute_path, bot_id)
                r, s, a = copy.deepcopy(r + rounds), copy.deepcopy(s + states), copy.deepcopy(a + actions)
                i += 1
        r, s, a = np.array(r), np.array(s), np.array(a)
        np.savez("{bot_id}-{year}.npz".format(bot_id=bot_id, year=year), round=r, state=s, action=a)
