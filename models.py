from pydantic import BaseModel


class FileModel:
    filename: str
    convert_state: str
    total_pages: int
    print_copies: int
    print_range_start: int
    print_range_end: int
    print_side: str

    def __init__(self):
        self.print_copies = 1
        self.print_range_start = 1
        self.print_side = "one-sided"


class FileList(BaseModel):
    fileList: list


class FileBill(FileModel):
    price: float

    def __init__(self):
        super().__init__()
        self.price = 0.0


class ReturnResult:
    code: int
    message: str
    data: dict

    def __init__(self, code, message, data):
        self.code = code
        self.message = message
        self.data = data
