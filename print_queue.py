import models


def init():
    global print_queue
    print_queue = []
    global test


def queue_push(print_job):
    print_queue.append(print_job)


def queue_pop(print_job):
    print_queue.pop(print_job)


def queue_remove(print_job):
    print_queue.remove(print_job)


def get_job(queue_position):
    return print_queue[queue_position]


def get_queue_size():
    return len(print_queue)
