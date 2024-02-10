def init():
    global _global_dict
    _global_dict = {}


def global_var_setter(key, var):
    _global_dict[key] = var

    # _global_dict.update({key: ""})
    # _global_dict.update({key: var})


def global_var_getter(key):
    return _global_dict[key]