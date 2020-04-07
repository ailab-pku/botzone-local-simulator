import os
import sys
import json
import copy
import numpy as np
from pacman import Pacman


class PacmanDataGenerator:
    def __init__(self, init_data):
        self.init_data = json.loads(init_data)
        self.game = Pacman(
            seed=self.init_data["seed"], height=self.init_data["height"], width=self.init_data["width"], 
            generator_interval=self.init_data["GENERATOR_INTERVAL"], 
            large_fruit_duration=self.init_data["LARGE_FRUIT_DURATION"], 
            large_fruit_enhancement=self.init_data["LARGE_FRUIT_ENHANCEMENT"], 
            static=self.init_data["static"], content=self.init_data["content"])

    def get_state_action(self, resp):
        action0, action1, action2, action3 = resp["0"], resp["1"], resp["2"], resp["3"]
        states = {player: copy.deepcopy(self.game.state()) for player in ("0", "1", "2", "3")}
        actions = {"0": action0, "1": action1, "2": action2, "3": action3}
        self.game.step([action0, action1, action2, action3])
        return states, actions


def generate_data(path, bot_id):
    rounds, roles, states, actions = [], [], [], []
    with open(path) as fp:
        matches = fp.readlines()
        for match_str in matches:
            try:
                match_round = 0
                match = json.loads(match_str)
                bot0, bot1, bot2, bot3 = \
                    match["players"][0].get("bot", ""), match["players"][1].get("bot", ""), match["players"][2].get("bot", ""), match["players"][3].get("bot", "")
                if bot0 != bot_id and bot1 != bot_id and bot2 != bot_id and bot3 != bot_id:
                    continue
                if bot0 == bot_id:
                    index = "0"
                elif bot1 == bot_id:
                    index = "1"
                elif bot2 == bot_id:
                    index = "2"
                else:
                    index = "3"
                print("match_id:", match["_id"], "bot_id:", bot_id)

                init_data = match["initdata"]
                generator = PacmanDataGenerator(init_data)
                for i in range(1, len(match["log"]), 2):
                    responses = {
                        player: match["log"][i].get(player, {"response": {"action": -1}})["response"]["action"] 
                        for player in ("0", "1", "2", "3")}
                    state, action = generator.get_state_action(responses)
                    rounds.append(copy.deepcopy(match_round))
                    roles.append(copy.deepcopy(int(index)))
                    states.append(copy.deepcopy(state[index]))
                    actions.append(copy.deepcopy(action[index]))
                    
                    match_round += 1
            except Exception as e:
                pass
    return rounds, roles, states, actions


if __name__ == "__main__":
    game = "Pacman"

    bot_id = str(sys.argv[1])
    print("bot_id:", bot_id)

    for year in (2015, 2016, 2017, 2018, 2019, 2020):
        r1, r2, s, a = [], [], [], []
        for month in range(1, 12 + 1):
            directory = "./{game}-{year}-{month}".format(game=game, year=year, month=month)
            if not os.path.exists(directory):
                continue
            number_files = len(os.listdir(directory))
            i = 0
            for filename in os.listdir(directory):
                print("{current}/{total}, {year}.{month} processed...".format(current=i, total=number_files, year=year, month=month))
                absolute_path = os.path.join(directory, filename)
                rounds, roles, states, actions = generate_data(absolute_path, bot_id)
                r1, r2, s, a = copy.deepcopy(r1 + rounds), copy.deepcopy(r2 + roles), copy.deepcopy(s + states), copy.deepcopy(a + actions)
                i += 1
        r1, r2, s, a = np.array(r1), np.array(r2), np.array(s), np.array(a)
        np.savez("{bot_id}-{year}.npz".format(bot_id=bot_id, year=year), round=r1, role=r2, state=s, action=a)
