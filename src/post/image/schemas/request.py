from common.model.image_model import ImageModelType
from pydantic import BaseModel, Field

class CreatePostImageSchema(BaseModel):
    path: str
    order: int
    type: ImageModelType
    post_id: int  # PostModel 객체 대신 ID만 받도록 수정