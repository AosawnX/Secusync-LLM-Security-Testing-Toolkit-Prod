import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, AlertTriangle, CheckCircle, Terminal, RotateCw, Clock, FileText, Download, StopCircle } from 'lucide-react'
import { apiClient } from '../api/client'

interface PromptVariant {
    id: string
    scan_run_id: string
    attack_class: string
    strategy_applied?: string
    depth: number
    prompt_text: string
    response_text?: string
    verdict: string
    deterministic_matches?: string
    semantic_classification?: string
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
    attack_classes: string
}

export function ExecutionDetail() {
    const { id } = useParams()
    const [run, setRun] = useState<ScanRun | null>(null)
    const [loading, setLoading] = useState(true)
    const [variants, setVariants] = useState<PromptVariant[]>([])
    const [stopping, setStopping] = useState(false)

    const ACTIVE_STATUSES = ['PENDING', 'RUNNING', 'STOPPING']
    const isActive = run ? ACTIVE_STATUSES.includes(run.status) : false

    const handleStopScan = async () => {
        if (!run || stopping) return
        if (!window.confirm('Stop this scan? Partial results will be saved.')) return
        setStopping(true)
        try {
            const res = await apiClient.post(`/scans/${run.id}/stop`)
            setRun(res.data)
        } catch (err) {
            console.error(err)
            alert('Failed to stop scan')
        } finally {
            setStopping(false)
        }
    }

    useEffect(() => {
        let intervalId: ReturnType<typeof setInterval>

        const fetchRunData = async () => {
            try {
                const res = await apiClient.get(`/scans/${id}`)
                setRun(res.data)
                setLoading(false)

                // Fetch prompt variants (results/logs)
                const varRes = await apiClient.get(`/scans/${id}/results`)
                if (varRes.data) {
                    setVariants(varRes.data)
                }

                if (['COMPLETED', 'FAILED', 'STOPPED'].includes(res.data.status)) {
                    clearInterval(intervalId)
                }
            } catch (err) {
                console.error(err)
                setLoading(false)
            }
        }

        fetchRunData()
        intervalId = setInterval(fetchRunData, 2000)

        return () => clearInterval(intervalId)
    }, [id])

    if (loading) return <div className="p-8 text-gray-500">Loading run details...</div>
    if (!run) return <div className="p-8 text-red-500">Run not found</div>

    const vulnerableVariants = variants.filter(v => v.verdict === 'VULNERABLE')

    return (
        <div className="space-y-6">
            <header className="flex items-center gap-4">
                <Link to={`/runs/${run.tllm_profile_id}`} className="p-2 hover:bg-gray-100 rounded-full text-gray-500">
                    <ArrowLeft className="h-5 w-5" />
                </Link>
                <div className="flex-1">
                    <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                        Scan Execution
                        <span className={`px-3 py-1 text-sm rounded-full border ${run.status === 'COMPLETED' ? 'bg-green-50 text-green-700 border-green-100' :
                            run.status === 'FAILED' ? 'bg-red-50 text-red-700 border-red-100' :
                            run.status === 'STOPPED' ? 'bg-gray-100 text-gray-700 border-gray-200' :
                                'bg-yellow-50 text-yellow-700 border-yellow-100'
                            }`}>
                            {run.status}
                        </span>
                    </h1>
                    <p className="text-gray-500 font-mono text-sm">ID: {run.id}</p>
                </div>
                <div>
                    <div className="flex gap-2">
                        <button
                            onClick={() => window.open(`http://127.0.0.1:8000/api/scans/${run.id}/report/executive`, '_blank')}
                            className="bg-white hover:bg-gray-50 border border-blue-200 text-blue-700 font-medium py-2 px-4 rounded inline-flex items-center gap-2 cursor-pointer transition-colors"
                        >
                            <FileText className="h-4 w-4" />
                            <span>Executive PDF</span>
                        </button>
                        <button
                            onClick={() => window.open(`http://127.0.0.1:8000/api/scans/${run.id}/report/technical`, '_blank')}
                            className="bg-white hover:bg-gray-50 border border-blue-200 text-blue-700 font-medium py-2 px-4 rounded inline-flex items-center gap-2 cursor-pointer transition-colors"
                        >
                            <Download className="h-4 w-4" />
                            <span>Technical PDF</span>
                        </button>
                        <button
                            onClick={() => window.open(`http://127.0.0.1:8000/api/scans/${run.id}/report/poc`, '_blank')}
                            className="bg-white hover:bg-gray-50 border border-gray-300 text-gray-700 font-medium py-2 px-4 rounded inline-flex items-center gap-2 cursor-pointer transition-colors"
                        >
                            <Download className="h-4 w-4" />
                            <span>PoC ZIP</span>
                        </button>
                        {isActive && (
                            <button
                                onClick={handleStopScan}
                                disabled={stopping || run.status === 'STOPPING'}
                                className="bg-[#DC2626] hover:bg-red-700 text-white font-bold py-2 px-4 rounded inline-flex items-center gap-2 cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
                            >
                                <StopCircle className="h-4 w-4" />
                                <span>{run.status === 'STOPPING' ? 'Stopping...' : 'Stop Scan'}</span>
                            </button>
                        )}
                        <button
                            onClick={async () => {
                                if (!run) return
                                try {
                                    const res = await apiClient.post('/scans/start', {
                                        tllm_profile_id: run.tllm_profile_id,
                                        attack_classes: ['prompt_injection'],
                                        mutation_strategies: ['none'],
                                        mutation_depth: 1
                                    })
                                    if (res.data?.id) {
                                        window.location.href = `/executions/${res.data.id}`
                                    }
                                } catch (err) {
                                    console.error(err)
                                    alert("Error restarting scan")
                                }
                            }}
                            disabled={isActive}
                            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded inline-flex items-center gap-2 cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
                        >
                            <RotateCw className="h-4 w-4" />
                            <span>Retry Attack</span>
                        </button>
                    </div>
                </div>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                    <h2 className="text-lg font-semibold mb-4">Summary</h2>
                    <p className="text-gray-700">
                        {run.status === 'COMPLETED'
                            ? `Scan completed. ${run.total_prompts_sent} prompts sent, ${run.vulnerabilities_found} vulnerabilities found.`
                            : run.status === 'RUNNING'
                                ? 'Scan is currently in progress...'
                                : run.status === 'PENDING'
                                    ? 'Scan is queued and will start shortly.'
                                    : 'Scan execution failed.'
                        }
                    </p>
                    <div className="mt-4 flex flex-col gap-2 text-sm text-gray-500">
                        <div className="flex items-center gap-2">
                            <Clock className="h-4 w-4" />
                            Started: {new Date(run.created_at + (run.created_at.endsWith('Z') ? '' : 'Z')).toLocaleString()}
                        </div>
                        {run.completed_at && (
                            <div className="flex items-center gap-2">
                                <CheckCircle className="h-4 w-4" />
                                Completed: {new Date(run.completed_at + (run.completed_at.endsWith('Z') ? '' : 'Z')).toLocaleString()}
                            </div>
                        )}
                    </div>
                </div>

                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                    <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                        <AlertTriangle className="h-5 w-5 text-orange-500" />
                        Vulnerability Assessment
                    </h2>
                    <div className="flex items-center gap-4 mb-4">
                        <div className="text-center">
                            <p className="text-sm text-gray-500">Prompts Sent</p>
                            <p className="text-3xl font-bold text-gray-900">{run.total_prompts_sent}</p>
                        </div>
                        <div className="text-center">
                            <p className="text-sm text-gray-500">Vulnerabilities</p>
                            <p className="text-3xl font-bold text-gray-900">{run.vulnerabilities_found}</p>
                        </div>
                    </div>
                    <ul className="space-y-2">
                        {vulnerableVariants.length > 0 ? (
                            vulnerableVariants.map((v) => (
                                <li key={v.id} className="p-3 bg-red-50 border border-red-100 rounded-lg text-sm text-red-800">
                                    <span className="font-bold uppercase text-xs mr-2 border border-red-200 px-1 rounded bg-white">VULNERABLE</span>
                                    {v.prompt_text.slice(0, 100)}...
                                </li>
                            ))
                        ) : (
                            <li className="text-sm text-gray-400 italic">No vulnerabilities detected.</li>
                        )}
                    </ul>
                </div>
            </div>

            <div className="bg-black text-green-400 font-mono text-sm p-4 rounded-xl shadow-lg border border-gray-800 h-96 overflow-y-auto">
                <div className="flex items-center gap-2 mb-2 border-b border-gray-800 pb-2">
                    <Terminal className="h-4 w-4" />
                    <span>Execution Logs</span>
                </div>
                <div className="space-y-2 font-mono text-xs">
                    {variants.length === 0 ? (
                        <p className="opacity-50">Waiting for logs...</p>
                    ) : (
                        variants.map((variant, i) => (
                            <div key={i} className="border-b border-gray-900 pb-2 mb-2">
                                <div className="text-blue-400 flex gap-2">
                                    <span className="opacity-50">[{new Date(variant.created_at + (variant.created_at.endsWith('Z') ? '' : 'Z')).toLocaleTimeString()}]</span>
                                    <span>&gt; {variant.prompt_text}</span>
                                </div>
                                <div className="text-gray-300 pl-4 mt-1 whitespace-pre-wrap">
                                    {variant.response_text || '(no response)'}
                                </div>
                                <div className="pl-4 mt-2 flex gap-4">
                                    <div className="flex-1 border border-gray-800 rounded p-2 bg-gray-900/50">
                                        <div className="text-xs uppercase text-gray-500 font-bold mb-1">Verdict</div>
                                        <div className={`text-xs font-mono font-bold ${variant.verdict === 'VULNERABLE' ? 'text-red-400' : variant.verdict === 'NEEDS_REVIEW' ? 'text-orange-400' : 'text-green-500'}`}>
                                            {variant.verdict}
                                        </div>
                                    </div>
                                    {variant.deterministic_matches && variant.deterministic_matches !== "[]" && (
                                        <div className="flex-1 border border-gray-800 rounded p-2 bg-gray-900/50">
                                            <div className="text-xs uppercase text-gray-500 font-bold mb-1">Deterministic Flags</div>
                                            <div className="text-red-400 text-xs font-mono">{variant.deterministic_matches}</div>
                                        </div>
                                    )}
                                    {variant.semantic_classification && (
                                        <div className="flex-1 border border-gray-800 rounded p-2 bg-gray-900/50">
                                            <div className="text-xs uppercase text-gray-500 font-bold mb-1">Semantic Class</div>
                                            <div className="text-blue-300 text-xs font-mono">{variant.semantic_classification}</div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    )
}
