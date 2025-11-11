import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './pages/App.tsx'
import { BrowserRouter, Route } from 'react-router'
import { Routes } from 'react-router'
import Settings from './pages/Settings.tsx'
import Login from './pages/Login.tsx'
import { UserProvider } from './context/UserContext.ts'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <UserProvider>
      <BrowserRouter>
        <Routes>
          <Route index element={<App/>}/>
          <Route path='/settings' element={<Settings/>}/>
          <Route path='/login' element={<Login/>}/>
        </Routes>
      </BrowserRouter>
    </UserProvider>
  </StrictMode>,
)
