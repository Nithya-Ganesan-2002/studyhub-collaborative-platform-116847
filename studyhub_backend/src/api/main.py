from fastapi import FastAPI, HTTPException, status, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from src.api.db import models, schemas, session

app = FastAPI(
    title="StudyHub Backend API",
    version="1.0.0",
    description="REST API for StudyHub collaborative study platform"
)

# Allow cross-origin for frontend; adjust in production!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"message": "Healthy"}



# ------------------ USER ENDPOINTS ------------------

from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

# PUBLIC_INTERFACE
@app.post("/users/", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(session.get_db)):
    """
    Create a new user.
    """
    hashed_password = generate_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username or email already exists")
    return db_user

# PUBLIC_INTERFACE
@app.get("/users/", response_model=List[schemas.UserOut], tags=["Users"])
def list_users(skip: int = 0, limit: int = 10, db: Session = Depends(session.get_db)):
    """
    List all users (paginated).
    """
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

# PUBLIC_INTERFACE
@app.get("/users/{user_id}", response_model=schemas.UserOut, tags=["Users"])
def get_user(user_id: int, db: Session = Depends(session.get_db)):
    """
    Retrieve a user by their ID.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# -------- USER PROFILE --------
# PUBLIC_INTERFACE
@app.get("/profile/{user_id}", response_model=schemas.UserOut, tags=["Profile"])
def user_profile(user_id: int, db: Session = Depends(session.get_db)):
    """
    Get profile for a user by user_id.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ------------------ DECK ENDPOINTS ------------------
# PUBLIC_INTERFACE
@app.post("/decks/", response_model=schemas.DeckOut, status_code=201, tags=["Decks"])
def create_deck(deck: schemas.DeckCreate, owner_id: int = Query(...), db: Session = Depends(session.get_db)):
    """
    Create a new deck for the given owner.
    """
    db_deck = models.Deck(
        title=deck.title,
        description=deck.description,
        owner_id=owner_id,
        is_public=deck.is_public
    )
    db.add(db_deck)
    db.commit()
    db.refresh(db_deck)
    return db_deck

# PUBLIC_INTERFACE
@app.get("/decks/", response_model=List[schemas.DeckOut], tags=["Decks"])
def list_decks(
    skip: int = 0, limit: int = 10, 
    public_only: bool = False, 
    owner_id: Optional[int] = None,
    db: Session = Depends(session.get_db)):
    """
    List decks (optionally filter by owner or public only).
    """
    query = db.query(models.Deck)
    if public_only:
        query = query.filter(models.Deck.is_public == True)
    if owner_id:
        query = query.filter(models.Deck.owner_id == owner_id)
    decks = query.offset(skip).limit(limit).all()
    return decks

# PUBLIC_INTERFACE
@app.get("/decks/{deck_id}", response_model=schemas.DeckOut, tags=["Decks"])
def get_deck(deck_id: int, db: Session = Depends(session.get_db)):
    """
    Get a specific deck by id.
    """
    deck = db.query(models.Deck).filter(models.Deck.id == deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    return deck

# PUBLIC_INTERFACE
@app.put("/decks/{deck_id}", response_model=schemas.DeckOut, tags=["Decks"])
def update_deck(deck_id: int, deck: schemas.DeckCreate, db: Session = Depends(session.get_db)):
    """
    Update a deck by deck id.
    """
    db_deck = db.query(models.Deck).filter(models.Deck.id == deck_id).first()
    if not db_deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    db_deck.title = deck.title
    db_deck.description = deck.description
    db_deck.is_public = deck.is_public if deck.is_public is not None else db_deck.is_public
    db.commit()
    db.refresh(db_deck)
    return db_deck

# PUBLIC_INTERFACE
@app.delete("/decks/{deck_id}", status_code=204, tags=["Decks"])
def delete_deck(deck_id: int, db: Session = Depends(session.get_db)):
    """
    Delete a deck by id.
    """
    db_deck = db.query(models.Deck).filter(models.Deck.id == deck_id).first()
    if db_deck is None:
        raise HTTPException(status_code=404, detail="Deck not found")
    db.delete(db_deck)
    db.commit()
    return


# ------------------ NOTE ENDPOINTS ------------------
# PUBLIC_INTERFACE
@app.post("/decks/{deck_id}/notes/", response_model=schemas.NoteOut, status_code=201, tags=["Notes"])
def create_note(deck_id: int, note: schemas.NoteCreate, author_id: int = Query(...), db: Session = Depends(session.get_db)):
    """
    Create a note in a deck.
    """
    db_note = models.Note(
        deck_id=deck_id,
        title=note.title,
        content=note.content,
        author_id=author_id
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

# PUBLIC_INTERFACE
@app.get("/decks/{deck_id}/notes/", response_model=List[schemas.NoteOut], tags=["Notes"])
def list_notes(deck_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(session.get_db)):
    """
    List all notes for a deck.
    """
    notes = db.query(models.Note).filter(models.Note.deck_id == deck_id).offset(skip).limit(limit).all()
    return notes

# PUBLIC_INTERFACE
@app.get("/notes/{note_id}", response_model=schemas.NoteOut, tags=["Notes"])
def get_note(note_id: int, db: Session = Depends(session.get_db)):
    """
    Get a specific note by id.
    """
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

# PUBLIC_INTERFACE
@app.put("/notes/{note_id}", response_model=schemas.NoteOut, tags=["Notes"])
def update_note(note_id: int, note: schemas.NoteCreate, db: Session = Depends(session.get_db)):
    """
    Update a note.
    """
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    db_note.title = note.title
    db_note.content = note.content
    db.commit()
    db.refresh(db_note)
    return db_note

# PUBLIC_INTERFACE
@app.delete("/notes/{note_id}", status_code=204, tags=["Notes"])
def delete_note(note_id: int, db: Session = Depends(session.get_db)):
    """
    Delete a note by id.
    """
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(db_note)
    db.commit()
    return


# ------------------ SHARING/PERMISSIONS ENDPOINTS ------------------
# PUBLIC_INTERFACE
@app.post("/decks/{deck_id}/shares/", response_model=schemas.DeckShareOut, status_code=201, tags=["Sharing"])
def share_deck(deck_id: int, share: schemas.DeckShareCreate, db: Session = Depends(session.get_db)):
    """
    Share a deck with a user.
    """
    share_entry = models.DeckShare(
        deck_id=deck_id,
        user_id=share.user_id,
        permission=share.permission
    )
    db.add(share_entry)
    try:
        db.commit()
        db.refresh(share_entry)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Share for this user/deck already exists")
    return share_entry

# PUBLIC_INTERFACE
@app.get("/decks/{deck_id}/shares/", response_model=List[schemas.DeckShareOut], tags=["Sharing"])
def list_shares(deck_id: int, db: Session = Depends(session.get_db)):
    """
    List all shares for a deck.
    """
    return db.query(models.DeckShare).filter(models.DeckShare.deck_id == deck_id).all()

# PUBLIC_INTERFACE
@app.delete("/shares/{share_id}", status_code=204, tags=["Sharing"])
def delete_share(share_id: int, db: Session = Depends(session.get_db)):
    """
    Remove sharing for a user/deck.
    """
    share = db.query(models.DeckShare).filter(models.DeckShare.id == share_id).first()
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
    db.delete(share)
    db.commit()
    return


# ------------------ LIKE ENDPOINTS ------------------
# PUBLIC_INTERFACE
@app.post("/decks/{deck_id}/like/", response_model=schemas.LikeOut, status_code=201, tags=["Likes"])
def like_deck(deck_id: int, user_id: int = Query(...), db: Session = Depends(session.get_db)):
    """
    Like a deck. Each user can like a deck once.
    """
    like = models.Like(
        deck_id=deck_id,
        user_id=user_id
    )
    db.add(like)
    try:
        db.commit()
        db.refresh(like)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Already liked")
    return like

# PUBLIC_INTERFACE
@app.get("/decks/{deck_id}/likes/", response_model=List[schemas.LikeOut], tags=["Likes"])
def get_deck_likes(deck_id: int, db: Session = Depends(session.get_db)):
    """
    Retrieve all likes for a deck.
    """
    likes = db.query(models.Like).filter(models.Like.deck_id == deck_id).all()
    return likes

# PUBLIC_INTERFACE
@app.delete("/likes/{like_id}", status_code=204, tags=["Likes"])
def remove_like(like_id: int, db: Session = Depends(session.get_db)):
    """
    Remove (unlike) a deck by like id.
    """
    like = db.query(models.Like).filter(models.Like.id == like_id).first()
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")
    db.delete(like)
    db.commit()
    return


# ------------------ COMMENT ENDPOINTS ------------------
# PUBLIC_INTERFACE
@app.post("/comments/", response_model=schemas.CommentOut, status_code=201, tags=["Comments"])
def add_comment(comment: schemas.CommentCreate, user_id: int = Query(...), db: Session = Depends(session.get_db)):
    """
    Add a comment to a deck or note.
    """
    if not (comment.deck_id or comment.note_id):
        raise HTTPException(status_code=400, detail="Specify deck_id or note_id")
    db_comment = models.Comment(
        content=comment.content,
        user_id=user_id,
        deck_id=comment.deck_id,
        note_id=comment.note_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

# PUBLIC_INTERFACE
@app.get("/comments/", response_model=List[schemas.CommentOut], tags=["Comments"])
def list_comments(deck_id: Optional[int] = None, note_id: Optional[int] = None, db: Session = Depends(session.get_db)):
    """
    List comments for a specific deck or note.
    """
    query = db.query(models.Comment)
    if deck_id:
        query = query.filter(models.Comment.deck_id == deck_id)
    if note_id:
        query = query.filter(models.Comment.note_id == note_id)
    return query.all()

# PUBLIC_INTERFACE
@app.delete("/comments/{comment_id}", status_code=204, tags=["Comments"])
def delete_comment(comment_id: int, db: Session = Depends(session.get_db)):
    """
    Delete a comment.
    """
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    db.delete(comment)
    db.commit()
    return


# ------------------ SEARCH ENDPOINTS ------------------
# PUBLIC_INTERFACE
@app.get("/search/", tags=["Search"])
def search(
    q: str = Query(..., description="Search query"),
    limit: int = 10,
    db: Session = Depends(session.get_db)
):
    """
    Search decks or notes by title/content.
    """
    deck_results = db.query(models.Deck).filter(models.Deck.title.ilike(f"%{q}%")).limit(limit).all()
    note_results = db.query(models.Note).filter(
        (models.Note.title.ilike(f"%{q}%")) |
        (models.Note.content.ilike(f"%{q}%"))
    ).limit(limit).all()
    return {
        "decks": deck_results,
        "notes": note_results
    }
