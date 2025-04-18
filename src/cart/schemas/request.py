from pydantic import BaseModel

class AddCartSchema(BaseModel):
    product_id: int
    quantity: int

class UpdateCartSchema(BaseModel):
    product_id: int
    quantity: int

class RemoveCartSchema(BaseModel):
    product_id: int
