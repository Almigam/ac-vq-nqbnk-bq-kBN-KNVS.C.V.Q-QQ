"""
Rutas de Reseñas
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.models import Review, Album, Song
from core.schemas import ReviewCreate, ReviewResponse
from core.security import get_current_user

router = APIRouter(prefix="/api/v1/reviews", tags=["reviews"])


@router.get("/album/{album_id}", response_model=List[ReviewResponse])
async def get_album_reviews(
    album_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Obtener todas las reseñas de un álbum"""
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Álbum no encontrado"
        )
    reviews = (
        db.query(Review)
        .filter(Review.album_id == album_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return reviews


@router.get("/song/{song_id}", response_model=List[ReviewResponse])
async def get_song_reviews(
    song_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Obtener todas las reseñas de una canción"""
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Canción no encontrada"
        )
    reviews = (
        db.query(Review)
        .filter(Review.song_id == song_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return reviews


@router.get("/me", response_model=List[ReviewResponse])
async def get_my_reviews(
    skip: int = 0,
    limit: int = 20,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener todas las reseñas del usuario autenticado"""
    reviews = (
        db.query(Review)
        .filter(Review.user_id == current_user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return reviews


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: ReviewCreate,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear una reseña — requiere autenticación.
    Debe especificarse album_id o song_id, no ambos.
    """
    if review.album_id is not None and review.song_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Una reseña solo puede ser de un álbum o una canción, no de ambos"
        )
    if review.album_id is None and review.song_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes especificar album_id o song_id"
        )

    if not 0 <= review.rating <= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El rating debe estar entre 0 y 5"
        )

    if review.album_id is not None:
        album = db.query(Album).filter(Album.id == review.album_id).first()
        if not album:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Álbum no encontrado"
            )
    if review.song_id is not None:
        song = db.query(Song).filter(Song.id == review.song_id).first()
        if not song:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Canción no encontrada"
            )

    # Verificar reseña duplicada
    existing = db.query(Review).filter(
        Review.user_id == current_user_id,
        Review.album_id == review.album_id,
        Review.song_id == review.song_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya has reseñado este álbum o canción"
        )

    db_review = Review(
        user_id=current_user_id,
        **review.model_dump()
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar una reseña — solo el autor puede eliminarla"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reseña no encontrada"
        )
    if review.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar esta reseña"
        )
    db.delete(review)
    db.commit()
