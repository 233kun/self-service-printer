def init():
    global print_queue
    print_queue = []


def queue_push(print_task):
    print_queue.append(print_task)


def queue_pop(print_task):
    print_queue.pop(print_task)


def get_task(queue_position):
    return print_queue[queue_position]
