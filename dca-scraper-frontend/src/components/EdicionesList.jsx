import { useEffect, useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { getEdiciones } from '../api/dcaApi'
import EstadoBadge from './EstadoBadge'
import './EdicionesList.css'

const MESES = [
  { num: '01', nombre: 'Enero' },
  { num: '02', nombre: 'Febrero' },
  { num: '03', nombre: 'Marzo' },
  { num: '04', nombre: 'Abril' },
  { num: '05', nombre: 'Mayo' },
  { num: '06', nombre: 'Junio' },
  { num: '07', nombre: 'Julio' },
  { num: '08', nombre: 'Agosto' },
  { num: '09', nombre: 'Septiembre' },
  { num: '10', nombre: 'Octubre' },
  { num: '11', nombre: 'Noviembre' },
  { num: '12', nombre: 'Diciembre' },
]

const obtenerAnioYMes = (fechaStr) => {
  if (!fechaStr) return { anio: '', mes: '' }
  const match = String(fechaStr).match(/^(\d{4})[-/](\d{2})/)
  if (match) {
    return { anio: match[1], mes: match[2] }
  }
  return { anio: '', mes: '' }
}

const formatearFecha = (fechaStr) => {
  const { anio, mes } = obtenerAnioYMes(fechaStr)
  if (!anio || !mes) return '—'
  const diaMatch = String(fechaStr).match(/^\d{4}-\d{2}-(\d{2})/)
  const dia = diaMatch ? parseInt(diaMatch[1], 10) : null
  const nombreMes = MESES.find((m) => m.num === mes)?.nombre.toLowerCase()
  if (!nombreMes) return fechaStr
  return dia ? `${dia} de ${nombreMes} de ${anio}` : `${nombreMes} de ${anio}`
}

export default function EdicionesList() {
  const [ediciones, setEdiciones] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)

  const [busqueda, setBusqueda] = useState('')
  const [orden, setOrden] = useState('reciente')
  const [anioFiltro, setAnioFiltro] = useState('todos')
  const [mesFiltro, setMesFiltro] = useState('todos')

  useEffect(() => {
    getEdiciones()
      .then(setEdiciones)
      .catch((e) => setError(e.message))
      .finally(() => setCargando(false))
  }, [])

  const aniosDisponibles = useMemo(() => {
    const aniosSet = new Set()
    ediciones.forEach((e) => {
      const { anio } = obtenerAnioYMes(e.fecha_publicacion)
      if (anio) aniosSet.add(anio)
    })
    return Array.from(aniosSet).sort().reverse()
  }, [ediciones])

  const edicionesProcesadas = useMemo(() => {
    return ediciones
      .filter((e) => {
        const coincideNombre = e.nombre.toLowerCase().includes(busqueda.toLowerCase())
        const { anio, mes } = obtenerAnioYMes(e.fecha_publicacion)

        const coincideAnio = anioFiltro === 'todos' || anio === anioFiltro
        const coincideMes = mesFiltro === 'todos' || mes === mesFiltro

        return coincideNombre && coincideAnio && coincideMes
      })
      .sort((a, b) => {
        const fechaA = a.fecha_publicacion ? new Date(a.fecha_publicacion) : 0
        const fechaB = b.fecha_publicacion ? new Date(b.fecha_publicacion) : 0

        return orden === 'reciente' ? fechaB - fechaA : fechaA - fechaB
      })
  }, [ediciones, busqueda, anioFiltro, mesFiltro, orden])

  if (cargando) return <p className="dca-loading">Cargando ediciones...</p>
  if (error) return <p className="dca-error">Error: {error}</p>

  return (
    <div className="ediciones-list">
      <div className="ediciones-header-fijo">
        <h1>Diario de Centro América</h1>

        <div className="controles-filtro">
          <input
            type="text"
            className="buscador-input"
            placeholder="Buscar por nombre..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />

          <select
            className="filtro-select"
            value={anioFiltro}
            onChange={(e) => setAnioFiltro(e.target.value)}
          >
            <option value="todos">Todos los años</option>
            {aniosDisponibles.map((anio) => (
              <option key={anio} value={anio}>
                {anio}
              </option>
            ))}
          </select>

          <select
            className="filtro-select"
            value={mesFiltro}
            onChange={(e) => setMesFiltro(e.target.value)}
          >
            <option value="todos">Todos los meses</option>
            {MESES.map((m) => (
              <option key={m.num} value={m.num}>
                {m.nombre}
              </option>
            ))}
          </select>

          <select
            className="filtro-select"
            value={orden}
            onChange={(e) => setOrden(e.target.value)}
          >
            <option value="reciente">Más reciente primero</option>
            <option value="antiguo">Más antiguo primero</option>
          </select>
        </div>
      </div>

      <table>
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Fecha</th>
            <th>Estado</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {edicionesProcesadas.map((e) => (
            <tr key={e.nombre}>
              <td>{e.nombre}</td>
              <td>{formatearFecha(e.fecha_publicacion)}</td>
              <td><EstadoBadge estado={e.estado} /></td>
              <td>
                <Link to={`/ediciones/${encodeURIComponent(e.nombre)}`}>Ver detalle</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {edicionesProcesadas.length === 0 && (
        <p className="dca-loading">No hay resultados que coincidan con los filtros.</p>
      )}
    </div>
  )
}