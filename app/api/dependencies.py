# app/api/dependencies.py (only the get_current_user function needs to be updated)

async def get_current_user(
    request: Request, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> UserModel:
    """
    Dependency: Gets the current user from the JWT token.  Raises exceptions on failure.
    The subject claim ('sub') in the token could be either a username or an email.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        subject: str = payload.get("sub")  # Get username or email from "sub" claim
        if subject is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_repo = UserRepository(db)
    
    # First try to get user by username
    user = user_repo.get_by_username(subject)
    
    # If not found, try by email
    if user is None:
        user = user_repo.get_by_email(subject)
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return user