import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Album, Song, Review, albumsAPI, songsAPI, reviewsAPI } from '../api';
import { useAuth } from '../hooks/useAuth';
import '../styles/AlbumDetail.css';

export function AlbumDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [album, setAlbum] = useState<Album | null>(null);
  const [songs, setSongs] = useState<Song[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [newReview, setNewReview] = useState({ rating: 5, comment: '' });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadData();
  }, [id]);

  const loadData = async () => {
    try {
      setLoading(true);
      const albumId = parseInt(id!);
      const [albumRes, songsRes, reviewsRes] = await Promise.all([
        albumsAPI.getById(albumId),
        songsAPI.getAll(0, 50, albumId),
        reviewsAPI.getAlbumReviews(albumId),
      ]);
      setAlbum(albumRes.data);
      setSongs(songsRes.data);
      setReviews(reviewsRes.data);
    } catch (err) {
      setError('Error al cargar los datos del álbum');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    setSubmitting(true);
    try {
      await reviewsAPI.create(newReview.rating, parseInt(id!), undefined, newReview.comment);
      setNewReview({ rating: 5, comment: '' });
      loadData();
    } catch (err) {
      setError('Error al enviar la reseña');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="loading">Cargando...</div>;
  }

  if (!album) {
    return <div className="error-message">Álbum no encontrado</div>;
  }

  return (
    <div className="album-detail-container">
      <div className="album-detail-header">
        <div className="album-cover-large">
          {album.cover_image_url ? (
            <img src={album.cover_image_url} alt={album.title} />
          ) : (
            <div className="placeholder-large">♪</div>
          )}
        </div>
        <div className="album-detail-info">
          <h1>{album.title}</h1>
          <p className="detail-artist">{album.artist}</p>
          {album.release_year && (
            <p className="detail-year">Año: {album.release_year}</p>
          )}
          {album.description && (
            <p className="detail-description">{album.description}</p>
          )}
          <div className="album-stats">
            <span>{reviews.length} reseñas</span>
            {reviews.length > 0 && (
              <span>Promedio: {(reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length).toFixed(1)} ⭐</span>
            )}
          </div>
        </div>
      </div>

      {songs.length > 0 && (
        <section className="songs-section">
          <h2>Canciones ({songs.length})</h2>
          <div className="songs-list">
            {songs.map((song) => (
              <div key={song.id} className="song-item">
                <div className="song-info">
                  <p className="song-title">{song.title}</p>
                  <p className="song-artist">{song.artist}</p>
                </div>
                {song.duration && (
                  <span className="song-duration">
                    {Math.floor(song.duration / 60)}:{(song.duration % 60).toString().padStart(2, '0')}
                  </span>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="reviews-section">
        <h2>Reseñas</h2>

        {isAuthenticated && (
          <form className="review-form" onSubmit={handleSubmitReview}>
            <h3>Escribe una reseña</h3>
            <div className="form-group">
              <label htmlFor="rating">Calificación (1-5)</label>
              <select
                id="rating"
                value={newReview.rating}
                onChange={(e) =>
                  setNewReview({ ...newReview, rating: parseFloat(e.target.value) })
                }
              >
                {[1, 2, 3, 4, 5].map((n) => (
                  <option key={n} value={n}>
                    {n} ⭐
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="comment">Comentario</label>
              <textarea
                id="comment"
                value={newReview.comment}
                onChange={(e) =>
                  setNewReview({ ...newReview, comment: e.target.value })
                }
                placeholder="¿Qué te pareció este álbum?"
                rows={4}
              />
            </div>
            <button type="submit" disabled={submitting} className="submit-btn">
              {submitting ? 'Enviando...' : 'Enviar reseña'}
            </button>
          </form>
        )}

        <div className="reviews-list">
          {reviews.length > 0 ? (
            reviews.map((review) => (
              <div key={review.id} className="review-item">
                <div className="review-header">
                  <span className="review-rating">{review.rating} ⭐</span>
                  <span className="review-date">
                    {new Date(review.created_at).toLocaleDateString('es-ES')}
                  </span>
                </div>
                {review.comment && (
                  <p className="review-comment">{review.comment}</p>
                )}
              </div>
            ))
          ) : (
            <p className="no-reviews">Sin reseñas aún. ¡Sé el primero en reseñar!</p>
          )}
        </div>
      </section>
    </div>
  );
}
