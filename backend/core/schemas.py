"""
Esquemas Pydantic para validación
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# Usuario
class UserBase(BaseModel):
    """Schema base para usuario"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema para crear usuario"""
    password: str

class UserUpdate(BaseModel):
    """Solo los campos que el usuario puede actualizar"""
    full_name: Optional[str] = None

class UserResponse(UserBase):
    """Schema de respuesta para usuario"""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Álbum
class AlbumBase(BaseModel):
    """Schema base para álbum"""
    title: str
    artist: str
    release_year: Optional[int] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None


class AlbumCreate(AlbumBase):
    """Schema para crear álbum"""
    pass

class AlbumUpdate(BaseModel):
    """"Todos los campos son opcionales para actualización"""
    title: Optional[str] = None
    artist: Optional[str] = None
    release_year: Optional[int] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None

class AlbumResponse(AlbumBase):
    """Schema de respuesta para álbum"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Canción
class SongBase(BaseModel):
    """Schema base para canción"""
    title: str
    artist: str
    album_id: Optional[int] = None
    duration: Optional[int] = None


class SongCreate(SongBase):
    """Schema para crear canción"""
    pass

class SongUpdate(BaseModel):
    """Todos los campos son opcionales para actualización"""
    title: Optional[str] = None
    artist: Optional[str] = None
    album_id: Optional[int] = None
    duration: Optional[int] = None

class SongResponse(SongBase):
    """Schema de respuesta para canción"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Reseña
class ReviewBase(BaseModel):
    """Schema base para reseña"""
    rating: float
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    """Schema para crear reseña"""
    album_id: Optional[int] = None
    song_id: Optional[int] = None


class ReviewResponse(ReviewBase):
    """Schema de respuesta para reseña"""
    id: int
    user_id: int
    album_id: Optional[int] = None
    song_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
