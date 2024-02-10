from etherlight import Etherlight
import time
from random import randint
import copy
from threading import Thread
# import readchar
import subprocess

ETHERLIGHTS = ["10.0.10.36", "10.0.10.6"]


class SnakeGame:

    def __int__(self):
        self.FIELD_WIDTH = 24
        self.FIELD_HEIGHT = 2 * len(ETHERLIGHTS)
        self.etherlights = [Etherlight(ip) for ip in ETHERLIGHTS]
        self.head = [0, 0]
        self.tail = []
        self.direction = 'R'
        self.user_direction = None
        self.fruit = [0, 0]
        self.delay = 0.2
        # self.spawn_fruit()
        self.display = self.get_display()
        self.old_display = copy.deepcopy(self.display)
        self.running = False
        self.reset_game()

    def reset_game(self):
        self.head = [0, 0]
        self.tail = []
        self.direction = 'R'
        self.user_direction = None
        self.spawn_fruit()
        self.display = self.get_display()
        self.old_display = copy.deepcopy(self.display)
        self.running = False

    def spawn_fruit(self):
        while True:
            fruit = [randint(0, self.FIELD_WIDTH - 1), randint(0, self.FIELD_HEIGHT - 1)]
            if fruit not in self.tail and fruit != self.head:
                self.fruit = fruit
                break

    def get_display(self):
        display = [['x' for x in range(self.FIELD_WIDTH)] for y in range(self.FIELD_HEIGHT)]
        display[self.fruit[1]][self.fruit[0]] = 'F'
        for i in self.tail:
            display[i[1]][i[0]] = self.tail.index(i) + 1
        display[self.head[1]][self.head[0]] = 'H'

        return display

    def move(self):
        self.tail.insert(0, copy.deepcopy(self.head))
        old_head = self.head
        if self.direction == 'D':
            self.head[1] += 1
        elif self.direction == 'U':
            self.head[1] -= 1
        elif self.direction == 'L':
            self.head[0] -= 1
        elif self.direction == 'R':
            self.head[0] += 1
        if self.head == self.fruit:
            print("Eating")
            self.spawn_fruit()
        else:
            self.tail.pop()
            if self.head in self.tail:
                print("Collision")
                return False
        if self.head[0] < 0 or self.head[0] >= self.FIELD_WIDTH or self.head[1] < 0 or self.head[
            1] >= self.FIELD_HEIGHT:
            print("Out of bounds")
            return False

        return True

    def draw(self):
        self.display = self.get_display()
        print(
            f"=== dir {self.direction}/{self.user_direction}; head {self.head}; fruit {self.fruit}; tail {self.tail} ===")
        for line in self.display:
            # print("".join(line))
            print(line)
        self.update_etherlight()
        print("===")

    def update_etherlight(self, force_all=False):
        if force_all:
            self.old_display = [['x' for x in range(self.FIELD_WIDTH)] for y in range(self.FIELD_HEIGHT)]
        for y in range(self.FIELD_HEIGHT):
            for x in range(self.FIELD_WIDTH):
                if self.display[y][x] != self.old_display[y][x] or force_all:
                    etherlight = self.etherlights[int(y / 2)]
                    if y % 2:
                        led = (x * 2) + 2
                    else:
                        led = (x * 2) + 1

                    if self.display[y][x] == 'x':
                        etherlight.set_led_color(led, [0, 0, 0])
                    elif self.display[y][x] == 'T':
                        etherlight.set_led_color(led, [0, 255, 0])
                    elif self.display[y][x] == 'H':
                        etherlight.set_led_color(led, [0, 0, 255])
                    elif self.display[y][x] == 'F':
                        etherlight.set_led_color(led, [255, 0, 0])
                    else:
                        t = self.display[y][x]
                        if t > 25:
                            t = 25
                        etherlight.set_led_color(led, [0, t * 10, 155 - t * 5])
        for etherlight in self.etherlights:
            etherlight.flush()
        self.old_display = copy.deepcopy(self.display)

    def set_direction(self, direction):
        valid_directions = {
            "U": ("L", "R"),
            "D": ("L", "R"),
            "L": ("U", "D"),
            "R": ("U", "D")

        }
        if direction in valid_directions[self.direction]:
            self.user_direction = direction

    def wait_for_direction(self):
        start_time = time.time()
        while start_time + self.delay > time.time():
            if self.user_direction:
                self.direction = self.user_direction
                self.user_direction = None
                return self.delay - (time.time() - start_time)

    def run(self):
        self.running = True
        self.update_etherlight(True)
        time.sleep(1.5)
        while self.running:
            delay = self.wait_for_direction()
            if not self.move():
                for etherlight in self.etherlights:
                    for i in range(48):
                        etherlight.set_led_color(i + 1, (255, 0, 0))
                    etherlight.flush()
                self.running = False
                break
            self.draw()
            # if delay:
            #     # print("Delaying", delay)
            #     time.sleep(delay)


snakegame = SnakeGame()
snakegame.__int__()


def rungame():
    snakegame.reset_game()
    time.sleep(0.5)
    thread = Thread(target=snakegame.run)
    thread.start()


def process_event(event):
    joystick_threshold = 31000
    if event['type'] == '1' and snakegame.running is False:
        print("restarting game")
        time.sleep(1)
        rungame()
    if event['type'] == '2':
        if event['number'] == '0' or event['number'] == '6':
            if event['value'] > joystick_threshold:
                snakegame.set_direction('R')
            elif event['value'] < -joystick_threshold:
                snakegame.set_direction('L')
        elif event['number'] == '1' or event['number'] == '7':
            if event['value'] > joystick_threshold:
                snakegame.set_direction('D')
            elif event['value'] < -joystick_threshold:
                snakegame.set_direction('U')


proc = subprocess.Popen(['jstest', '--event', '/dev/input/js0'], stdout=subprocess.PIPE)

while True:
    line = proc.stdout.readline().decode("utf-8").strip()
    if line.startswith("Event:"):
        line = line.split("Event: ")[1]
        event = {}
        for i in line.split(","):
            i = i.strip()
            key, value = i.split(" ")
            event[key.strip()] = value.strip()
        event["value"] = int(event["value"])
        print(event)
        process_event(event)

# while True:
#     direction = readchar.readchar()
#     # print("got direction", direction)
#     if direction == 'w':
#         snakegame.set_direction('U')
#     elif direction == 's':
#         snakegame.set_direction('D')
#     elif direction == 'a':
#         snakegame.set_direction('L')
#     elif direction == 'd':
#         snakegame.set_direction('R')
#     elif direction == 'q':
#         snakegame.running = False
#         break
