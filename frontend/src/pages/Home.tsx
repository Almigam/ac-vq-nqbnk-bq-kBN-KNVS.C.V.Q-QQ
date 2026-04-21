import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import '../styles/Home.css';

export function Home() {
  const { isAuthenticated, user } = useAuth();

  return (
    <div className="home-container">
      <section className="hero">
        <div className="hero-content">
          <h1>Soundlog</h1>
          <p className="tagline">Descubre, reseña y comparte tu pasión por la música</p>
          <p className="description">
            Encuentra álbumes, explora canciones y lee reseñas de otros usuarios.
            Comparte tus opiniones sobre tu música favorita.
          </p>
          <div className="hero-buttons">
            {!isAuthenticated ? (
              <>
                <Link to="/login" className="btn btn-primary">
                  Iniciar sesión
                </Link>
                <Link to="/register" className="btn btn-secondary">
                  Registrarse
                </Link>
              </>
            ) : (
              <>
                <p className="welcome">¡Bienvenido, {user?.username}!</p>
                <Link to="/albums" className="btn btn-primary">
                  Explorar álbumes
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      <section className="features">
        <h2>Características</h2>
        <div className="features-grid">
          <div className="feature">
            <div className="feature-icon">📚</div>
            <h3>Catálogo completo</h3>
            <p>Accede a miles de álbumes y canciones</p>
          </div>
          <div className="feature">
            <div className="feature-icon">⭐</div>
            <h3>Reseña y valora</h3>
            <p>Comparte tus opiniones con calificaciones</p>
          </div>
          <div className="feature">
            <div className="feature-icon">👥</div>
            <h3>Comunidad</h3>
            <p>Lee reseñas de otros usuarios apasionados</p>
          </div>
          <div className="feature">
            <div className="feature-icon">🔒</div>
            <h3>Seguro y privado</h3>
            <p>Gestiona tu perfil de forma segura</p>
          </div>
        </div>
      </section>

      {isAuthenticated && (
        <section className="quick-links">
          <h2>Empieza aquí</h2>
          <div className="links-grid">
            <Link to="/albums" className="quick-link">
              <span className="icon">📀</span>
              <span>Explorar álbumes</span>
            </Link>
            <Link to="/songs" className="quick-link">
              <span className="icon">🎵</span>
              <span>Ver todas las canciones</span>
            </Link>
            <Link to="/profile" className="quick-link">
              <span className="icon">👤</span>
              <span>Mi perfil</span>
            </Link>
          </div>
        </section>
      )}
    </div>
  );
}
