import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

export const getEdiciones = () => api.get('/ediciones').then(r => r.data)

export const getEdicion = (nombre) => api.get(`/ediciones/${encodeURIComponent(nombre)}`).then(r => r.data)

export const getPdfUrl = (nombre) => `/api/ediciones/${encodeURIComponent(nombre)}/pdf`

export default api
