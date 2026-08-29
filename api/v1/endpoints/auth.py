from database import get_db
from schemas import UserCreate, UserResponse, TokenResponse
from crud import create_user, authenticate_user, get_user_emal, get_user_username
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from core.security import create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from service.email import send_welcome_email
router = APIRouter(prefix="/auth", tags=["AUTH"])

@router.post("/register", response_model=UserResponse, description="Register")
def register(user: UserCreate, db:Session=Depends(get_db)):
    existing_user = get_user_username(db, user.username)
    existing_email = get_user_emal(db, user.email)

    if existing_user or existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or Email is already registered"
        )

    db_user = create_user(db, user)
    
    # Send welcome email with error handling
    try:
        send_welcome_email(db_user.email, db_user.username)
        print(f"Welcome email sent to {db_user.email}")
    except Exception as e:
        print(f"Welcome email failed: {e}")
        # Don't fail registration if email fails

    return db_user

@router.post("/login", response_model=TokenResponse, description="User Login")
def login(request: OAuth2PasswordRequestForm = Depends(), db:Session=Depends(get_db)):
    user = authenticate_user(db, request.username, request.password)

    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = create_access_token({"sub": str(user.id)})
    return {
        "access_token": token,
        "token_type": "bearer"
    }