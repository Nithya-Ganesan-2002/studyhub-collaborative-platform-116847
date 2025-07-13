from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# -------- USER SCHEMAS --------
# PUBLIC_INTERFACE
class UserBase(BaseModel):
    username: str = Field(..., description="Unique username for the user")
    email: EmailStr

# PUBLIC_INTERFACE
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

# PUBLIC_INTERFACE
class UserOut(UserBase):
    id: int
    bio: Optional[str]
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

# -------- DECK SCHEMAS --------
# PUBLIC_INTERFACE
class DeckBase(BaseModel):
    title: str
    description: Optional[str] = None

# PUBLIC_INTERFACE
class DeckCreate(DeckBase):
    is_public: Optional[bool] = False

# PUBLIC_INTERFACE
class DeckOut(DeckBase):
    id: int
    owner_id: int
    is_public: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# -------- NOTE SCHEMAS --------
# PUBLIC_INTERFACE
class NoteBase(BaseModel):
    title: str
    content: str

# PUBLIC_INTERFACE
class NoteCreate(NoteBase):
    pass

# PUBLIC_INTERFACE
class NoteOut(NoteBase):
    id: int
    deck_id: int
    author_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# -------- SHARING SCHEMAS --------
# PUBLIC_INTERFACE
class DeckShareBase(BaseModel):
    user_id: int
    permission: str = Field(..., description="'read' or 'write' permission only.")

# PUBLIC_INTERFACE
class DeckShareCreate(DeckShareBase):
    pass

# PUBLIC_INTERFACE
class DeckShareOut(DeckShareBase):
    id: int
    deck_id: int
    shared_at: datetime

    class Config:
        from_attributes = True

# -------- LIKE SCHEMAS --------
# PUBLIC_INTERFACE
class LikeOut(BaseModel):
    id: int
    deck_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# -------- COMMENT SCHEMAS --------
# PUBLIC_INTERFACE
class CommentBase(BaseModel):
    content: str

# PUBLIC_INTERFACE
class CommentCreate(CommentBase):
    deck_id: Optional[int] = None
    note_id: Optional[int] = None

# PUBLIC_INTERFACE
class CommentOut(CommentBase):
    id: int
    user_id: int
    deck_id: Optional[int]
    note_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
