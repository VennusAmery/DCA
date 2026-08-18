import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getEdicion, getPdfUrl, getPdfDcaUrl } from '../api/dcaApi' // Agrega getPdfDcaUrl si aplica
import './EdicionDetalle.css'

export default function EdicionDetalle() {
  const { nombre } = useParams()
  const [edicion, setEdicion] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)
  const [verTextoCrudo, setVerTextoCrudo] = useState(false)
  const [pdfActivo, setPdfActivo] = useState('reporte') // 'reporte' | 'dca'

  useEffect(() => {
    getEdicion(nombre)
      .then(setEdicion)
      .catch((e) => setError(e.message))
      .finally(() => setCargando(false))
  }, [nombre])

  if (cargando) return <p className="dca-loading">Cargando edición...</p>
  if (error) return <p className="dca-error">Error: {error}</p>
  if (!edicion) return null

  // Define las URLs de los PDF según la estructura de tu API
  const urlPdfReporte = getPdfUrl(nombre)
  const urlPdfDca = edicion.url_pdf_dca || (getPdfDcaUrl ? getPdfDcaUrl(nombre) : null)

  return (
    <div className="edicion-detalle">
      <Link to="/" className="volver">&larr; Volver</Link>
      <h1>{edicion.nombre}</h1>

      {/* Selector de PDFs */}
      <div className="pdf-selector-tabs">
        <button 
          className={`tab-btn ${pdfActivo === 'reporte' ? 'active' : ''}`}
          onClick={() => setPdfActivo('reporte')}
        >
          📄 Reporte Generado
        </button>
        <button 
          className={`tab-btn ${pdfActivo === 'dca' ? 'active' : ''}`}
          onClick={() => setPdfActivo('dca')}
        >
          📰 PDF Original DCA
        </button>
      </div>

      {/* Visor de PDF Reporte */}
      {pdfActivo === 'reporte' && (
        edicion.tiene_pdf_reporte ? (
          <div className="pdf-container">
            <a className="descargar-pdf" href={urlPdfReporte} download target="_blank" rel="noreferrer">
              Descargar reporte PDF
            </a>
            <iframe
              className="pdf-embed"
              src={urlPdfReporte}
              title="Reporte PDF"
            />
          </div>
        ) : (
          <p className="dca-error">Reporte PDF aún no generado para esta edición.</p>
        )
      )}

      {/* Visor de PDF Original DCA */}
      {pdfActivo === 'dca' && (
        urlPdfDca ? (
          <div className="pdf-container">
            <a className="descargar-pdf" href={urlPdfDca} download target="_blank" rel="noreferrer">
              Descargar PDF Original DCA
            </a>
            <iframe
              className="pdf-embed"
              src={urlPdfDca}
              title="PDF Original DCA"
            />
          </div>
        ) : (
          <p className="dca-error">PDF original del DCA no disponible.</p>
        )
      )}

      {edicion.resumen_html && (
        <div
          className="resumen-html"
          dangerouslySetInnerHTML={{ __html: edicion.resumen_html }}
        />
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