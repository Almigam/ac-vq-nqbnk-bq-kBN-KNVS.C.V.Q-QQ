import { useState, useEffect } from 'react';
import { Review, reviewsAPI } from '../api';
import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';
import '../styles/Profile.css';

export function Profile() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMyReviews();
  }, []);

  const loadMyReviews = async () => {
    try {
      const response = await reviewsAPI.getMyReviews();
      setReviews(response.data);
    } catch (err) {
      console.error('Error al cargar reseñas', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) {
    return null;
  }

  return (
    <div className="profile-container">
      <div className="profile-card">
        <div className="profile-header">
          <div className="profile-avatar">{user.username[0]?.toUpperCase()}</div>
          <div className="profile-info">
            <h1>{user.full_name || user.username}</h1>
            <p className="profile-username">@{user.username}</p>
            <p className="profile-email">{user.email}</p>
          </div>
          <button onClick={handleLogout} className="logout-btn">
            Cerrar sesión
          </button>
        </div>
      </div>

      <section className="my-reviews">
        <h2>Mis Reseñas ({reviews.length})</h2>
        {loading ? (
          <div className="loading">Cargando...</div>
        ) : reviews.length > 0 ? (
          <div className="reviews-grid">
            {reviews.map((review) => (
              <div key={review.id} className="review-card">
                <div className="review-rating">
                  {review.rating} ⭐
                </div>
                {review.comment && (
                  <p className="review-text">{review.comment}</p>
                )}
                <p className="review-date">
                  {new Date(review.created_at).toLocaleDateString('es-ES')}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p className="no-reviews">No has escrito reseñas aún</p>
        )}
      </section>
    </div>
  );
}
