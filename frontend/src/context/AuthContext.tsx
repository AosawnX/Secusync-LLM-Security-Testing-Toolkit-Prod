import { createContext, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import {
    onAuthStateChanged,
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword,
    signOut as firebaseSignOut,
} from 'firebase/auth'
import type { User, AuthError } from 'firebase/auth'
import { auth } from '../firebase'

interface AuthContextValue {
    user: User | null
    loading: boolean
    signIn: (email: string, password: string) => Promise<void>
    signUp: (email: string, password: string) => Promise<void>
    signOut: () => Promise<void>
    getIdToken: () => Promise<string>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
            setUser(firebaseUser)
            setLoading(false)
        })
        return unsubscribe
    }, [])

    const signIn = async (email: string, password: string) => {
        await signInWithEmailAndPassword(auth, email, password)
    }

    const signUp = async (email: string, password: string) => {
        await createUserWithEmailAndPassword(auth, email, password)
    }

    const signOut = async () => {
        await firebaseSignOut(auth)
    }

    const getIdToken = async (): Promise<string> => {
        if (!user) throw new Error('Not authenticated')
        // forceRefresh=false: Firebase auto-refreshes before expiry (1h TTL)
        return user.getIdToken(false)
    }

    return (
        <AuthContext.Provider value={{ user, loading, signIn, signUp, signOut, getIdToken }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth(): AuthContextValue {
    const ctx = useContext(AuthContext)
    if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
    return ctx
}

// Re-export for convenience in error handling
export type { AuthError }
