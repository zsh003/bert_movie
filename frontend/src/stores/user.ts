import { defineStore } from 'pinia'

interface UserState {
  token: string
  user: User | null
  favorites: string[]
}

interface User {
  id: string
  username: string
  email: string
  is_admin: boolean
  avatar?: string
  created_at: string
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    favorites: JSON.parse(localStorage.getItem('favorites') || '[]')
  }),

  getters: {
    isLoggedIn: (state): boolean => !!state.token,
    isAdmin: (state): boolean => state.user?.is_admin || false,
    getFavorites: (state): string[] => state.favorites
  },

  actions: {
    setToken(token: string): void {
      this.token = token
      localStorage.setItem('token', token)
    },

    setUser(user: User): void {
      this.user = user
      localStorage.setItem('user', JSON.stringify(user))
    },

    addToFavorites(movieId: string): void {
      if (!this.favorites.includes(movieId)) {
        this.favorites.push(movieId)
        localStorage.setItem('favorites', JSON.stringify(this.favorites))
      }
    },

    removeFromFavorites(movieId: string): void {
      const index = this.favorites.indexOf(movieId)
      if (index > -1) {
        this.favorites.splice(index, 1)
        localStorage.setItem('favorites', JSON.stringify(this.favorites))
      }
    },

    logout(): void {
      this.token = ''
      this.user = null
      this.favorites = []
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('favorites')
    }
  }
}) 