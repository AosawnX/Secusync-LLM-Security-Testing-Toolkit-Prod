import { useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { Shield, LogIn, UserPlus, Eye, EyeOff } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

type Mode = 'signin' | 'signup'

// Map Firebase auth error codes to human-readable messages.
// Never expose raw Firebase error strings to the user (they can leak
// implementation details).
function friendlyError(code: string): string {
    switch (code) {
        case 'auth/invalid-email':
            return 'Invalid email address.'
        case 'auth/user-not-found':
        case 'auth/wrong-password':
        case 'auth/invalid-credential':
            return 'Incorrect email or password.'
        case 'auth/email-already-in-use':
            return 'An account with that email already exists.'
        case 'auth/weak-password':
            return 'Password must be at least 6 characters.'
        case 'auth/too-many-requests':
            return 'Too many failed attempts. Please try again later.'
        case 'auth/network-request-failed':
            return 'Network error. Check your connection.'
        default:
            return 'Authentication failed. Please try again.'
    }
}

export function Login() {
    const { signIn, signUp } = useAuth()
    const navigate = useNavigate()
    const [mode, setMode] = useState<Mode>('signin')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [showPassword, setShowPassword] = useState(false)
    const [error, setError] = useState('')
    const [submitting, setSubmitting] = useState(false)

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault()
        setError('')
        setSubmitting(true)
        try {
            if (mode === 'signin') {
                await signIn(email, password)
            } else {
                await signUp(email, password)
            }
            navigate('/', { replace: true })
        } catch (err: unknown) {
            const code = (err as { code?: string }).code ?? ''
            setError(friendlyError(code))
        } finally {
            setSubmitting(false)
        }
    }

    return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
            <div className="w-full max-w-md">
                {/* Brand header */}
                <div className="flex items-center justify-center gap-3 mb-8">
                    <Shield className="h-10 w-10 text-[#0461E2]" />
                    <span className="text-3xl font-bold tracking-tight text-[#1B2771]">SECUSYNC</span>
                </div>

                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
                    <h1 className="text-xl font-semibold text-gray-900 mb-1">
                        {mode === 'signin' ? 'Sign in to your account' : 'Create an account'}
                    </h1>
                    <p className="text-sm text-gray-500 mb-6">
                        {mode === 'signin'
                            ? 'LLM Security Testing Toolkit'
                            : 'Get started with SECUSYNC'}
                    </p>

                    <form onSubmit={handleSubmit} className="space-y-4" noValidate>
                        <div>
                            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                                Email
                            </label>
                            <input
                                id="email"
                                type="email"
                                autoComplete="email"
                                required
                                value={email}
                                onChange={e => setEmail(e.target.value)}
                                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="you@example.com"
                            />
                        </div>

                        <div>
                            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                                Password
                            </label>
                            <div className="relative">
                                <input
                                    id="password"
                                    type={showPassword ? 'text' : 'password'}
                                    autoComplete={mode === 'signin' ? 'current-password' : 'new-password'}
                                    required
                                    value={password}
                                    onChange={e => setPassword(e.target.value)}
                                    className="w-full border border-gray-300 rounded-lg px-3 py-2 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    placeholder={mode === 'signup' ? 'At least 6 characters' : '••••••••'}
                                />
                                <button
                                    type="button"
                                    tabIndex={-1}
                                    onClick={() => setShowPassword(v => !v)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                                >
                                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                                </button>
                            </div>
                        </div>

                        {error && (
                            <div className="bg-red-50 border border-red-200 rounded-lg px-3 py-2 text-sm text-red-700" role="alert">
                                {error}
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={submitting || !email || !password}
                            className="w-full bg-[#0461E2] hover:bg-blue-700 text-white font-semibold py-2.5 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                        >
                            {mode === 'signin'
                                ? <><LogIn className="h-4 w-4" />{submitting ? 'Signing in...' : 'Sign In'}</>
                                : <><UserPlus className="h-4 w-4" />{submitting ? 'Creating account...' : 'Create Account'}</>
                            }
                        </button>
                    </form>

                    <div className="mt-5 pt-5 border-t border-gray-100 text-center text-sm text-gray-500">
                        {mode === 'signin' ? (
                            <>
                                Don't have an account?{' '}
                                <button
                                    type="button"
                                    onClick={() => { setMode('signup'); setError('') }}
                                    className="text-[#0461E2] font-medium hover:underline"
                                >
                                    Sign up
                                </button>
                            </>
                        ) : (
                            <>
                                Already have an account?{' '}
                                <button
                                    type="button"
                                    onClick={() => { setMode('signin'); setError('') }}
                                    className="text-[#0461E2] font-medium hover:underline"
                                >
                                    Sign in
                                </button>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}
