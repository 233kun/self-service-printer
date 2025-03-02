class print_queue_singleton:
    instance = None
    data = []

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super().__new__(cls)
            return cls.instance
        else:
            return cls.instance