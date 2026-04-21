"""
Rutas de Álbumes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.models import Album
from core.schemas import AlbumCreate, AlbumResponse, AlbumUpdate
from core.security import get_current_user

router = APIRouter(prefix="/api/v1/albums", tags=["albums"])


@router.get("/", response_model=List[AlbumResponse])
async def get_albums(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Listar álbumes con paginación"""
    albums = db.query(Album).offset(skip).limit(limit).all()
    return albums


@router.get("/{album_id}", response_model=AlbumResponse)
async def get_album(
    album_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un álbum por ID"""
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Álbum no encontrado"
        )
    return album


@router.post("/", response_model=AlbumResponse, status_code=status.HTTP_201_CREATED)
async def create_album(
    album: AlbumCreate,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear un nuevo álbum — requiere autenticación"""
    db_album = Album(**album.model_dump())
    db.add(db_album)
    db.commit()
    db.refresh(db_album)
    return db_album


@router.patch("/{album_id}", response_model=AlbumResponse)
async def update_album(
    album_id: int,
    updates: AlbumUpdate,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar un álbum — requiere autenticación"""
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Álbum no encontrado"
        )

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(album, field, value)

    db.commit()
    db.refresh(album)
    return album


@router.delete("/{album_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_album(
    album_id: int,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar un álbum — requiere autenticación"""
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Álbum no encontrado"
        )
    db.delete(album)
    db.commit()