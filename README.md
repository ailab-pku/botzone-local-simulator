# botzone-local-simulator
Botzone本地模拟器及对局数据产生器

游戏：黑白棋 (Reversi)、五子棋 (Gomoku)、贪吃蛇 (Snake)、吃豆人 (Pacman)

## 本地模拟器

目录：`botzone-local-simulator/games/`

#### Demo

```python
# -*- coding: utf-8 -*-
import random
from reversi import Reversi

if __name__ == "__main__":
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

```

## 对局数据产生器

目录：`botzone-local-simulator/dataset_generator/`

- `1_download.py`：从Botzone上下载某个游戏的全部数据（log）
- `2_generator.py`：从下载的数据中筛选出指定bot的对局并生成对局数据
- `run.sh`：并行生成对局数据

