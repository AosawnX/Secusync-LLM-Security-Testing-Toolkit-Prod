import { Link, Outlet, useLocation } from 'react-router-dom'
import { LayoutDashboard, FileText, Shield, Target as TargetIcon } from 'lucide-react'

export function MainLayout() {
    const location = useLocation()

    const navItems = [
        { path: '/', label: 'Dashboard', icon: LayoutDashboard },
        { path: '/targets', label: 'Targets', icon: TargetIcon },
        { path: '/reports', label: 'Reports', icon: FileText },
    ]

    return (
        <div className="flex h-screen bg-gray-50 text-gray-900 font-sans">
            {/* Sidebar */}
            <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
                <div className="p-6 flex items-center gap-3 border-b border-gray-100">
                    <Shield className="h-8 w-8 text-blue-600" />
                    <span className="text-xl font-bold tracking-tight text-gray-900">SECUSYNC</span>
                </div>

                <nav className="flex-1 p-4 space-y-1">
                    {navItems.map((item) => {
                        const Icon = item.icon
                        const isActive = location.pathname === item.path
                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${isActive
                                    ? 'bg-blue-50 text-blue-700'
                                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                                    }`}
                            >
                                <Icon className="h-5 w-5" />
                                {item.label}
                            </Link>
                        )
                    })}
                </nav>

                <div className="p-4 border-t border-gray-100">
                    <div className="text-xs text-gray-400 text-center">
                        SECUSYNC v1.0
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto">
                <div className="p-8 max-w-7xl mx-auto">
                    <Outlet />
                </div>
            </main>
        </div>
    )
}
