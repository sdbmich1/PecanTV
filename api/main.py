from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
from dotenv import load_dotenv

from database import get_db
import models
import schemas
import crud

# Load environment variables
load_dotenv()

app = FastAPI(
    title="PecanTV API",
    description="API for PecanTV streaming service",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to PecanTV API"}

@app.get("/content", response_model=List[schemas.Content])
def get_content(
    skip: int = 0,
    limit: int = 100,
    type: str = None,
    genre: str = None,
    db: Session = Depends(get_db)
):
    """Get all content with optional filtering"""
    return crud.get_content(db, skip=skip, limit=limit, type=type, genre=genre)

@app.get("/content/{content_id}", response_model=schemas.Content)
def get_content_by_id(content_id: int, db: Session = Depends(get_db)):
    """Get specific content by ID"""
    content = crud.get_content_by_id(db, content_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found")
    return content

@app.get("/genres", response_model=List[schemas.Genre])
def get_genres(db: Session = Depends(get_db)):
    """Get all genres"""
    return crud.get_genres(db)

@app.get("/ratings", response_model=List[schemas.Rating])
def get_ratings(db: Session = Depends(get_db)):
    """Get all ratings"""
    return crud.get_ratings(db)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 