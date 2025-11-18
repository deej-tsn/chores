import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import Home from './pages/Home.tsx'
import { BrowserRouter, Navigate, Route } from 'react-router'
import { Routes } from 'react-router'
import Settings from './pages/Settings.tsx'
import Login from './pages/Login.tsx'
import { UserProvider } from './context/UserContext.ts'
import ProtectedRoute from './components/ProtectedRoute.tsx'
import { EditPanelProvider } from './context/EditContext.ts'
import SignUp from './pages/SignUp.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
      <UserProvider>
        <EditPanelProvider>
          <BrowserRouter>
            <Routes>
              <Route index element={<Navigate to="/login"/>}/>
              <Route element={<ProtectedRoute/>}>
                <Route path='/home' element={<Home/>}/>
                <Route path='/settings' element={<Settings/>}/>
              </Route>

              <Route path='/login' element={<Login/>}/>
              <Route path='/sign-up'  element={<SignUp/>}/>
            </Routes>
          </BrowserRouter>
        </EditPanelProvider>
      </UserProvider>
  </StrictMode>,
)
