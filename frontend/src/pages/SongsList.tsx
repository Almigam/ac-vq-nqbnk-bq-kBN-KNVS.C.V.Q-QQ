import { useState, useEffect } from 'react';
import { Song, songsAPI } from '../api';
import '../styles/Songs.css';

export function SongsList() {
  const [songs, setSongs] = useState<Song[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [skip, setSkip] = useState(0);

  useEffect(() => {
    loadSongs();
  }, [skip]);

  const loadSongs = async () => {
    try {
      setLoading(true);
      const response = await songsAPI.getAll(skip, 20);
      setSongs(response.data);
    } catch (err: any) {
      setError('Error al cargar canciones');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="songs-container">
      <div className="songs-header">
        <h1>Canciones</h1>
        <p>Todas las canciones en Soundlog</p>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading">Cargando canciones...</div>
      ) : (
        <>
          <div className="songs-table">
            <table>
              <thead>
                <tr>
                  <th>Título</th>
                  <th>Artista</th>
                  <th>Duración</th>
                </tr>
              </thead>
              <tbody>
                {songs.map((song) => (
                  <tr key={song.id}>
                    <td>{song.title}</td>
                    <td>{song.artist}</td>
                    <td>
                      {song.duration
                        ? `${Math.floor(song.duration / 60)}:${(song.duration % 60).toString().padStart(2, '0')}`
                        : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="pagination">
            <button
              disabled={skip === 0}
              onClick={() => setSkip(Math.max(0, skip - 20))}
              className="pagination-btn"
            >
              ← Anterior
            </button>
            <button
              disabled={songs.length < 20}
              onClick={() => setSkip(skip + 20)}
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
