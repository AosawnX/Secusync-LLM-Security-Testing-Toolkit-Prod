import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { FileText, Download, Clock } from 'lucide-react'
import { apiClient } from '../api/client'

interface ScanRun {
    id: string
    tllm_profile_id: string
    status: string
    created_at: string
    completed_at: string | null
    total_prompts_sent: number
    vulnerabilities_found: number
}

export function Reports() {
    const [scans, setScans] = useState<ScanRun[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        apiClient.get('/scans/all')
            .then(res => {
                // Filter only completed scans
                const completedScans = (res.data as ScanRun[]).filter(r => r.status === 'COMPLETED')
                setScans(completedScans)
                setLoading(false)
            })
            .catch(err => {
                console.error(err)
                setLoading(false)
            })
    }, [])

    if (loading) return <div className="p-8 text-gray-500">Loading reports...</div>

    return (
        <div className="space-y-6">
            <header>
                <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                    <FileText className="h-8 w-8 text-blue-600" />
                    Security Reports
                </h1>
                <p className="text-gray-500 mt-2">Access and download detailed security assessment reports.</p>
            </header>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                {scans.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">
                        No reports available yet. Complete a vulnerability scan to generate a report.
                    </div>
                ) : (
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Scan ID</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Results</th>
                                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {scans.map((scan) => (
                                <tr key={scan.id} className="hover:bg-gray-50 transition-colors">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center">
                                            <div className="text-sm font-medium text-gray-900">
                                                <Link to={`/executions/${scan.id}`} className="hover:text-blue-600">
                                                    {scan.id.slice(0, 8)}...
                                                </Link>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm text-gray-500 flex items-center gap-2">
                                            <Clock className="h-4 w-4" />
                                            {new Date(scan.created_at).toLocaleDateString()} {new Date(scan.created_at).toLocaleTimeString()}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${scan.vulnerabilities_found > 0 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
                                            {scan.vulnerabilities_found} vulnerabilities / {scan.total_prompts_sent} prompts
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                        <div className="flex justify-end gap-2">
                                            <Link
                                                to={`/executions/${scan.id}`}
                                                className="text-blue-600 hover:text-blue-900 inline-flex items-center gap-1"
                                            >
                                                <Download className="h-4 w-4" />
                                                View Details
                                            </Link>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    )
}
