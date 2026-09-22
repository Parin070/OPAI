from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from database import engine, get_db
import models
import schemas
import auth
import storage
import ml_client

app = FastAPI(title="StyleSync Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Ensure pgvector extension exists
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    # Initialize MinIO bucket
    storage.init_bucket()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/auth/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.post("/items/upload", response_model=schemas.ClothingItemResponse)
async def upload_item(
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # Read file once into memory
    file_bytes = await file.read()
    
    # 1. Upload to MinIO
    filename = f"{current_user.id}/{file.filename}"
    file_url = storage.upload_image_to_minio(file_bytes, filename, file.content_type)
    
    # 2. Get embeddings and tags from ML service
    ml_result = await ml_client.analyze_image_with_ml(file_bytes, filename, file.content_type)
    
    # 3. Save to database
    item = models.ClothingItem(
        user_id=current_user.id,
        image_url=file_url,
        category=ml_result["attributes"].get("category"),
        color=ml_result["attributes"].get("color"),
        pattern=ml_result["attributes"].get("pattern"),
        season=ml_result["attributes"].get("season"),
        formality_score=ml_result["attributes"].get("formality_score"),
        embedding=ml_result["embedding"]
    )
    
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@app.get("/items", response_model=List[schemas.ClothingItemResponse])
def get_user_items(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    items = db.query(models.ClothingItem).filter(models.ClothingItem.user_id == current_user.id).all()
    
    # Fix URLs for older items that were saved with internal Docker networking URLs
    import os
    internal_url = os.environ.get("MINIO_URL", "http://minio:9000")
    public_url = os.environ.get("MINIO_PUBLIC_URL", "http://localhost:9000")
    for item in items:
        if item.image_url and item.image_url.startswith(internal_url):
            item.image_url = item.image_url.replace(internal_url, public_url)
            
    return items
