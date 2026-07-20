import { BrowserRouter, Routes, Route } from 'react-router-dom'
import EdicionesList from './components/EdicionesList'
import EdicionDetalle from './components/EdicionDetalle'

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <Routes>
          <Route path="/" element={<EdicionesList />} />
          <Route path="/ediciones/:nombre" element={<EdicionDetalle />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}
