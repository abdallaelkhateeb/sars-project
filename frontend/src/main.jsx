import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import './index.css'

async function start() {
  // Demo mode: fake API so the UI can be previewed without the backend
  if (import.meta.env.VITE_DEMO === 'true') {
    await import('./devPreview.js')
  }
  ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </React.StrictMode>
  )
}

start()
