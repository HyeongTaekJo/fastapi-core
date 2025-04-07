from fastapi import APIRouter,Request, Depends, HTTPException, status
from typing import List
from user.repository import UserRepository
from user.model.model import UserModel
from user.schemas.response import UserSchema, UserListSchema

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
async def get_users(
    userRepository: UserRepository = Depends(UserRepository)
):
 
    users : List[UserModel] = await userRepository.get_users()
    return UserListSchema(
        users=[UserSchema.model_validate(user) for user in users]
    )


@router.get("/email/{email}")
async def get_user_by_email(
    email: str,
    userRepository: UserRepository = Depends(UserRepository)
):
    user : UserModel = await userRepository.get_user_by_email(email)

    if user:
        return UserSchema.model_validate(user)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="존재하지 않는 User 입니다.")

@router.get("/id/{id}")
async def get_user_by_id(
    id: int,
    userRepository: UserRepository = Depends(UserRepository)
):
    user : UserModel = await userRepository.get_user_by_id(id)

    if user:
        return UserSchema.model_validate(user)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="존재하지 않는 User2 입니다.")
