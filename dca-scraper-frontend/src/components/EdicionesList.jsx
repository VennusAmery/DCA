import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getEdiciones } from '../api/dcaApi'
import EstadoBadge from './EstadoBadge'
import './EdicionesList.css'

export default function EdicionesList() {
  const [ediciones, setEdiciones] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getEdiciones()
      .then(setEdiciones)
      .catch((e) => setError(e.message))
      .finally(() => setCargando(false))
  }, [])

  if (cargando) return <p className="dca-loading">Cargando ediciones...</p>
  if (error) return <p className="dca-error">Error: {error}</p>

  return (
    <div className="ediciones-list">
      <h1>Diario de Centro América</h1>
      <table>
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Estado</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {ediciones.map((e) => (
            <tr key={e.nombre}>
              <td>{e.nombre}</td>
              <td><EstadoBadge estado={e.estado} /></td>
              <td>
                <Link to={`/ediciones/${encodeURIComponent(e.nombre)}`}>Ver detalle</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
