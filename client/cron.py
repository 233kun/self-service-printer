from threading import Timer
import time


def loop_function(func, second):
    while True:
        timer = Timer(second, func)
        timer.start()
        timer.join()  # 