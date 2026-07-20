import { useEffect, useState } from 'react'
import { getResumen } from '../api/dcaApi'
import './ResumenViewer.css'

export default function ResumenViewer({ edicionId }) {
  const [resumen, setResumen] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getResumen(edicionId)
      .then(setResumen)
      .catch((e) => setError(e.message))
      .finally(() => setCargando(false))
  }, [edicionId])

  if (cargando) return <p className="dca-loading">Cargando resumen...</p>
  if (error) return <p className="dca-error">Sin resumen disponible</p>
  if (!resumen) return null

  return (
    <div className="resumen-viewer">
      <h2>Resumen</h2>
      <div dangerouslySetInnerHTML={{ __html: resumen.contenido_html }} />
    </div>
  )
}
