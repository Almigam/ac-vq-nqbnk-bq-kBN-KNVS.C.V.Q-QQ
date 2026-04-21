import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Album, albumsAPI } from '../api';
import '../styles/Albums.css';

export function AlbumsList() {
  const [albums, setAlbums] = useState<Album[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [skip, setSkip] = useState(0);

  useEffect(() => {
    loadAlbums();
  }, [skip]);

  const loadAlbums = async () => {
    try {
      setLoading(true);
      const response = await albumsAPI.getAll(skip, 12);
      setAlbums(response.data);
    } catch (err: any) {
      setError('Error al cargar álbumes');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="albums-container">
      <div className="albums-header">
        <h1>Álbumes</h1>
        <p>Descubre y reseña tus álbumes favoritos</p>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading">Cargando álbumes...</div>
      ) : (
        <>
          <div className="albums-grid">
            {albums.map((album) => (
              <Link key={album.id} to={`/albums/${album.id}`} className="album-card">
                <div className="album-cover">
                  {album.cover_image_url ? (
                    <img src={album.cover_image_url} alt={album.title} />
                  ) : (
                    <div className="placeholder">
                      <span>♪</span>
                    </div>
                  )}
                </div>
                <div className="album-info">
                  <h3>{album.title}</h3>
                  <p className="artist">{album.artist}</p>
                  {album.release_year && (
                    <p className="year">{album.release_year}</p>
                  )}
                </div>
              </Link>
            ))}
          </div>

          <div className="pagination">
            <button
              disabled={skip === 0}
              onClick={() => setSkip(Math.max(0, skip - 12))}
              className="pagination-btn"
            >
              ← Anterior
            </button>
            <button
              disabled={albums.length < 12}
              onClick={() => setSkip(skip + 12)}
              className="pagination-btn"
            >
              Siguiente →
            </button>
          </div>
        </>
      )}
    </div>
  );
}
