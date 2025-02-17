import models


class print_queue_singleton:
    instance = None
    data = []

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super().__new__(cls)
            return cls.instance
        else:
            return cls.instance


def init():
    global print_queue
    print_queue = []


def queue_push(print_job):
    print_queue.append(print_job)


def queue_pop(print_job):
    return print_queue.pop(print_job)


def get_job(queue_position):
    return print_queue[queue_position]


def get_queue_size():
    return len(print_queue)
