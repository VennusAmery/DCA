// edicion-detalle.jsx
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
  const [pdfActivo, setPdfActivo] = useState('reporte')

  useEffect(() => {
    getEdicion(nombre)
      .then(setEdicion)
      .catch((e) => setError(e.message))
      .finally(() => setCargando(false))
  }, [nombre])

  const cambiarTab = (tab) => {
    setPdfActivo(tab)
    setVerTextoCrudo(false)
  }

  if (cargando) return <p className="dca-loading">Cargando edición...</p>
  if (error) return <p className="dca-error">Error: {error}</p>
  if (!edicion) return null

  const urlPdfReporte = getPdfUrl(nombre)
  const urlPdfDca = edicion.url_pdf_dca

  return (
    <div className="edicion-detalle">
      <Link to="/" className="volver">&larr; Volver</Link>
      <h1>{edicion.nombre}</h1>

      <div className="botones-fila">
        <button 
          className={`accion-btn ${pdfActivo === 'reporte' && !verTextoCrudo ? 'active' : ''}`}
          onClick={() => cambiarTab('reporte')}
        >
          📄 Reporte Generado
        </button>
        <button 
          className={`accion-btn ${pdfActivo === 'dca' && !verTextoCrudo ? 'active' : ''}`}
          onClick={() => cambiarTab('dca')}
        >
          📰 PDF Original DCA
        </button>

        <button 
          className={`accion-btn ${verTextoCrudo ? 'active' : ''}`} 
          onClick={() => setVerTextoCrudo(!verTextoCrudo)}
        >
          📝 Ver texto crudo transcrito
        </button>

        {!verTextoCrudo && pdfActivo === 'reporte' && edicion.tiene_pdf_reporte && (
          <a className="accion-btn" href={urlPdfReporte} download target="_blank" rel="noreferrer">
            ⬇️ Descargar reporte PDF
          </a>
        )}
        {!verTextoCrudo && pdfActivo === 'dca' && urlPdfDca && (
          <a className="accion-btn" href={urlPdfDca} download target="_blank" rel="noreferrer">
            ⬇️ Descargar DCA PDF
          </a>
        )}
      </div>

      {verTextoCrudo ? (
        <div className="resumen-viewer" key="texto-crudo">
          <pre>{edicion.texto || 'Sin texto disponible'}</pre>
        </div>
      ) : (
        <>
          {pdfActivo === 'reporte' && (
            edicion.tiene_pdf_reporte ? (
              <div className="pdf-container" key="reporte">
                <iframe className="pdf-embed" src={urlPdfReporte} title="Reporte PDF" />
              </div>
            ) : (
              <p className="dca-error">Reporte PDF aún no generado para esta edición.</p>
            )
          )}

          {pdfActivo === 'dca' && (
            urlPdfDca ? (
              <div className="pdf-container" key="dca">
                <iframe className="pdf-embed" src={urlPdfDca} title="PDF Original DCA" />
              </div>
            ) : (
              <p className="dca-error">PDF original del DCA no disponible.</p>
            )
          )}

          {edicion.resumen_html && (
            <div className="resumen-html" dangerouslySetInnerHTML={{ __html: edicion.resumen_html }} />
          )}
        </>
      )}
    </div>
  )
}