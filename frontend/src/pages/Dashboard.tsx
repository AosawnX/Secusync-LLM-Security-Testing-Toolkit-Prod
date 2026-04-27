import { useEffect, useState } from 'react'
import { Plus, ChevronRight, Activity } from 'lucide-react'
import { Link } from 'react-router-dom'
import { apiClient } from '../api/client'

const STATUS_STYLES: Record<string, string> = {
    COMPLETED: 'bg-green-50 text-green-700 border-green-200',
    FAILED: 'bg-red-50 text-red-700 border-red-200',
    STOPPED: 'bg-gray-100 text-gray-600 border-gray-200',
    RUNNING: 'bg-blue-50 text-blue-700 border-blue-200',
    PENDING: 'bg-yellow-50 text-yellow-700 border-yellow-200',
}

function parseList(raw: string): string[] {
    try { return JSON.parse(raw) } catch { return raw.split(',').map(s => s.trim()).filter(Boolean) }
}

function fmtClass(cls: string): string {
    return cls.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

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
    attack_classes: string
    created_at: string
    vulnerabilities_found: number
    total_prompts_sent: number
}

export function Dashboard() {
    const [profiles, setProfiles] = useState<TLLMProfile[]>([])
    const [allScans, setAllScans] = useState<ScanRun[]>([])
    const [filter, setFilter] = useState('7d')
    const [stats, setStats] = useState({
        totalScans: 0,
        activeTargets: 0,
        vulnerabilities: 0,
        successRate: 0
    })
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [profilesRes, scansRes] = await Promise.all([
                    apiClient.get('/tllm/profiles').catch(() => ({ data: [] })),
                    apiClient.get('/scans/all').catch(() => ({ data: [] }))
                ])

                setProfiles(profilesRes.data || [])
                setAllScans(scansRes.data || [])
                setLoading(false)
            } catch (err) {
                console.error(err)
                setLoading(false)
            }
        }

        fetchData()
    }, [])

    useEffect(() => {
        if (loading) return

        const now = new Date()
        const filterDate = new Date()

        if (filter === 'today') filterDate.setHours(0, 0, 0, 0)
        else if (filter === '7d') filterDate.setDate(now.getDate() - 7)
        else if (filter === '30d') filterDate.setDate(now.getDate() - 30)
        else if (filter === '90d') filterDate.setDate(now.getDate() - 90)

        const filteredScans = allScans.filter((r) => new Date(r.created_at + (r.created_at.endsWith('Z') ? '' : 'Z')) >= filterDate)

        const totalScans = filteredScans.length
        const activeTargets = profiles.length
        const vulnerabilities = filteredScans.reduce((acc, scan) => acc + (scan.vulnerabilities_found || 0), 0)

        const completedScans = filteredScans.filter((r) => r.status === 'COMPLETED')
        const scansWithVulns = completedScans.filter((r) => (r.vulnerabilities_found || 0) > 0)
        const successRate = completedScans.length > 0
            ? Math.round((scansWithVulns.length / completedScans.length) * 100)
            : 0

        setStats({
            totalScans,
            activeTargets,
            vulnerabilities,
            successRate
        })

    }, [filter, allScans, profiles, loading])

    return (
        <div className="space-y-6">
            <header className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
                    <p className="text-gray-500">Welcome to SECUSYNC — LLM Security Testing Toolkit.</p>
                </div>
                <div className="flex gap-3">
                    <select
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                        className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="today">Today</option>
                        <option value="7d">Last 7 Days</option>
                        <option value="30d">Last 30 Days</option>
                        <option value="90d">Last 90 Days</option>
                    </select>
                    <Link to="/targets" className="px-4 py-2 bg-blue-600 text-white rounded-lg flex items-center gap-2 hover:bg-blue-700 transition">
                        <Plus className="h-5 w-5" />
                        New Target
                    </Link>
                </div>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                    <p className="text-sm font-medium text-gray-500 mb-1">Total Scans</p>
                    <div className="flex items-baseline gap-2">
                        <h3 className="text-3xl font-bold text-gray-900">{stats.totalScans}</h3>
                        <span className="text-xs font-medium text-green-600 bg-green-50 px-2 py-0.5 rounded-full">
                            {filter === 'today' ? 'Today' : filter}
                        </span>
                    </div>
                </div>
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                    <p className="text-sm font-medium text-gray-500 mb-1">Active Targets</p>
                    <h3 className="text-3xl font-bold text-gray-900">{stats.activeTargets}</h3>
                </div>
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                    <p className="text-sm font-medium text-gray-500 mb-1">Vulnerabilities</p>
                    <div className="flex items-baseline gap-2">
                        <h3 className="text-3xl font-bold text-gray-900">{stats.vulnerabilities}</h3>
                        {stats.vulnerabilities > 0 && (
                            <span className="text-xs font-medium text-red-600 bg-red-50 px-2 py-0.5 rounded-full">Action required</span>
                        )}
                    </div>
                </div>
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                    <p className="text-sm font-medium text-gray-500 mb-1">Detection Rate</p>
                    <div className="flex items-baseline gap-2">
                        <h3 className="text-3xl font-bold text-gray-900">{stats.successRate}%</h3>
                        <span className="text-xs text-gray-400">Detection efficiency</span>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Recent Targets */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                    <h2 className="text-lg font-semibold mb-4 flex items-center justify-between">
                        <span>Targets</span>
                        <Link to="/targets" className="text-xs text-[#0461E2] hover:underline font-normal">Manage</Link>
                    </h2>
                    {loading ? (
                        <p className="text-gray-400 text-sm">Loading…</p>
                    ) : profiles.length === 0 ? (
                        <div className="text-center py-8">
                            <p className="text-gray-400 mb-3 text-sm">No targets configured yet.</p>
                            <Link to="/targets" className="text-[#0461E2] font-medium hover:underline text-sm">Create your first target →</Link>
                        </div>
                    ) : (
                        <ul className="divide-y divide-gray-50">
                            {profiles.slice(0, 6).map(p => (
                                <li key={p.id} className="py-3 flex justify-between items-center group">
                                    <div>
                                        <Link to={`/runs/${p.id}`} className="font-medium text-gray-900 group-hover:text-[#0461E2] transition-colors block text-sm">
                                            {p.name}
                                        </Link>
                                        <p className="text-xs text-gray-400 capitalize">{p.provider}</p>
                                    </div>
                                    <Link to={`/runs/${p.id}`} className="flex items-center gap-1 text-xs text-gray-400 hover:text-[#0461E2]">
                                        Scan <ChevronRight className="h-3 w-3" />
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>

                {/* Recent Scans */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                    <h2 className="text-lg font-semibold mb-4 flex items-center justify-between">
                        <span>Recent Scans</span>
                        <Link to="/history" className="text-xs text-[#0461E2] hover:underline font-normal">View all</Link>
                    </h2>
                    {loading ? (
                        <p className="text-gray-400 text-sm">Loading…</p>
                    ) : allScans.length === 0 ? (
                        <div className="text-center py-8">
                            <Activity className="h-8 w-8 text-gray-200 mx-auto mb-2" />
                            <p className="text-gray-400 text-sm">No scans run yet.</p>
                        </div>
                    ) : (
                        <ul className="divide-y divide-gray-50">
                            {allScans.slice(0, 6).map(scan => {
                                const classes = parseList(scan.attack_classes ?? '[]')
                                const asr = scan.total_prompts_sent > 0
                                    ? Math.round((scan.vulnerabilities_found / scan.total_prompts_sent) * 100)
                                    : null
                                return (
                                    <li key={scan.id} className="py-3 flex items-center justify-between gap-3">
                                        <div className="min-w-0">
                                            <Link to={`/executions/${scan.id}`} className="text-sm font-medium text-gray-900 hover:text-[#0461E2] font-mono block truncate">
                                                {scan.id.slice(0, 12)}…
                                            </Link>
                                            <div className="flex flex-wrap gap-1 mt-1">
                                                {classes.map(c => (
                                                    <span key={c} className="text-[10px] px-1.5 py-0.5 bg-gray-100 text-gray-500 rounded">{fmtClass(c)}</span>
                                                ))}
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2 shrink-0">
                                            {asr !== null && scan.status === 'COMPLETED' && (
                                                <span className={`text-xs font-bold font-mono ${asr > 0 ? 'text-red-600' : 'text-green-600'}`}>
                                                    ASR {asr}%
                                                </span>
                                            )}
                                            <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${STATUS_STYLES[scan.status] ?? 'bg-gray-50 text-gray-500 border-gray-200'}`}>
                                                {scan.status}
                                            </span>
                                        </div>
                                    </li>
                                )
                            })}
                        </ul>
                    )}
                </div>
            </div>
        </div>
    )
}
