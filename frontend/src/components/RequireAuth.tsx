import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Shield } from 'lucide-react'

/**
 * Route guard — redirects unauthenticated users to /login.
 * Preserves the intended path so after login they land on the right page.
 * Shows a full-screen spinner while Firebase resolves the persisted session
 * (prevents a flash of the login page on refresh when already logged in).
 */
export function RequireAuth({ children }: { children: React.ReactNode }) {
    const { user, loading } = useAuth()
    const location = useLocation()

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="flex flex-col items-center gap-3 text-gray-400">
                    <Shield className="h-10 w-10 text-[#0461E2] animate-pulse" />
                    <span className="text-sm">Loading...</span>
                </div>
            </div>
        )
    }

    if (!user) {
        return <Navigate to="/login" state={{ from: location }} replace />
    }

    return <>{children}</>
}
