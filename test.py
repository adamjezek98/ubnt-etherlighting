from random import randint
import time
from etherlight import Etherlight

#

etherlight = Etherlight("10.0.10.6")
time.sleep(2)
# for i in range(48):
#     etherlight.set_led_color(i + 1, (0, 10, 0))
#     # time.sleep(0.1)
# etherlight.flush()

# time.sleep(5)
# for _i in range(15):
#     for c in [(10, 0, 0), (0, 10, 0), (0, 0, 10)]:
#         for i in range(48):
#             etherlight.cache_led_color(i + 1, c)
#         etherlight.flush_led_cache()
while True:
    for i in range(52):
        etherlight.set_led_color(i + 1, (randint(0, 255), randint(0, 255), randint(0, 255)))
    etherlight.flush()
print("done")
