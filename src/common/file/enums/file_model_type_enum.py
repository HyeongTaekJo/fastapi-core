from enum import Enum

class FileModelType(str, Enum):
    IMAGE = "IMAGE"
    PDF = "PDF"
    EXCEL = "EXCEL"
    PPT = "PPT"
    WORD = "WORD"
    HWP = "HWP"
    OTHER = "OTHER"
