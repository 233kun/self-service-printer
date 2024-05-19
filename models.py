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


class ReturnResult:
    code: int
    message: str
    data: str