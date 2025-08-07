from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserLogin  # Pydantic schemas for request validation
from app.models.user import User  # SQLAlchemy User model
from app.db import SessionLocal, get_db  # Database session factory
from app.auth.jwt_handler import hash_password, create_access_token  # Password hashing & JWT creation
from app.utils.hashing import verify_password  # Password verification
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()  # Creates a router for authentication endpoints

# Dependency to get a database session for each request
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db  # Provide the session to the request
#     finally:
#         db.close()  # Ensure the session is closed after the request

def authenticate_user(username: str, password: str, db: Session):
    user = db.query(User).filter(User.email == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# User registration endpoint
@router.post('/register')
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists by email
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create a new user with hashed password
    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    
    db.add(new_user)      # Add new user to the session
    db.commit()           # Commit transaction to save user
    db.refresh(new_user)  # Refresh instance to get new user ID
    
    return {
        "message": "User created successfully",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email
        }
    }

# User login endpoint
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}