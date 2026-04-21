import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import '../styles/Navbar.css';

export function Navbar() {
  const navigate = useNavigate();
  const { isAuthenticated, user, logout } = useAuth();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
    setIsMenuOpen(false);
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <a href="/" className="navbar-logo">
          ♪ Soundlog
        </a>
        <button
          className="menu-toggle"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
        >
          ☰
        </button>
        <div className={`navbar-menu ${isMenuOpen ? 'open' : ''}`}>
          <a href="/albums" className="nav-link" onClick={() => setIsMenuOpen(false)}>
            Álbumes
          </a>
          <a href="/songs" className="nav-link" onClick={() => setIsMenuOpen(false)}>
            Canciones
          </a>
          {isAuthenticated ? (
            <>
              <a href="/profile" className="nav-link" onClick={() => setIsMenuOpen(false)}>
                {user?.username}
              </a>
              <button onClick={handleLogout} className="nav-link logout-link">
                Cerrar sesión
              </button>
            </>
          ) : (
            <>
              <a href="/login" className="nav-link" onClick={() => setIsMenuOpen(false)}>
                Iniciar sesión
              </a>
              <a href="/register" className="nav-link signup-link" onClick={() => setIsMenuOpen(false)}>
                Registrarse
              </a>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
