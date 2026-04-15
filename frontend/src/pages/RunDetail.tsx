import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Play, Activity, Clock } from 'lucide-react'
import { apiClient } from '../api/client'

interface TLLMProfile {
    id: string
    name: string
    provider: string
    endpoint_url?: string
    created_at: string
}

interface ScanRun {
    id: string
    tllm_profile_id: string
    status: string
    created_at: string
    completed_at: string | null
    total_prompts_sent: number
    vulnerabilities_found: number
}

export function RunDetail() {
    const { id } = useParams()
    const [target, setTarget] = useState<TLLMProfile | null>(null)
    const [scans, setScans] = useState<ScanRun[]>([])
    const [loading, setLoading] = useState(true)
    const [startingRun, setStartingRun] = useState(false)

    useEffect(() => {
        // Fetch Target Details
        apiClient.get('/tllm/profiles')
            .then(res => {
                const profile = (res.data as TLLMProfile[]).find(p => p.id === id)
                if (profile) setTarget(profile)
                setLoading(false)
            })
            .catch(err => {
                console.error(err)
                setLoading(false)
            })

        // Fetch Scans (all, then filter by profile id)
        apiClient.get('/scans/all')
            .then(res => {
                const profileScans = (res.data as ScanRun[]).filter(s => s.tllm_profile_id === id)
                setScans(profileScans)
            })
            .catch(console.error)
    }, [id])

    const handleStartRun = async () => {
        if (!target) return
        setStartingRun(true)

        try {
            const res = await apiClient.post('/scans/start', {
                tllm_profile_id: target.id,
                attack_classes: ['prompt_injection'],
                mutation_strategies: ['none'],
                mutation_depth: 1
            })

            if (res.data?.id) {
                window.location.href = `/executions/${res.data.id}`
            }
        } catch (err) {
            console.error(err)
            alert("Error starting scan")
        } finally {
            setStartingRun(false)
        }
    }

    if (loading) return <div className="p-8 text-gray-500">Loading details...</div>
    if (!target) return <div className="p-8 text-red-500">Target not found</div>

    return (
        <div className="space-y-6">
            <header className="flex items-center gap-4">
                <Link to="/targets" className="p-2 hover:bg-gray-100 rounded-full text-gray-500">
                    <ArrowLeft className="h-5 w-5" />
                </Link>
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">{target.name}</h1>
                    <p className="text-gray-500 font-mono text-sm">{target.id}</p>
                </div>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="md:col-span-2 space-y-6">
                    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                            <Activity className="h-5 w-5 text-blue-600" />
                            Target Configuration
                        </h2>
                        <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-6">
                            <div>
                                <dt className="text-sm font-medium text-gray-500">Provider</dt>
                                <dd className="mt-1 text-sm text-gray-900 capitalize bg-gray-50 inline-block px-2 py-1 rounded">{target.provider}</dd>
                            </div>
                            <div className="sm:col-span-1">
                                <dt className="text-sm font-medium text-gray-500">Created</dt>
                                <dd className="mt-1 text-sm text-gray-900">{new Date(target.created_at + (target.created_at.endsWith('Z') ? '' : 'Z')).toLocaleString()}</dd>
                            </div>
                            {target.endpoint_url && (
                                <div className="sm:col-span-2">
                                    <dt className="text-sm font-medium text-gray-500">Endpoint URL</dt>
                                    <dd className="mt-1 text-sm font-mono text-gray-700 bg-gray-50 p-2 rounded block overflow-hidden text-ellipsis">{target.endpoint_url}</dd>
                                </div>
                            )}
                        </dl>
                    </div>

                    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-lg font-semibold">Scan History</h2>
                        </div>
                        {scans.length === 0 ? (
                            <p className="text-gray-400 italic">No scans executed yet.</p>
                        ) : (
                            <ul className="divide-y divide-gray-100">
                                {scans.map(scan => (
                                    <li key={scan.id} className="py-3 flex justify-between items-center group">
                                        <div>
                                            <p className="font-medium text-gray-900">Scan {scan.id.slice(0, 8)}...</p>
                                            <div className="text-sm text-gray-500">
                                                {new Date(scan.created_at + (scan.created_at.endsWith('Z') ? '' : 'Z')).toLocaleString()}
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-3">
                                            <span className={`px-2 py-1 text-xs rounded-full border ${scan.status === 'COMPLETED' ? 'bg-green-50 text-green-700 border-green-100' :
                                                scan.status === 'FAILED' ? 'bg-red-50 text-red-700 border-red-100' :
                                                    'bg-yellow-50 text-yellow-700 border-yellow-100'
                                                }`}>
                                                {scan.status}
                                            </span>
                                            <Link to={`/executions/${scan.id}`} className="px-3 py-1 bg-white border border-gray-200 text-xs font-medium text-gray-600 rounded hover:bg-gray-50 hover:text-blue-600 transition-colors">
                                                View Details
                                            </Link>
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>
                </div>

                <div className="space-y-6">
                    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                        <h2 className="text-lg font-semibold mb-4">Actions</h2>
                        <div className="space-y-3">
                            <button
                                onClick={handleStartRun}
                                disabled={startingRun}
                                className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                            >
                                <Play className="h-4 w-4" />
                                {startingRun ? 'Starting...' : 'Start Attack'}
                            </button>
                            <button className="w-full py-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 font-medium rounded-lg transition-colors">
                                Test Connection
                            </button>
                            <button className="w-full py-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 font-medium rounded-lg transition-colors">
                                Edit Configuration
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
