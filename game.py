from functools import cmp_to_key

from apple import Apple
from configs import *
from field import Field
from player import Player


def comp(x, y):
    if x[0] < y[0]:
        return -1
    elif x[0] > y[0]:
        return 1
    elif x[1] > y[1]:
        return 1
    elif x[1] < y[1]:
        return -1
    else:
        return 0


class Game:
    def __init__(self, field_size=(80, 24), players=1):
        super(Game, self).__init__()
        self.__field = Field(*field_size)
        self.__players = [Player(*field_size, i + 1, POSSIBLE_PLAYERS + 1) for i in range(POSSIBLE_PLAYERS)]
        self.__players_alive = players
        for player in self.__players[players:]:
            player.die()
        snakes = set()
        for snake in self.__players:
            snakes |= snake.get_body()
            snakes.update({snake.get_head()})
        self.__apple = Apple(*field_size, snakes)
        self.o_b_o = [0 for i in self.__players]
        self.in_loop = True

    def run(self, dt=0.5):
        if self.__players_alive != 0:
            for snake in self.__players:
                snake.move()
            self.__check_collisions()

    def __check_collisions(self):
        # variables
        blue_snake = self.__players[0]
        red_snake = self.__players[1]
        walls = set()
        snakes = set()
        for snake in self.__players:
            walls |= snake.get_body()
            snakes |= {snake.get_head()}
        snakes |= walls
        need_apple = False
        # food check
        for snake in self.__players:
            if snake.get_head() == self.__apple.get_coord():
                snake.eat()
                need_apple = True
        if need_apple:
            self.__apple.gen_apple(snakes)
        # die. problem with heads. in future i can do smth with that
        if blue_snake.get_head() == red_snake.get_head():
            red_snake.die()
            blue_snake.die()
            self.__players_alive -= 2
            return
        for snake in self.__players:
            if snake.is_alive():
                if (snake.get_head() in walls) or \
                        self.__field.not_on_field(snake.get_head()):
                    snake.die()
                    self.__players_alive -= 1

    def key_pressed(self, key):
        self.__players[key[0]].change_direction(key[1])

    def finish(self):
        self.__players_alive = 0

    def reset(self, field_size=(80, 24), players=1):
        self.__field = Field(*field_size)
        self.__players = [Player(*field_size, i + 1, POSSIBLE_PLAYERS + 1) for i in range(POSSIBLE_PLAYERS)]
        self.__players_alive = players
        for player in self.__players[players:]:
            player.die()
        snakes = set()
        for snake in self.__players:
            snakes |= snake.get_body()
            snakes.update({snake.get_head()})
        self.__apple = Apple(*field_size, snakes)
        self.in_loop = True

    def paint(self):
        if self.__players_alive != 0:
            blue_snake = self.__players[0]
            red_snake = self.__players[1]
            blue_snake.draw_snake(blue_body_pic, blue_head_pics)
            red_snake.draw_snake(red_body_pic, red_head_pics)
            apple = pyglet.sprite.Sprite(apple_pic,
                                         x=self.__apple.get_coord()[0] * BLOCK_SIZE[0],
                                         y=self.__apple.get_coord()[1] * BLOCK_SIZE[1])
            apple.update(scale_x=SCALE_X, scale_y=SCALE_Y)
            apple.draw()
        else:
            self.__end_screen()

    def __end_screen(self):
        winners = []
        score = []
        for i in range(POSSIBLE_PLAYERS):
            score.append((self.__players[i].get_score(),
                          self.__players[i].life, i + 1))
        score = sorted(score, key=cmp_to_key(comp), reverse=True)
        for pl in score:
            if (pl[0] == score[0][0]) and (pl[1] == score[0][1]):
                winners.append(str(pl[2]))
                if self.in_loop:
                    self.o_b_o[pl[2] - 1] += 1
        self.in_loop = False

        text = ', '.join(winners)
        if len(winners) != 1:
            text = 'Draw! ' + text + ' best'
        else:
            text = 'Player ' + text + ' win'
        label1 = pyglet.text.Label(text,
                                   font_name='Times New Roman',
                                   font_size=72,
                                   x=300, y=600)
        label1.draw()
        label2 = pyglet.text.Label(f'Score: {score[0][0]}',
                                   font_name='Times New Roman',
                                   font_size=72,
                                   x=300, y=400)
        label2.draw()
        label3 = pyglet.text.Label(':'.join([str(sc) for sc in self.o_b_o]),
                                   font_name='Times New Roman',
                                   font_size=72,
                                   x=300, y=200)
        label3.draw()
