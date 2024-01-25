from etherlight import Etherlight
import time
from random import randint
import copy
from threading import Thread

etherlight = Etherlight("192.168.1.254")

FIELD_LENGTH = 24


class DinoGame:

    def __int__(self):
        print("init")
        self.field = [' ' for x in range(FIELD_LENGTH)]
        self.jump = 0
        self.will_jump = False
        self.old_display = self.get_display()
        self.running = False

    def get_display(self):
        display = copy.deepcopy([[' ' for x in range(FIELD_LENGTH)], self.field])
        if '-' not in self.field:
            if self.jump > 0:
                display[0][1] = 'D'
            else:
                display[1][1] = 'D'
        return display

    def update(self):
        if '-' in self.field:
            self.running = False
            time.sleep(1)
            for i in range(48):
                etherlight.set_led_color(i + 1, [255, 0, 0])
            etherlight.flush()
            return
        self.field.pop(0)
        self.field.append(' ')
        space = randint(3, 8)
        try:
            last = self.field[::-1].index("x")
        except ValueError:
            last = FIELD_LENGTH
        if last > space:
            self.field[-1] = 'x'
        if self.will_jump:
            self.jump = 2
            self.will_jump = False
        if self.jump > 0:
            self.jump -= 1
        if self.field[1] == 'x' and self.jump == 0:
            self.field[1] = '-'

    def do_jump(self):
        self.jump = 2
        self.draw()

    def draw(self, force_all=False):
        display = self.get_display()
        print("=====")
        print(display[0])
        print(display[1])
        print("=====")
        for y in range(2):
            for x in range(FIELD_LENGTH):
                if display[y][x] != self.old_display[y][x] or force_all:
                    led = 2 * x + y + 1
                    if display[y][x] == ' ':
                        etherlight.set_led_color(led, [0, 0, 0])
                    elif display[y][x] == 'x':
                        etherlight.set_led_color(led, [0, 255, 0])
                    elif display[y][x] == 'D':
                        etherlight.set_led_color(led, [0, 0, 255])
                    elif display[y][x] == '-':
                        etherlight.set_led_color(led, [255, 0, 0])
        etherlight.flush()
        self.old_display = copy.deepcopy(display)

    def run(self):
        self.draw(True)
        time.sleep(2)
        self.running = True
        while self.running:
            self.update()
            self.draw()
            time.sleep(0.3)


dinogame = DinoGame()
dinogame.__int__()

thread = Thread(target=dinogame.run)
thread.start()

while True:
    input()
    dinogame.do_jump()
