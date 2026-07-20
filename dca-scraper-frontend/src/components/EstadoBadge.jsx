import './EstadoBadge.css'

const LABELS = {
  pendiente: 'Pendiente',
  descargado: 'Descargado',
  transcrito: 'Transcrito',
  resumido: 'Resumido',
  error: 'Error',
}

export default function EstadoBadge({ estado }) {
  return (
    <span className={`estado-badge estado-${estado}`}>
      {LABELS[estado] || estado}
    </span>
  )
}
