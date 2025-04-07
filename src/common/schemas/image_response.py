# common/schemas/response.py 등 적절한 위치에 생성
from pydantic import BaseModel, computed_field, field_serializer
from common.model.image_model import ImageModelType
from common.const.path_consts import POST_PUBLIC_IMAGE_PATH

class ImageSchema(BaseModel):
    path: str
    order: int
    type: ImageModelType

    @field_serializer("path")
    def serialize_path(self, path: str, info) -> str:
        # path 값을 "/public/posts/..." 형태로 변경
        if self.type == ImageModelType.POST_IMAGE:
            return f"/{POST_PUBLIC_IMAGE_PATH}/{path}".replace("\\", "/")
        return path


    class Config:
        from_attributes = True