from fastapi import Form, File, UploadFile
from typing import Optional, Union, List

class CreatePostForm:
    def __init__(
        self,
        title: str = Form(...),
        content: str = Form(...),
        files: Optional[Union[UploadFile, List[UploadFile]]] = File(None),  # 👈 핵심
    ):
        self.title = title
        self.content = content

        # 파일을 리스트로 통일해서 내부적으로 항상 동일하게 처리 가능
        if files is None:
            self.files = []
        elif isinstance(files, list):
            self.files = files
        else:
            self.files = [files]
