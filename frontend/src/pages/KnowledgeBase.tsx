import { useEffect, useMemo, useState } from 'react'
import { Plus, Trash2, Book } from 'lucide-react'
import { apiClient } from '../api/client'

/** KB entry as returned by `GET /api/kb/entries`. Kept in sync with
 *  `backend/app/schemas/kb.py :: KBEntryResponse`. */
interface KBEntry {
    id: string
    attack_class: string
    title: string
    template: string
    tags: string[]
    source: string | null
}

// Mirrors the backend _ALLOWED_CLASSES. Displayed order = scan-config order.
const ATTACK_CLASSES: { id: string; label: string }[] = [
    { id: 'prompt_injection', label: 'Prompt Injection' },
    { id: 'system_prompt_leakage', label: 'System Prompt Leakage' },
    { id: 'file_poisoning', label: 'File Poisoning' },
    { id: 'sensitive_info_disclosure', label: 'Sensitive Info Disclosure' },
]

export function KnowledgeBase() {
    const [entries, setEntries] = useState<KBEntry[]>([])
    const [loading, setLoading] = useState(true)
    const [filter, setFilter] = useState<string>('')  // '' = all
    const [showForm, setShowForm] = useState(false)
    const [saving, setSaving] = useState(false)

    // New-entry form state — kept minimal on purpose. Source is pinned to
    // 'user' since the form is the only path for user-contributed rows.
    const [form, setForm] = useState({
        attack_class: 'prompt_injection',
        title: '',
        template: '',
        tags: '',  // comma-separated; split before POST
    })

    const reload = async () => {
        setLoading(true)
        try {
            const url = filter ? `/kb/entries?attack_class=${filter}` : '/kb/entries'
            const res = await apiClient.get(url)
            setEntries(res.data || [])
        } catch (err) {
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        reload()
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [filter])

    // Per-class counts for the filter chips. Memoised because the full list
    // is refetched only on filter change, so this recomputes cheaply.
    const counts = useMemo(() => {
        const c: Record<string, number> = {}
        for (const e of entries) c[e.attack_class] = (c[e.attack_class] || 0) + 1
        return c
    }, [entries])

    const handleCreate = async () => {
        if (!form.title.trim() || !form.template.trim()) {
            alert('Title and template are required.')
            return
        }
        setSaving(true)
        try {
            await apiClient.post('/kb/entries', {
                attack_class: form.attack_class,
                title: form.title.trim(),
                template: form.template,
                tags: form.tags.split(',').map(t => t.trim()).filter(Boolean),
                source: 'user',
            })
            setForm({ attack_class: form.attack_class, title: '', template: '', tags: '' })
            setShowForm(false)
            await reload()
        } catch (err: any) {
            alert(err?.response?.data?.detail || 'Failed to create entry')
        } finally {
            setSaving(false)
        }
    }

    const handleDelete = async (id: string) => {
        if (!confirm('Delete this template?')) return
        try {
            await apiClient.delete(`/kb/entries/${id}`)
            await reload()
        } catch (err) {
            console.error(err)
            alert('Delete failed')
        }
    }

    return (
        <div className="space-y-6">
            <header className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <Book className="h-7 w-7 text-blue-600" />
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">Knowledge Base</h1>
                        <p className="text-gray-500 text-sm">Adversarial templates used to seed scans.</p>
                    </div>
                </div>
                <button
                    onClick={() => setShowForm(s => !s)}
                    className="flex items-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg"
                >
                    <Plus className="h-4 w-4" />
                    {showForm ? 'Cancel' : 'Add Template'}
                </button>
            </header>

            {/* Filter chips — `filter === ''` means show everything. */}
            <div className="flex flex-wrap gap-2">
                <button
                    onClick={() => setFilter('')}
                    className={`px-3 py-1 rounded-full text-xs font-medium border ${filter === '' ? 'bg-blue-50 border-blue-200 text-blue-700' : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'}`}
                >
                    All
                </button>
                {ATTACK_CLASSES.map(c => (
                    <button
                        key={c.id}
                        onClick={() => setFilter(c.id)}
                        className={`px-3 py-1 rounded-full text-xs font-medium border ${filter === c.id ? 'bg-blue-50 border-blue-200 text-blue-700' : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'}`}
                    >
                        {c.label}{counts[c.id] ? ` (${counts[c.id]})` : ''}
                    </button>
                ))}
            </div>

            {showForm && (
                <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 space-y-4">
                    <h2 className="font-semibold">New Template</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <label className="block">
                            <span className="text-xs font-semibold uppercase tracking-wide text-gray-500">Attack Class</span>
                            <select
                                value={form.attack_class}
                                onChange={e => setForm(f => ({ ...f, attack_class: e.target.value }))}
                                className="mt-1 w-full border border-gray-300 rounded px-3 py-2 text-sm"
                            >
                                {ATTACK_CLASSES.map(c => (
                                    <option key={c.id} value={c.id}>{c.label}</option>
                                ))}
                            </select>
                        </label>
                        <label className="block">
                            <span className="text-xs font-semibold uppercase tracking-wide text-gray-500">Title</span>
                            <input
                                value={form.title}
                                onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
                                className="mt-1 w-full border border-gray-300 rounded px-3 py-2 text-sm"
                                placeholder="e.g. Payload via fake footer"
                            />
                        </label>
                    </div>
                    <label className="block">
                        <span className="text-xs font-semibold uppercase tracking-wide text-gray-500">Template</span>
                        <textarea
                            value={form.template}
                            onChange={e => setForm(f => ({ ...f, template: e.target.value }))}
                            rows={6}
                            className="mt-1 w-full border border-gray-300 rounded px-3 py-2 text-sm font-mono"
                            placeholder="Use [Document body] as the carrier placeholder for file_poisoning."
                        />
                    </label>
                    <label className="block">
                        <span className="text-xs font-semibold uppercase tracking-wide text-gray-500">Tags (comma-separated)</span>
                        <input
                            value={form.tags}
                            onChange={e => setForm(f => ({ ...f, tags: e.target.value }))}
                            className="mt-1 w-full border border-gray-300 rounded px-3 py-2 text-sm"
                            placeholder="e.g. jailbreak, custom"
                        />
                    </label>
                    <div className="flex justify-end">
                        <button
                            onClick={handleCreate}
                            disabled={saving}
                            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg disabled:opacity-50"
                        >
                            {saving ? 'Saving…' : 'Create Template'}
                        </button>
                    </div>
                </div>
            )}

            <div className="bg-white rounded-xl border border-gray-100 shadow-sm">
                {loading ? (
                    <div className="p-8 text-gray-500">Loading templates…</div>
                ) : entries.length === 0 ? (
                    <div className="p-8 text-gray-400 italic">No templates yet. Add one above.</div>
                ) : (
                    <ul className="divide-y divide-gray-100">
                        {entries.map(e => (
                            <li key={e.id} className="p-4 flex items-start justify-between gap-4">
                                <div className="min-w-0 flex-1">
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className="px-2 py-0.5 text-[10px] font-medium rounded bg-gray-100 text-gray-700 uppercase tracking-wide">
                                            {e.attack_class.replace(/_/g, ' ')}
                                        </span>
                                        {e.source && (
                                            <span className="text-[10px] text-gray-400">{e.source}</span>
                                        )}
                                    </div>
                                    <p className="font-semibold text-gray-900">{e.title}</p>
                                    <pre className="mt-1 text-xs text-gray-600 font-mono whitespace-pre-wrap break-words line-clamp-3">
                                        {e.template}
                                    </pre>
                                    {e.tags.length > 0 && (
                                        <div className="mt-2 flex flex-wrap gap-1">
                                            {e.tags.map(t => (
                                                <span key={t} className="text-[10px] px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-100">
                                                    {t}
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                </div>
                                <button
                                    onClick={() => handleDelete(e.id)}
                                    title="Delete"
                                    className="p-2 rounded hover:bg-red-50 text-gray-400 hover:text-red-600 shrink-0"
                                >
                                    <Trash2 className="h-4 w-4" />
                                </button>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    )
}
