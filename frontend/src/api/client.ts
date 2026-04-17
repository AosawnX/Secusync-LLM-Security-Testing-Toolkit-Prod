import axios from 'axios'
import { auth } from '../firebase'

export const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
})

// Attach a fresh Firebase ID token to every outbound request.
// getIdToken() returns a cached token and only hits the network when
// the token is within 5 minutes of expiry — safe to call on every request.
apiClient.interceptors.request.use(async (config) => {
  const user = auth.currentUser
  if (user) {
    const token = await user.getIdToken(false)
    config.headers = config.headers ?? {}
    config.headers['Authorization'] = `Bearer ${token}`
  }
  return config
})

// On 401 the session has expired on the backend (e.g. token revoked in
// Firebase Console). Sign the user out so they're redirected to /login.
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await auth.signOut()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
