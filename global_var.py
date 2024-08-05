import models


def init():
    global _global_dict
    _global_dict = {}


def global_var_setter(key, var):
    _global_dict[key] = var
    # _global_dict.update({key: ""})
    # _global_dict.update({key: var})


def global_var_getter(key):
    # try:
    return _global_dict[key]
    # except:
    #     print('读取' + key + '失败\r\n')
    #     return "error"


def global_var_isKey_exist(key):
    return key in _global_dict


def free_var(key):
    _global_dict.pop(key)
