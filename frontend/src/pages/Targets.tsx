import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Target as TargetIcon, Cpu, Globe, ArrowRight, ShieldAlert, X, Trash2, Edit2 } from 'lucide-react'
import { apiClient } from '../api/client'

interface TLLMProfile {
    id: string
    name: string
    provider: string
    endpoint_url?: string
    api_key_ref?: string
    system_prompt?: string
    has_rag: boolean
    accepts_documents: boolean
    accepts_multimodal: boolean
    created_at: string
}

export function Targets() {
    const [targets, setTargets] = useState<TLLMProfile[]>([])
    const [loading, setLoading] = useState(true)
    const [showNewTarget, setShowNewTarget] = useState(false)
    const [editingTargetId, setEditingTargetId] = useState<string | null>(null)

    // Form State
    const [formData, setFormData] = useState({
        name: '',
        provider: 'ollama',
        endpoint_url: '',
        api_key_ref: '',
        system_prompt: '',
        has_rag: false,
        accepts_documents: false,
        accepts_multimodal: false
    })
    const [creating, setCreating] = useState(false)

    useEffect(() => {
        fetchTargets()
    }, [])

    const fetchTargets = () => {
        apiClient.get('/tllm/profiles')
            .then(res => {
                setTargets(res.data)
                setLoading(false)
            })
            .catch(err => {
                console.error(err)
                setLoading(false)
            })
    }

    const handleDelete = async (id: string, name: string) => {
        if (!confirm(`Are you sure you want to delete target "${name}"? This action cannot be undone.`)) return

        try {
            const res = await apiClient.delete(`/tllm/profiles/${id}`)
            if (res.status === 200) {
                setTargets(targets.filter(t => t.id !== id))
            }
        } catch (err) {
            console.error(err)
            alert('Error deleting target')
        }
    }

    const handleEdit = (target: TLLMProfile) => {
        setEditingTargetId(target.id)
        setFormData({
            name: target.name,
            provider: target.provider,
            endpoint_url: target.endpoint_url || '',
            api_key_ref: target.api_key_ref || '',
            system_prompt: target.system_prompt || '',
            has_rag: target.has_rag,
            accepts_documents: target.accepts_documents,
            accepts_multimodal: target.accepts_multimodal
        })
        setShowNewTarget(true)
    }

    const handleCreateOrUpdateSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setCreating(true)

        const payload = {
            ...formData,
            name: formData.name.trim(),
            endpoint_url: formData.endpoint_url.trim() || undefined,
            api_key_ref: formData.api_key_ref.trim() || undefined,
            system_prompt: formData.system_prompt.trim() || undefined,
        }

        try {
            if (editingTargetId) {
                await apiClient.put(`/tllm/profiles/${editingTargetId}`, payload)
            } else {
                await apiClient.post('/tllm/profiles', payload)
            }
            fetchTargets()
            closeForm()
        } catch (err) {
            console.error(err)
            alert(`Error ${editingTargetId ? 'updating' : 'creating'} target`)
        } finally {
            setCreating(false)
        }
    }

    const closeForm = () => {
        setShowNewTarget(false)
        setEditingTargetId(null)
        setFormData({ name: '', provider: 'ollama', endpoint_url: '', api_key_ref: '', system_prompt: '', has_rag: false, accepts_documents: false, accepts_multimodal: false })
    }

    if (loading) return <div className="p-8 text-gray-500">Loading targets...</div>

    return (
        <div className="space-y-6">
            <header className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                        <TargetIcon className="h-8 w-8 text-blue-600" />
                        Targets
                    </h1>
                    <p className="text-gray-500 mt-2">Manage your TLLM security targets and endpoints.</p>
                </div>
                {!showNewTarget && (
                    <button
                        onClick={() => setShowNewTarget(true)}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg flex items-center gap-2 hover:bg-blue-700 transition"
                    >
                        <Plus className="h-5 w-5" />
                        Add New Target
                    </button>
                )}
            </header>

            {showNewTarget && (
                <div className="bg-white p-6 rounded-xl shadow-sm border border-blue-100 ring-1 ring-blue-50">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-lg font-semibold">{editingTargetId ? 'Edit Target' : 'Configure New Target'}</h2>
                        <button onClick={closeForm} className="text-gray-400 hover:text-gray-600">
                            <X className="h-5 w-5" />
                        </button>
                    </div>

                    <form onSubmit={handleCreateOrUpdateSubmit} className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Target Name</label>
                            <input
                                required
                                type="text"
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-shadow"
                                value={formData.name}
                                onChange={e => setFormData({ ...formData, name: e.target.value })}
                                placeholder="e.g. Corporate ChatBot V1"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-3">Target Type</label>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div
                                    className={`border rounded-lg p-4 cursor-pointer transition-all ${formData.provider === 'local_mock' ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500' : 'border-gray-200 hover:border-gray-300'}`}
                                    onClick={() => setFormData({ ...formData, provider: 'local_mock' })}
                                >
                                    <div className="flex items-center gap-3 mb-2">
                                        <TargetIcon className={`h-5 w-5 ${formData.provider === 'local_mock' ? 'text-blue-600' : 'text-gray-500'}`} />
                                        <span className="font-medium text-gray-900">Local Mock</span>
                                    </div>
                                    <p className="text-xs text-gray-500">Built-in vulnerable LLM mock for safe testing without keys.</p>
                                </div>
                                <div
                                    className={`border rounded-lg p-4 cursor-pointer transition-all ${formData.provider === 'ollama' ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500' : 'border-gray-200 hover:border-gray-300'}`}
                                    onClick={() => setFormData({ ...formData, provider: 'ollama' })}
                                >
                                    <div className="flex items-center gap-3 mb-2">
                                        <Cpu className={`h-5 w-5 ${formData.provider === 'ollama' ? 'text-blue-600' : 'text-gray-500'}`} />
                                        <span className="font-medium text-gray-900">Local (Ollama)</span>
                                    </div>
                                    <p className="text-xs text-gray-500">Local LLM via Ollama endpoint.</p>
                                </div>

                                <div
                                    className={`border rounded-lg p-4 cursor-pointer transition-all ${['openai', 'anthropic', 'custom'].includes(formData.provider) ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500' : 'border-gray-200 hover:border-gray-300'}`}
                                    onClick={() => setFormData({ ...formData, provider: 'openai' })}
                                >
                                    <div className="flex items-center gap-3 mb-2">
                                        <Globe className={`h-5 w-5 ${['openai', 'anthropic', 'custom'].includes(formData.provider) ? 'text-blue-600' : 'text-gray-500'}`} />
                                        <span className="font-medium text-gray-900">External API</span>
                                    </div>
                                    <p className="text-xs text-gray-500">Connect to OpenAI, Anthropic or custom endpoint.</p>
                                </div>
                            </div>
                        </div>

                        {['openai', 'anthropic', 'custom'].includes(formData.provider) && (
                            <div className="space-y-4 pt-4 border-t border-gray-50">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Provider</label>
                                    <select
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                        value={formData.provider}
                                        onChange={e => setFormData({ ...formData, provider: e.target.value })}
                                    >
                                        <option value="openai">OpenAI</option>
                                        <option value="anthropic">Anthropic</option>
                                        <option value="custom">Custom</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Endpoint URL</label>
                                    <input
                                        type="url"
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                        value={formData.endpoint_url}
                                        onChange={e => setFormData({ ...formData, endpoint_url: e.target.value })}
                                        placeholder="https://api.openai.com/v1..."
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">API Key</label>
                                    <input
                                        type="password"
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                        value={formData.api_key_ref}
                                        onChange={e => setFormData({ ...formData, api_key_ref: e.target.value })}
                                        placeholder="sk-..."
                                    />
                                </div>
                            </div>
                        )}

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">System Prompt (Optional)</label>
                            <textarea
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                rows={3}
                                value={formData.system_prompt}
                                onChange={e => setFormData({ ...formData, system_prompt: e.target.value })}
                                placeholder="Optional system prompt to initialize the model with..."
                            />
                        </div>

                        <div className="bg-yellow-50 border border-yellow-100 p-4 rounded-lg flex items-start gap-3">
                            <ShieldAlert className="h-5 w-5 text-yellow-600 mt-0.5 flex-shrink-0" />
                            <div className="text-sm text-yellow-800">
                                <strong>Authorization Required:</strong> By proceeding, you verify you are authorized to test this target. All actions are logged.
                            </div>
                        </div>

                        <div className="flex gap-3">
                            <button
                                type="button"
                                onClick={closeForm}
                                className="flex-1 py-2.5 bg-white border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                disabled={creating}
                                className="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2 shadow-sm"
                            >
                                {creating ? 'Saving...' : (
                                    <>
                                        {editingTargetId ? 'Update Target' : 'Create Target'} <ArrowRight className="h-4 w-4" />
                                    </>
                                )}
                            </button>
                        </div>
                    </form>
                </div>
            )}

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                {targets.length === 0 && !showNewTarget ? (
                    <div className="p-12 text-center text-gray-500 bg-gray-50">
                        <TargetIcon className="h-12 w-12 mx-auto text-gray-300 mb-4" />
                        <h3 className="text-lg font-medium text-gray-900">No targets found</h3>
                        <p className="mb-6">Get started by adding your first target.</p>
                        <button
                            onClick={() => setShowNewTarget(true)}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg inline-flex items-center gap-2 hover:bg-blue-700 transition"
                        >
                            <Plus className="h-5 w-5" />
                            Add New Target
                        </button>
                    </div>
                ) : targets.length > 0 && (
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Provider</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {targets.map((target) => (
                                <tr key={target.id} className="hover:bg-gray-50 transition-colors">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center">
                                            <div className="text-sm font-medium text-gray-900">{target.name}</div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm text-gray-500 capitalize">{target.provider}</div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm text-gray-500">
                                            {new Date(target.created_at).toLocaleDateString()}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium flex justify-end gap-3">
                                        <Link
                                            to={`/runs/${target.id}`}
                                            className="text-blue-600 hover:text-blue-900 inline-flex items-center gap-1"
                                        >
                                            View Setup
                                        </Link>
                                        <button
                                            onClick={() => handleEdit(target)}
                                            className="text-gray-500 hover:text-blue-600 transition-colors"
                                            title="Edit Target"
                                        >
                                            <Edit2 className="h-4 w-4" />
                                        </button>
                                        <button
                                            onClick={() => handleDelete(target.id, target.name)}
                                            className="text-gray-500 hover:text-red-600 transition-colors"
                                            title="Delete Target"
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </button>
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
