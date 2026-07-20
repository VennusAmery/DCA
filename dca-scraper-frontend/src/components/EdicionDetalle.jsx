import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getEdicion, getPdfUrl } from '../api/dcaApi'
import './EdicionDetalle.css'

export default function EdicionDetalle() {
  const { nombre } = useParams()
  const [edicion, setEdicion] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)
  const [verTextoCrudo, setVerTextoCrudo] = useState(false)

  useEffect(() => {
    getEdicion(nombre)
      .then(setEdicion)
      .catch((e) => setError(e.message))
      .finally(() => setCargando(false))
  }, [nombre])

  if (cargando) return <p className="dca-loading">Cargando edición...</p>
  if (error) return <p className="dca-error">Error: {error}</p>
  if (!edicion) return null

  return (
    <div className="edicion-detalle">
      <Link to="/" className="volver">&larr; Volver</Link>
      <h1>{edicion.nombre}</h1>

      {edicion.resumen_html && (
        <div
          className="resumen-html"
          dangerouslySetInnerHTML={{ __html: edicion.resumen_html }}
        />
      )}

      {edicion.tiene_pdf_reporte ? (
        <>
          <a className="descargar-pdf" href={getPdfUrl(nombre)} target="_blank" rel="noreferrer">
            Descargar reporte PDF
          </a>
          <iframe
            className="pdf-embed"
            src={getPdfUrl(nombre)}
            title="Reporte PDF"
          />
        </>
      ) : (
        <p className="dca-error">Reporte PDF aún no generado para esta edición.</p>
      )}

      <button className="toggle-texto" onClick={() => setVerTextoCrudo(!verTextoCrudo)}>
        {verTextoCrudo ? 'Ocultar texto crudo' : 'Ver texto crudo transcrito'}
      </button>
      {verTextoCrudo && (
        <div className="resumen-viewer">
          <pre>{edicion.texto || 'Sin texto disponible'}</pre>
        </div>
      )}
    </div>
  )
}
