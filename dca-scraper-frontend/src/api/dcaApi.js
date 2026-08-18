// dca-scraper-frontend/src/api/dcaApi.js
import axios from 'axios'

const BASE_URL = 'https://dca-kmda.onrender.com/api'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
})

export const getEdiciones = () => api.get('/ediciones').then(r => r.data)
export const getEdicion = (nombre) => api.get(`/ediciones/${encodeURIComponent(nombre)}`).then(r => r.data)
export const getPdfUrl = (nombre) => `${BASE_URL}/ediciones/${encodeURIComponent(nombre)}/pdf`
export const getPdfDcaUrl = (nombre) => `${BASE_URL}/ediciones/${encodeURIComponent(nombre)}/pdf-dca`

export default api