// dca-scraper-frontend/src/api/dcaApi.js
import axios from 'axios'

const BASE_URL = '/api'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 35000,
})

export const getEdiciones = () => api.get('/ediciones').then(r => r.data)
export const getEdicion = (nombre) => api.get(`/ediciones/${encodeURIComponent(nombre)}`).then(r => r.data)
export const getPdfUrl = (nombre) => `${BASE_URL}/ediciones/${encodeURIComponent(nombre)}/pdf`
export const getPdfDcaUrl = (nombre) => `${BASE_URL}/ediciones/${encodeURIComponent(nombre)}/pdf-dca`

export const descargarOriginalBlob = (link) =>
  api
    .post('/dca/descargar-original', { link }, { responseType: 'blob', timeout: 120000 })
    .then((r) => r.data)

   
export const generarResumenArchivoBlob = (file) => {
  const formData = new FormData()
  formData.append('archivo', file)
  return api
    .post('/dca/generar-resumen-archivo', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      responseType: 'blob',
      timeout: 180000,
    })
    .then((r) => r.data)
}

export default api