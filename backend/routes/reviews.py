"""
Rutas de Canciones
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.models import Song, Album
from core.schemas import SongCreate, SongResponse, SongUpdate
from core.security import get_current_user

router = APIRouter(prefix="/api/v1/songs", tags=["songs"])


@router.get("/", response_model=List[SongResponse])
async def get_songs(
    skip: int = 0,
    limit: int = 20,
    album_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Listar canciones con paginación.
    Opcionalmente filtrar por álbum con ?album_id=1
    """
    query = db.query(Song)
    if album_id:
        query = query.filter(Song.album_id == album_id)
    songs = query.offset(skip).limit(limit).all()
    return songs


@router.get("/{song_id}", response_model=SongResponse)
async def get_song(
    song_id: int,
    db: Session = Depends(get_db)
):
    """Obtener una canción por ID"""
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Canción no encontrada"
        )
    return song


@router.post("/", response_model=SongResponse, status_code=status.HTTP_201_CREATED)
async def create_song(
    song: SongCreate,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear una nueva canción — requiere autenticación"""
    # Verificar que el álbum existe si se especifica
    if song.album_id:
        album = db.query(Album).filter(Album.id == song.album_id).first()
        if not album:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Álbum no encontrado"
            )

    db_song = Song(**song.model_dump())
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song


@router.patch("/{song_id}", response_model=SongResponse)
async def update_song(
    song_id: int,
    updates: SongUpdate,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar una canción — requiere autenticación"""
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Canción no encontrada"
        )

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(song, field, value)

    db.commit()
    db.refresh(song)
    return song


@router.delete("/{song_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_song(
    song_id: int,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar una canción — requiere autenticación"""
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Canción no encontrada"
        )
    db.delete(song)
    db.commit()