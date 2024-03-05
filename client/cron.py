from threading import Timer
import time


def printHello():
    print("Hello")
    print("当前时间戳是", time.time())


def loop_func(func, second):
    # 每隔second秒执行func函数
    while True:
        timer = Timer(second, func)
        timer.start()
        timer.join()


loop_func(printHello, 5)
loop_func(printHello, 5)
loop_func(printHello, 5)
loop_func(printHello, 5)
loop_func(printHello, 5)
