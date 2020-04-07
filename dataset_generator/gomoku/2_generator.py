import os
import sys
import json
import copy
import numpy as np


class GomokuDataGenerator:
    def __init__(self):
        self.board_size = 15
        self.current_player = 1
        self.board = [[0] * self.board_size for _ in range(self.board_size)]

    def get_state_action(self, resp):
        state = copy.deepcopy(self.board)
        # if self.current_player == -1:
        #     for i in range(self.board_size):
        #         for j in range(self.board_size):
        #             state[i][j] *= -1
        player = self.current_player
        x, y = resp["response"]["x"], resp["response"]["y"]
        self.board[y][x] = self.current_player
        self.current_player *= -1
        return player, state, y * self.board_size + x


def generate_data(path, bot_id):
    roles, states, actions = [], [], []
    with open(path) as fp:
        matches = fp.readlines()
        for match_str in matches:
            try:
                match = json.loads(match_str)
                bot0, bot1 = match["players"][0]["bot"], match["players"][1]["bot"]
                if bot0 != bot_id and bot1 != bot_id:
                    continue
                index = "0" if bot0 == bot_id else "1"
                print("match_id:", match["_id"], "bot_id:", bot_id)

                generator = GomokuDataGenerator()
                for i in range(1, len(match["log"]), 2):
                    player = list(match["log"][i].keys())[0]
                    response = match["log"][i][player]
                    role, state, action = generator.get_state_action(response)
                    if player == index:
                        roles.append(copy.deepcopy(role))
                        states.append(copy.deepcopy(state))
                        actions.append(copy.deepcopy(action))
            except Exception as e:
                pass
    return roles,states, actions


if __name__ == "__main__":
    game = "Gomoku"

    bot_id = str(sys.argv[1])
    print("bot_id:", bot_id)

    for year in (2018, 2019, 2020):
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
                roles, states, actions = generate_data(absolute_path, bot_id)
                r, s, a = copy.deepcopy(r + roles), copy.deepcopy(s + states), copy.deepcopy(a + actions)
                i += 1
        r, s, a = np.array(r), np.array(s), np.array(a)
        np.savez("{bot_id}-{year}.npz".format(bot_id=bot_id, year=year), role=r, state=s, action=a)
