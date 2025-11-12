import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import Home from './pages/Home.tsx'
import { BrowserRouter, Route } from 'react-router'
import { Routes } from 'react-router'
import Settings from './pages/Settings.tsx'
import Login from './pages/Login.tsx'
import { UserProvider } from './context/UserContext.ts'
import ProtectedRoute from './components/ProtectedRoute.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <UserProvider>
      <BrowserRouter>
        <Routes>

          <Route element={<ProtectedRoute/>}>
            <Route path='/home' element={<Home/>}/>
            <Route path='/settings' element={<Settings/>}/>
          </Route>

          <Route index path='/login' element={<Login/>}/>
        </Routes>
      </BrowserRouter>
    </UserProvider>
  </StrictMode>,
)
