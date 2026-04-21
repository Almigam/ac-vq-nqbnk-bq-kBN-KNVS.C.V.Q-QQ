import api from './client';

export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface Album {
  id: number;
  title: string;
  artist: string;
  release_year?: number;
  description?: string;
  cover_image_url?: string;
  created_at: string;
}

export interface Song {
  id: number;
  title: string;
  artist: string;
  album_id?: number;
  duration?: number;
  created_at: string;
}

export interface Review {
  id: number;
  user_id: number;
  album_id?: number;
  song_id?: number;
  rating: number;
  comment?: string;
  created_at: string;
}

// Auth API
export const authAPI = {
  register: (email: string, username: string, password: string, full_name?: string) =>
    api.post<User>('/api/v1/auth/register', {
      email,
      username,
      password,
      full_name,
    }),

  login: (username: string, password: string) =>
    api.post<LoginResponse>('/api/v1/auth/login', 
      new URLSearchParams({
        username,
        password,
      }),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    ),
};

// Albums API
export const albumsAPI = {
  getAll: (skip: number = 0, limit: number = 20) =>
    api.get<Album[]>('/api/v1/albums', { params: { skip, limit } }),

  getById: (id: number) =>
    api.get<Album>(`/api/v1/albums/${id}`),

  create: (album: Omit<Album, 'id' | 'created_at'>) =>
    api.post<Album>('/api/v1/albums', album),

  update: (id: number, updates: Partial<Album>) =>
    api.patch<Album>(`/api/v1/albums/${id}`, updates),

  delete: (id: number) =>
    api.delete(`/api/v1/albums/${id}`),
};

// Songs API
export const songsAPI = {
  getAll: (skip: number = 0, limit: number = 20, albumId?: number) =>
    api.get<Song[]>('/api/v1/songs', { params: { skip, limit, album_id: albumId } }),

  getById: (id: number) =>
    api.get<Song>(`/api/v1/songs/${id}`),

  create: (song: Omit<Song, 'id' | 'created_at'>) =>
    api.post<Song>('/api/v1/songs', song),

  update: (id: number, updates: Partial<Song>) =>
    api.patch<Song>(`/api/v1/songs/${id}`, updates),

  delete: (id: number) =>
    api.delete(`/api/v1/songs/${id}`),
};

// Reviews API
export const reviewsAPI = {
  getAlbumReviews: (albumId: number, skip: number = 0, limit: number = 20) =>
    api.get<Review[]>(`/api/v1/reviews/album/${albumId}`, { params: { skip, limit } }),

  getSongReviews: (songId: number, skip: number = 0, limit: number = 20) =>
    api.get<Review[]>(`/api/v1/reviews/song/${songId}`, { params: { skip, limit } }),

  getMyReviews: (skip: number = 0, limit: number = 20) =>
    api.get<Review[]>('/api/v1/reviews/me', { params: { skip, limit } }),

  create: (rating: number, albumId?: number, songId?: number, comment?: string) =>
    api.post<Review>('/api/v1/reviews', {
      rating,
      album_id: albumId,
      song_id: songId,
      comment,
    }),
};
