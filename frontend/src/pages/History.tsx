import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { History as HistoryIcon, ChevronRight, AlertTriangle, CheckCircle, Clock, XCircle } from 'lucide-react'
import { apiClient } from '../api/client'

interface ScanRun {
    id: string
    tllm_profile_id: string
    status: string
    attack_classes: string
    mutation_strategies: string
    mutation_depth: number
    total_prompts_sent: number
    vulnerabilities_found: number
    created_at: string
    completed_at: string | null
}

interface TLLMProfile {
    id: string
    name: string
    provider: string
}

const STATUS_STYLES: Record<string, string> = {
    COMPLETED: 'bg-green-50 text-green-700 border-green-200',
    FAILED: 'bg-red-50 text-red-700 border-red-200',
    STOPPED: 'bg-gray-100 text-gray-600 border-gray-200',
    RUNNING: 'bg-blue-50 text-blue-700 border-blue-200',
    PENDING: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    STOPPING: 'bg-orange-50 text-orange-700 border-orange-200',
}

const STATUS_ICONS: Record<string, React.ElementType> = {
    COMPLETED: CheckCircle,
    FAILED: XCircle,
    STOPPED: XCircle,
    RUNNING: Clock,
    PENDING: Clock,
    STOPPING: Clock,
}

function parseList(raw: string): string[] {
    try { return JSON.parse(raw) } catch { return raw.split(',').map(s => s.trim()).filter(Boolean) }
}

function formatClass(cls: string): string {
    return cls.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

export function History() {
    const [scans, setScans] = useState<ScanRun[]>([])
    const [profiles, setProfiles] = useState<Record<string, TLLMProfile>>({})
    const [loading, setLoading] = useState(true)
    const [statusFilter, setStatusFilter] = useState('all')
    const [classFilter, setClassFilter] = useState('all')

    useEffect(() => {
        const load = async () => {
            try {
                const [scansRes, profilesRes] = await Promise.all([
                    apiClient.get('/scans/all').catch(() => ({ data: [] })),
                    apiClient.get('/tllm/profiles').catch(() => ({ data: [] })),
                ])
                setScans(scansRes.data || [])
                const profileMap: Record<string, TLLMProfile> = {}
                for (const p of (profilesRes.data || [])) profileMap[p.id] = p
                setProfiles(profileMap)
            } catch (err) {
                console.error(err)
            } finally {
                setLoading(false)
            }
        }
        load()
    }, [])

    const allClasses = Array.from(new Set(
        scans.flatMap(s => parseList(s.attack_classes))
    )).sort()

    const filtered = scans.filter(s => {
        const statusOk = statusFilter === 'all' || s.status === statusFilter
        const classOk = classFilter === 'all' || parseList(s.attack_classes).includes(classFilter)
        return statusOk && classOk
    })

    const totalVulns = filtered.reduce((acc, s) => acc + (s.vulnerabilities_found || 0), 0)
    const completed = filtered.filter(s => s.status === 'COMPLETED')
    const avgASR = completed.length > 0
        ? Math.round(completed.reduce((acc, s) => {
              const sent = s.total_prompts_sent || 0
              return acc + (sent > 0 ? (s.vulnerabilities_found / sent) * 100 : 0)
          }, 0) / completed.length)
        : 0

    return (
        <div className="space-y-6">
            <header className="flex justify-between items-start">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                        <HistoryIcon className="h-8 w-8 text-[#0461E2]" />
                        Scan History
                    </h1>
                    <p className="text-gray-500 mt-1">All scan runs across all targets</p>
                </div>
            </header>

            {/* Summary strip */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                    { label: 'Total Runs', value: filtered.length },
                    { label: 'Completed', value: filtered.filter(s => s.status === 'COMPLETED').length },
                    { label: 'Vulnerabilities', value: totalVulns },
                    { label: 'Avg ASR', value: `${avgASR}%` },
                ].map(({ label, value }) => (
                    <div key={label} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
                        <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">{label}</p>
                        <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
                    </div>
                ))}
            </div>

            {/* Filters */}
            <div className="flex flex-wrap gap-3 items-center">
                <select
                    value={statusFilter}
                    onChange={e => setStatusFilter(e.target.value)}
                    className="px-3 py-2 bg-white border border-gray-300 rounded-lg text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#0461E2]"
                >
                    <option value="all">All Statuses</option>
                    {['COMPLETED', 'RUNNING', 'PENDING', 'FAILED', 'STOPPED'].map(s => (
                        <option key={s} value={s}>{s}</option>
                    ))}
                </select>

                <select
                    value={classFilter}
                    onChange={e => setClassFilter(e.target.value)}
                    className="px-3 py-2 bg-white border border-gray-300 rounded-lg text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#0461E2]"
                >
                    <option value="all">All Attack Classes</option>
                    {allClasses.map(c => (
                        <option key={c} value={c}>{formatClass(c)}</option>
                    ))}
                </select>

                {(statusFilter !== 'all' || classFilter !== 'all') && (
                    <button
                        onClick={() => { setStatusFilter('all'); setClassFilter('all') }}
                        className="text-sm text-[#0461E2] hover:underline"
                    >
                        Clear filters
                    </button>
                )}

                <span className="ml-auto text-sm text-gray-400">{filtered.length} run{filtered.length !== 1 ? 's' : ''}</span>
            </div>

            {/* Table */}
            <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
                {loading ? (
                    <p className="p-8 text-gray-400">Loading scan history…</p>
                ) : filtered.length === 0 ? (
                    <div className="p-12 text-center">
                        <HistoryIcon className="h-12 w-12 text-gray-200 mx-auto mb-3" />
                        <p className="text-gray-400">No scan runs match your filters.</p>
                    </div>
                ) : (
                    <table className="w-full text-sm">
                        <thead className="bg-[#1B2771] text-white text-xs uppercase tracking-wide">
                            <tr>
                                <th className="px-4 py-3 text-left">Target</th>
                                <th className="px-4 py-3 text-left">Attack Classes</th>
                                <th className="px-4 py-3 text-left">Status</th>
                                <th className="px-4 py-3 text-right">Prompts</th>
                                <th className="px-4 py-3 text-right">Vulns</th>
                                <th className="px-4 py-3 text-right">ASR</th>
                                <th className="px-4 py-3 text-left">Started</th>
                                <th className="px-4 py-3"></th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-50">
                            {filtered.map(scan => {
                                const profile = profiles[scan.tllm_profile_id]
                                const classes = parseList(scan.attack_classes)
                                const StatusIcon = STATUS_ICONS[scan.status] ?? Clock
                                const asr = scan.total_prompts_sent > 0
                                    ? Math.round((scan.vulnerabilities_found / scan.total_prompts_sent) * 100)
                                    : 0
                                return (
                                    <tr key={scan.id} className="hover:bg-gray-50 transition-colors">
                                        <td className="px-4 py-3">
                                            <div className="font-medium text-gray-900 truncate max-w-[140px]">
                                                {profile?.name ?? <span className="text-gray-400 font-mono text-xs">{scan.tllm_profile_id.slice(0, 8)}</span>}
                                            </div>
                                            <div className="text-xs text-gray-400 capitalize">{profile?.provider ?? ''}</div>
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className="flex flex-wrap gap-1">
                                                {classes.map(c => (
                                                    <span key={c} className="text-xs px-1.5 py-0.5 bg-gray-100 text-gray-600 rounded">
                                                        {formatClass(c)}
                                                    </span>
                                                ))}
                                            </div>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border ${STATUS_STYLES[scan.status] ?? 'bg-gray-50 text-gray-500 border-gray-200'}`}>
                                                <StatusIcon className="h-3 w-3" />
                                                {scan.status}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 text-right font-mono text-gray-700">{scan.total_prompts_sent}</td>
                                        <td className="px-4 py-3 text-right">
                                            <span className={`font-bold ${scan.vulnerabilities_found > 0 ? 'text-red-600' : 'text-gray-400'}`}>
                                                {scan.vulnerabilities_found}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 text-right">
                                            {scan.status === 'COMPLETED' && scan.total_prompts_sent > 0 ? (
                                                <span className={`font-mono font-semibold ${asr > 0 ? 'text-red-600' : 'text-green-600'}`}>
                                                    {asr}%
                                                </span>
                                            ) : (
                                                <span className="text-gray-300">—</span>
                                            )}
                                        </td>
                                        <td className="px-4 py-3 text-xs text-gray-500">
                                            {new Date(scan.created_at + (scan.created_at.endsWith('Z') ? '' : 'Z')).toLocaleString()}
                                        </td>
                                        <td className="px-4 py-3">
                                            <Link
                                                to={`/executions/${scan.id}`}
                                                className="inline-flex items-center gap-1 text-[#0461E2] hover:text-[#1B2771] text-xs font-medium"
                                            >
                                                View <ChevronRight className="h-3 w-3" />
                                            </Link>
                                        </td>
                                    </tr>
                                )
                            })}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    )
}
