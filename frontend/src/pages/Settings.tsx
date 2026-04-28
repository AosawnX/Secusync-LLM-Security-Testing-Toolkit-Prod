import { useEffect, useState } from 'react'
import { Settings as SettingsIcon, Save, RefreshCw, Info, CheckCircle, ExternalLink, Loader } from 'lucide-react'
import { apiClient } from '../api/client'

const LS_KEY = 'secusync_settings'

interface AppSettings {
    hfApiToken: string
    hfParaphraseEndpoint: string
    hfTranslateEndpoint: string
    judgeProvider: string
    judgeApiKey: string
    judgeBaseUrl: string
    maxVariantsPerRun: number
    scanRequestDelayMs: number
}

const DEFAULTS: AppSettings = {
    hfApiToken: '',
    hfParaphraseEndpoint: 'https://api-inference.huggingface.co/models/tuner007/pegasus_paraphrase',
    hfTranslateEndpoint: 'https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-en-fr',
    judgeProvider: 'openai',
    judgeApiKey: '',
    judgeBaseUrl: 'https://api.openai.com/v1',
    maxVariantsPerRun: 50,
    scanRequestDelayMs: 500,
}

function loadSettings(): AppSettings {
    try {
        const raw = localStorage.getItem(LS_KEY)
        if (raw) return { ...DEFAULTS, ...JSON.parse(raw) }
    } catch { /* ignore */ }
    return { ...DEFAULTS }
}

interface FieldProps {
    label: string
    hint?: string
    children: React.ReactNode
}

function Field({ label, hint, children }: FieldProps) {
    return (
        <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">{label}</label>
            {hint && <p className="text-xs text-gray-400">{hint}</p>}
            {children}
        </div>
    )
}

export function Settings() {
    const [settings, setSettings] = useState<AppSettings>(loadSettings)
    const [saved, setSaved] = useState(false)
    const [backendInfo, setBackendInfo] = useState<Record<string, unknown> | null>(null)
    const [migrating, setMigrating] = useState(false)
    const [migrationResult, setMigrationResult] = useState<Record<string, unknown> | null>(null)

    useEffect(() => {
        fetch('http://127.0.0.1:8000/api/demo/target/info')
            .then(r => r.json())
            .then(setBackendInfo)
            .catch(() => setBackendInfo(null))
    }, [])

    const set = (key: keyof AppSettings, value: string | number) =>
        setSettings(prev => ({ ...prev, [key]: value }))

    const handleSave = () => {
        localStorage.setItem(LS_KEY, JSON.stringify(settings))
        setSaved(true)
        setTimeout(() => setSaved(false), 2500)
    }

    const handleReset = () => {
        setSettings({ ...DEFAULTS })
        localStorage.removeItem(LS_KEY)
    }

    const handleMigrateLegacyData = async () => {
        setMigrating(true)
        try {
            const response = await apiClient.post('/migrate')
            setMigrationResult(response.data)
        } catch (err) {
            setMigrationResult({ error: 'Failed to migrate legacy data', details: String(err) })
        } finally {
            setMigrating(false)
        }
    }

    const inputCls = "w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0461E2] font-mono"

    return (
        <div className="space-y-6 max-w-2xl">
            <header>
                <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                    <SettingsIcon className="h-8 w-8 text-[#0461E2]" />
                    Settings
                </h1>
                <p className="text-gray-500 mt-1">
                    Configure API keys, HuggingFace endpoints, and scan defaults.
                    Settings are stored locally in your browser.
                </p>
            </header>

            {/* HuggingFace */}
            <section className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 space-y-4">
                <h2 className="text-lg font-semibold text-[#1B2771]">HuggingFace Inference</h2>
                <p className="text-xs text-gray-400">
                    Required for <code className="bg-gray-100 px-1 rounded">paraphrase</code> and{' '}
                    <code className="bg-gray-100 px-1 rounded">lang_switch</code> mutation strategies.
                    Leave blank to use deterministic strategies only.
                </p>

                <Field label="HF API Token" hint="Starts with hf_…  Never committed to source control.">
                    <input
                        type="password"
                        value={settings.hfApiToken}
                        onChange={e => set('hfApiToken', e.target.value)}
                        placeholder="hf_xxxxxxxxxxxxxxxx"
                        className={inputCls}
                    />
                </Field>

                <Field label="Paraphrase Endpoint">
                    <input
                        type="text"
                        value={settings.hfParaphraseEndpoint}
                        onChange={e => set('hfParaphraseEndpoint', e.target.value)}
                        className={inputCls}
                    />
                </Field>

                <Field label="Translation Endpoint (EN→FR)">
                    <input
                        type="text"
                        value={settings.hfTranslateEndpoint}
                        onChange={e => set('hfTranslateEndpoint', e.target.value)}
                        className={inputCls}
                    />
                </Field>
            </section>

            {/* Judge LLM */}
            <section className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 space-y-4">
                <h2 className="text-lg font-semibold text-[#1B2771]">Semantic Judge LLM</h2>
                <p className="text-xs text-gray-400">
                    Used by the Hybrid Analysis engine for semantic verdict classification.
                    Only redacted outputs are sent — raw secrets never leave local scope.
                </p>

                <Field label="Provider">
                    <select
                        value={settings.judgeProvider}
                        onChange={e => set('judgeProvider', e.target.value)}
                        className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0461E2]"
                    >
                        <option value="openai">OpenAI</option>
                        <option value="anthropic">Anthropic (Claude)</option>
                        <option value="ollama">Ollama (Local)</option>
                    </select>
                </Field>

                <Field label="Judge API Key" hint="Stored in browser only — never sent to SECUSYNC servers.">
                    <input
                        type="password"
                        value={settings.judgeApiKey}
                        onChange={e => set('judgeApiKey', e.target.value)}
                        placeholder="sk-…"
                        className={inputCls}
                    />
                </Field>

                <Field label="Base URL" hint="Leave default for OpenAI/Anthropic. Set http://localhost:11434/v1 for Ollama.">
                    <input
                        type="text"
                        value={settings.judgeBaseUrl}
                        onChange={e => set('judgeBaseUrl', e.target.value)}
                        className={inputCls}
                    />
                </Field>
            </section>

            {/* Scan defaults */}
            <section className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 space-y-4">
                <h2 className="text-lg font-semibold text-[#1B2771]">Scan Defaults</h2>

                <Field label="Max Variants Per Run" hint="Hard cap on total prompts per scan (PRD §7 — 20-prompt run ≤ 5 min).">
                    <input
                        type="number"
                        min={1}
                        max={200}
                        value={settings.maxVariantsPerRun}
                        onChange={e => set('maxVariantsPerRun', parseInt(e.target.value, 10))}
                        className={inputCls}
                    />
                </Field>

                <Field label="Request Delay (ms)" hint="Rate-limit delay between TLLM calls. Increase for strict rate-limited APIs.">
                    <input
                        type="number"
                        min={0}
                        max={10000}
                        step={100}
                        value={settings.scanRequestDelayMs}
                        onChange={e => set('scanRequestDelayMs', parseInt(e.target.value, 10))}
                        className={inputCls}
                    />
                </Field>
            </section>

            {/* Data Migration */}
            {migrationResult === null && (
                <section className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 space-y-3">
                    <h2 className="text-lg font-semibold text-[#1B2771] flex items-center gap-2">
                        <Info className="h-5 w-5 text-[#0461E2]" />
                        Migrate Legacy Data
                    </h2>
                    <p className="text-xs text-gray-500">
                        If you have pre-authentication demo targets and scans, click below to migrate them to your authenticated account.
                        This is a one-time operation.
                    </p>
                    <button
                        onClick={handleMigrateLegacyData}
                        disabled={migrating}
                        className="flex items-center gap-2 px-4 py-2 bg-[#0461E2] text-white font-medium rounded-lg hover:bg-[#1B2771] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {migrating ? <Loader className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                        {migrating ? 'Migrating…' : 'Migrate Legacy Data'}
                    </button>
                </section>
            )}

            {/* Migration Result */}
            {migrationResult && (
                <section className={`rounded-xl border shadow-sm p-6 space-y-3 ${migrationResult.error ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}`}>
                    <h2 className="text-lg font-semibold flex items-center gap-2">
                        {migrationResult.error ? (
                            <span className="text-red-700">❌ Migration Failed</span>
                        ) : (
                            <span className="text-green-700">✅ Migration Complete</span>
                        )}
                    </h2>
                    {migrationResult.error ? (
                        <p className="text-sm text-red-600">{migrationResult.details || migrationResult.error}</p>
                    ) : (
                        <div className="text-sm text-green-700 space-y-1">
                            <p>Profiles migrated: <strong>{migrationResult.profiles_migrated}</strong></p>
                            <p>Scan runs migrated: <strong>{migrationResult.runs_migrated}</strong></p>
                        </div>
                    )}
                    <button
                        onClick={() => { setMigrationResult(null); window.location.reload(); }}
                        className="flex items-center gap-2 px-4 py-2 bg-[#0461E2] text-white font-medium rounded-lg hover:bg-[#1B2771] transition-colors"
                    >
                        <CheckCircle className="h-4 w-4" />
                        Reload to View Data
                    </button>
                </section>
            )}

            {/* Demo TLLM info */}
            <section className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 space-y-3">
                <h2 className="text-lg font-semibold text-[#1B2771] flex items-center gap-2">
                    <Info className="h-5 w-5 text-[#0461E2]" />
                    Demo Vulnerable TLLM
                </h2>
                <p className="text-xs text-gray-500">
                    A synthetic vulnerable TLLM is bundled for defense demonstrations.
                    Create a new Target with{' '}
                    <code className="bg-gray-100 px-1 rounded">Provider: custom</code> and{' '}
                    <code className="bg-gray-100 px-1 rounded">Endpoint: http://127.0.0.1:8000/api/demo/target</code>.
                </p>
                <div className={`flex items-center gap-2 text-sm font-medium ${backendInfo ? 'text-green-600' : 'text-gray-400'}`}>
                    {backendInfo
                        ? <><CheckCircle className="h-4 w-4" /> Demo TLLM is online</>
                        : <><RefreshCw className="h-4 w-4 animate-spin" /> Checking demo status…</>
                    }
                </div>
                {backendInfo && (
                    <a
                        href="http://127.0.0.1:8000/api/demo/target/info"
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-xs text-[#0461E2] hover:underline"
                    >
                        View endpoint metadata <ExternalLink className="h-3 w-3" />
                    </a>
                )}
            </section>

            {/* Actions */}
            <div className="flex gap-3">
                <button
                    onClick={handleSave}
                    className="flex items-center gap-2 px-6 py-2.5 bg-[#0461E2] text-white font-medium rounded-lg hover:bg-[#1B2771] transition-colors"
                >
                    {saved ? <CheckCircle className="h-4 w-4" /> : <Save className="h-4 w-4" />}
                    {saved ? 'Saved!' : 'Save Settings'}
                </button>
                <button
                    onClick={handleReset}
                    className="flex items-center gap-2 px-6 py-2.5 bg-white border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors"
                >
                    <RefreshCw className="h-4 w-4" />
                    Reset to Defaults
                </button>
            </div>
        </div>
    )
}
