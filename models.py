from pydantic import BaseModel


class FileModel:
    filename: str
    convert_state: str
    total_pages: int
    print_copies: int
    print_range_start: int
    print_range_end: int
    print_side: str
    folder: str

    def __init__(self):
        self.print_copies = 1
        self.print_range_start = 1
        self.print_side = "one-sided"


class JwtToken(BaseModel):
    token: object


class FileList(BaseModel):
    fileList: list


class FileBill(FileModel):
    price: float

    def __init__(self):
        super().__init__()
        self.price = 0.0


class RemoveFilename(BaseModel):
    filename: str


class UpdateJob(BaseModel):
    bill_attributes: str


class UpdateState(BaseModel):
    filename: str
    path: str
    state: str
    authorization: str


class ReturnResult:
    code: int
    message: str
    data: dict

    def __init__(self, code, message, data):
        self.code = code
        self.message = message
        self.data = data


class GlobalVar:
    _global_var: dict

    def __init__(self):
        self._global_dict = {}

    def setter(self, key, value):
        self._global_dict[key] = value

    def getter(self, key):
        return self._global_dict[key]

    def getAll(self):
        return self._global_dict

    def free(self, key):
        del self._global_dict[key]
