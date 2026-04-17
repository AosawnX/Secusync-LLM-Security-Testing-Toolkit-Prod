import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { RequireAuth } from './components/RequireAuth'
import { MainLayout } from './layouts/MainLayout'
import { Login } from './pages/Login'
import { Dashboard } from './pages/Dashboard'
import { Targets } from './pages/Targets'
import { RunDetail } from './pages/RunDetail'
import { ExecutionDetail } from './pages/ExecutionDetail'
import { Reports } from './pages/Reports'
import './index.css'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public route */}
          <Route path="/login" element={<Login />} />

          {/* All other routes require authentication */}
          <Route
            path="/"
            element={
              <RequireAuth>
                <MainLayout />
              </RequireAuth>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="targets" element={<Targets />} />
            <Route path="runs/:id" element={<RunDetail />} />
            <Route path="executions/:id" element={<ExecutionDetail />} />
            <Route path="reports" element={<Reports />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
