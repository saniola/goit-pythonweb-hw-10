from fastapi import APIRouter, Depends, Request, File, UploadFile, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from schemas import User
from services.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User
from database.db import get_db
from services.upload_file import UploadFileService
from conf.config import settings
from services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)

@router.get(
  "/me", response_model=User, description="No more than 10 requests per minute"
)
@limiter.limit("10/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
  return user

@router.patch("/avatar", response_model=User, description="Update user avatar")
async def update_avatar(
    file: UploadFile = File(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, current_user.username)

    user_service = UserService(db)
    return await user_service.update_avatar_url(current_user.email, avatar_url)
