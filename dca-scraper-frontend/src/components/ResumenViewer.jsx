import { useEffect, useState } from 'react'
import { getResumen } from '../api/dcaApi'
import './ResumenViewer.css'
import loaderGif from '../../src/assets/cargando.gif'

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

if (cargando) {
    return (
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backdropFilter: 'blur(4px)',
          background: 'rgba(255,255,255,0.6)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
        }}
      >
        <img
          src={loaderGif}
          alt="Cargando..."
          style={{ width: 100, position: 'relative', zIndex: 10000 }}
        />
        <p style={{ marginTop: 12, color: 'var(--crimson, #333)', fontWeight: 600 }}>
          Cargando...
        </p>
      </div>
    )
  }
  if (error) return <p className="dca-error">Sin resumen disponible</p>
  if (!resumen) return null

  return (
    <div className="resumen-viewer">
      <h2>Resumen</h2>
      <div dangerouslySetInnerHTML={{ __html: resumen.contenido_html }} />
    </div>
  )
}
