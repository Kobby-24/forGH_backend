from fastapi import Depends,HTTPException,status
from typing import Annotated
import token_utils as tk
from fastapi.security import OAuth2PasswordBearer
 


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    return tk.verify_token(token,credentials_exception)

async def get_admin_user(current_user: Annotated[str, Depends(get_current_user)]):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have enough privileges",
        )
    return current_user
    
    

