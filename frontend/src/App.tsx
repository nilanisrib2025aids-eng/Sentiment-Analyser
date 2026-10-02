import { useEffect, useMemo, useState } from 'react';
import { BarChart3, FileText, Gauge, LayoutDashboard, LogIn, MessageSquareText, ShieldCheck, Sparkles, UploadCloud, UserCog, Users } from 'lucide-react';
import { Link, Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import { ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, LineChart, Line } from 'recharts';
import { apiFetch, apiUpload, clearAuthToken, getAuthToken, setAuthToken, type UserSession } from './services/api';

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/analyzer', label: 'Feedback Analyzer', icon: Gauge },
  { to: '/explorer', label: 'Feedback Explorer', icon: FileText },
  { to: '/rag', label: 'RAG Assistant', icon: MessageSquareText },
  { to: '/documents', label: 'Documents', icon: UploadCloud },
  { to: '/admin', label: 'Admin', icon: UserCog, admin: true },
];

function App() {
  const [session, setSession] = useState<UserSession | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getAuthToken();
    if (!token) {
      setLoading(false);
      return;
    }
    apiFetch<{ id: number; name: string; email: string; role: string; is_active: boolean }>('/users/me')
      .then((user) => setSession(user))
      .catch(() => clearAuthToken())
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="flex min-h-screen items-center justify-center text-slate-600">Loading platform...</div>;
  }

  return (
    <Routes>
      <Route path="/" element={<LandingPage session={session} setSession={setSession} />} />
      <Route path="/login" element={<LoginPage setSession={setSession} />} />
      <Route path="/register" element={<RegisterPage setSession={setSession} />} />
      <Route path="/dashboard" element={<ProtectedRoute session={session}><DashboardPage session={session} /></ProtectedRoute>} />
      <Route path="/analyzer" element={<ProtectedRoute session={session}><AnalyzerPage /></ProtectedRoute>} />
      <Route path="/explorer" element={<ProtectedRoute session={session}><ExplorerPage /></ProtectedRoute>} />
      <Route path="/rag" element={<ProtectedRoute session={session}><RAGPage /></ProtectedRoute>} />
      <Route path="/documents" element={<ProtectedRoute session={session}><DocumentsPage /></ProtectedRoute>} />
      <Route path="/admin" element={<AdminRoute session={session}><AdminPage /></AdminRoute>} />
      <Route path="*" element={<Navigate to={session ? '/dashboard' : '/'} replace />} />
    </Routes>
  );
}

function ProtectedRoute({ session, children }: { session: UserSession | null; children: JSX.Element }) {
  if (!session) return <Navigate to="/login" replace />;
  return children;
}

function AdminRoute({ session, children }: { session: UserSession | null; children: JSX.Element }) {
  if (!session) return <Navigate to="/login" replace />;
  if (session.role !== 'ADMIN') return <Navigate to="/dashboard" replace />;
  return children;
}

function LandingPage({ session, setSession }: { session: UserSession | null; setSession: (value: UserSession | null) => void }) {
  const navigate = useNavigate();
  const handleLogout = async () => {
    try {
      await apiFetch('/auth/logout');
    } finally {
      clearAuthToken();
      setSession(null);
      navigate('/');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <div className="text-xl font-bold">Sentiment Intelligence Platform</div>
        <div className="flex items-center gap-4">
          {session ? (
            <>
              <Link to="/dashboard" className="rounded-full bg-white px-4 py-2 text-sm font-medium text-slate-900">Dashboard</Link>
              <button onClick={handleLogout} className="rounded-full border border-white/20 px-4 py-2 text-sm">Logout</button>
            </>
          ) : (
            <>
              <Link to="/login" className="rounded-full border border-white/20 px-4 py-2 text-sm">Login</Link>
              <Link to="/register" className="rounded-full bg-indigo-500 px-4 py-2 text-sm font-medium text-white">Register</Link>
            </>
          )}
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 pb-20 pt-10">
        <section className="grid items-center gap-10 lg:grid-cols-2">
          <div>
            <p className="mb-4 inline-flex rounded-full bg-indigo-500/20 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-indigo-200">AI-powered feedback intelligence</p>
            <h1 className="text-5xl font-bold leading-tight">AI-powered analysis of feedback, opinions and customer sentiment.</h1>
            <p className="mt-5 max-w-xl text-lg text-slate-300">Analyze user sentiment, detect recurring issues, retrieve grounded insights, and surface actionable trends across your organization.</p>
            <div className="mt-8 flex gap-4">
              <Link to={session ? '/dashboard' : '/login'} className="rounded-xl bg-indigo-500 px-6 py-3 font-medium text-white">Analyze Feedback</Link>
              <Link to="/register" className="rounded-xl border border-white/20 px-6 py-3 font-medium text-white">Get Started</Link>
            </div>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <FeatureCard title="Sentiment Analysis" icon={Sparkles} description="Classify feedback as positive, negative, or neutral with confidence scores." />
            <FeatureCard title="RAG Insights" icon={MessageSquareText} description="Ask natural-language questions grounded in departmental feedback and documents." />
            <FeatureCard title="Analytics" icon={BarChart3} description="Track sentiment trends by category, product, department, and location." />
            <FeatureCard title="Security" icon={ShieldCheck} description="RBAC, JWT access, audit logs, and protected retrieval controls." />
          </div>
        </section>
      </main>
    </div>
  );
}

function FeatureCard({ title, description, icon: Icon }: { title: string; description: string; icon: any }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm">
      <div className="mb-4 inline-flex rounded-xl bg-indigo-500/20 p-3 text-indigo-200"><Icon size={24} /></div>
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="mt-2 text-sm text-slate-300">{description}</p>
    </div>
  );
}

function LoginPage({ setSession }: { setSession: (value: UserSession | null) => void }) {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: 'admin@sih.local', password: 'Admin@123' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await apiFetch<{ access_token: string; user: UserSession }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify(form),
      });
      setAuthToken(response.access_token);
      setSession(response.user);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthCard title="Login" subtitle="Welcome back">
      <form onSubmit={handleSubmit} className="space-y-4">
        <input className="w-full rounded-xl border border-slate-200 p-3" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="Email" />
        <input type="password" className="w-full rounded-xl border border-slate-200 p-3" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="Password" />
        {error && <div className="rounded-xl bg-red-50 p-3 text-sm text-red-700">{error}</div>}
        <button disabled={loading} className="w-full rounded-xl bg-indigo-600 px-4 py-3 font-medium text-white">{loading ? 'Signing in...' : 'Login'}</button>
        <Link to="/register" className="block text-center text-sm text-indigo-700">Need an account? Register</Link>
      </form>
    </AuthCard>
  );
}

function RegisterPage({ setSession }: { setSession: (value: UserSession | null) => void }) {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: 'Demo User', email: 'demo@sih.local', password: 'Demo@123' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await apiFetch<{ access_token: string; user: UserSession }>('/auth/register', {
        method: 'POST',
        body: JSON.stringify(form),
      });
      setAuthToken(response.access_token);
      setSession(response.user);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthCard title="Register" subtitle="Create your account">
      <form onSubmit={handleSubmit} className="space-y-4">
        <input className="w-full rounded-xl border border-slate-200 p-3" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Full name" />
        <input className="w-full rounded-xl border border-slate-200 p-3" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="Email" />
        <input type="password" className="w-full rounded-xl border border-slate-200 p-3" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="Password" />
        {error && <div className="rounded-xl bg-red-50 p-3 text-sm text-red-700">{error}</div>}
        <button disabled={loading} className="w-full rounded-xl bg-indigo-600 px-4 py-3 font-medium text-white">{loading ? 'Creating account...' : 'Register'}</button>
        <Link to="/login" className="block text-center text-sm text-indigo-700">Already have an account? Login</Link>
      </form>
    </AuthCard>
  );
}

function AuthCard({ title, subtitle, children }: { title: string; subtitle: string; children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 p-6">
      <div className="card w-full max-w-md p-8">
        <div className="mb-6 text-center">
          <h2 className="text-2xl font-bold">{title}</h2>
          <p className="text-sm text-slate-500">{subtitle}</p>
        </div>
        {children}
      </div>
    </div>
  );
}

function DashboardPage({ session }: { session: UserSession | null }) {
  const [overview, setOverview] = useState<any>(null);
  const [trends, setTrends] = useState<any[]>([]);
  useEffect(() => {
    apiFetch<any>('/analytics/overview').then(setOverview).catch(console.error);
    apiFetch<any[]>('/analytics/trends').then(setTrends).catch(console.error);
  }, []);

  const pieData = [
    { name: 'Positive', value: overview?.positive_percentage || 0, color: '#22c55e' },
    { name: 'Negative', value: overview?.negative_percentage || 0, color: '#ef4444' },
    { name: 'Neutral', value: overview?.neutral_percentage || 0, color: '#fbbf24' },
  ];

  return (
    <Shell session={session}>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <div className="rounded-full bg-emerald-100 px-3 py-1 text-sm text-emerald-700">Realtime insights</div>
        </div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-6">
          <StatCard label="Total feedback" value={overview?.total_feedback ?? 0} />
          <StatCard label="Positive %" value={`${overview?.positive_percentage ?? 0}%`} tone="green" />
          <StatCard label="Negative %" value={`${overview?.negative_percentage ?? 0}%`} tone="red" />
          <StatCard label="Neutral %" value={`${overview?.neutral_percentage ?? 0}%`} tone="amber" />
          <StatCard label="Avg confidence" value={`${overview?.average_confidence ?? 0}`} tone="sky" />
          <StatCard label="Processed today" value={overview?.processed_today ?? 0} tone="purple" />
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <div className="card p-5">
            <h3 className="mb-4 text-lg font-semibold">Sentiment distribution</h3>
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" outerRadius={85} innerRadius={55}>
                  {pieData.map((entry) => <Cell key={entry.name} fill={entry.color} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="card p-5">
            <h3 className="mb-4 text-lg font-semibold">Trend</h3>
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={trends}>
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="positive" stroke="#22c55e" strokeWidth={2} />
                <Line type="monotone" dataKey="negative" stroke="#ef4444" strokeWidth={2} />
                <Line type="monotone" dataKey="neutral" stroke="#fbbf24" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </Shell>
  );
}

function AnalyzerPage() {
  const [text, setText] = useState('Customer service was excellent and the issue was resolved quickly.');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const response = await apiFetch<{ feedback_id: number; result: any }>('/sentiment/analyze', {
        method: 'POST',
        body: JSON.stringify({ text, source: 'manual', category: 'support', department: 'customer_service', product: 'platform', location: 'chennai' }),
      });
      setResult(response.result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Gemini analysis failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Shell session={null}>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Feedback Analyzer</h1>
        <div className="card p-6">
          <textarea value={text} onChange={(e) => setText(e.target.value)} className="h-36 w-full rounded-xl border border-slate-200 p-4" placeholder="Enter customer feedback or complaint..." />
          <div className="mt-4 flex justify-between">
            <div className="text-sm text-slate-500">Gemini analyzes sentiment, language, and evidence from the feedback.</div>
            <button disabled={loading} onClick={handleAnalyze} className="rounded-xl bg-indigo-600 px-5 py-3 font-medium text-white disabled:opacity-60">{loading ? 'Analyzing...' : 'Analyze sentiment'}</button>
          </div>
        </div>
        {error && <div role="alert" className="rounded-xl bg-red-50 p-4 text-sm text-red-700">{error}</div>}
        {result && (
          <div className="card p-6">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-xl font-semibold">Sentiment result</h3>
              <span className="rounded-full bg-indigo-100 px-3 py-1 text-sm font-medium text-indigo-700">{result.sentiment}</span>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div><strong>Confidence:</strong> {result.confidence.toFixed(2)}</div>
              <div><strong>Language:</strong> {result.language}</div>
              <div><strong>Positive:</strong> {result.positive_score.toFixed(2)}</div>
              <div><strong>Negative:</strong> {result.negative_score.toFixed(2)}</div>
              <div><strong>Neutral:</strong> {result.neutral_score.toFixed(2)}</div>
              <div><strong>Keywords:</strong> {result.important_keywords.join(', ') || 'N/A'}</div>
            </div>
            <div className="mt-4 rounded-xl bg-slate-50 p-4 text-sm text-slate-700">{result.explanation}</div>
          </div>
        )}
      </div>
    </Shell>
  );
}

function ExplorerPage() {
  const [items, setItems] = useState<any[]>([]);
  useEffect(() => {
    apiFetch<any[]>('/feedback').then(setItems).catch(console.error);
  }, []);

  return (
    <Shell session={null}>
      <div className="space-y-4">
        <h1 className="text-3xl font-bold">Feedback Explorer</h1>
        <div className="card overflow-hidden">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="p-3">Feedback</th>
                <th className="p-3">Sentiment</th>
                <th className="p-3">Confidence</th>
                <th className="p-3">Category</th>
                <th className="p-3">Department</th>
                <th className="p-3">Date</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id} className="border-t border-slate-200">
                  <td className="p-3 max-w-md">{item.text.slice(0, 100)}</td>
                  <td className="p-3">{item.sentiment?.sentiment || 'Pending'}</td>
                  <td className="p-3">{item.sentiment?.confidence ? item.sentiment.confidence.toFixed(2) : '—'}</td>
                  <td className="p-3">{item.category}</td>
                  <td className="p-3">{item.department}</td>
                  <td className="p-3">{new Date(item.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </Shell>
  );
}

function RAGPage() {
  const [question, setQuestion] = useState('Why are customers unhappy?');
  const [answer, setAnswer] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    setLoading(true);
    try {
      const result = await apiFetch<any>('/rag/query', {
        method: 'POST',
        body: JSON.stringify({ question, top_k: 5 }),
      });
      setAnswer(result);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Shell session={null}>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">RAG AI Assistant</h1>
        <div className="card p-6">
          <textarea value={question} onChange={(e) => setQuestion(e.target.value)} className="h-28 w-full rounded-xl border border-slate-200 p-4" />
          <div className="mt-4 flex justify-end">
            <button onClick={handleAsk} className="rounded-xl bg-indigo-600 px-5 py-3 font-medium text-white">{loading ? 'Retrieving...' : 'Ask question'}</button>
          </div>
        </div>
        {answer && (
          <div className="card p-6">
            <h3 className="text-lg font-semibold">Answer</h3>
            <p className="mt-3 text-slate-700">{answer.answer}</p>
            <div className="mt-6">
              <h4 className="font-semibold">Sources</h4>
              <ul className="mt-2 list-disc space-y-1 pl-6 text-sm text-slate-600">
                {answer.sources.map((source: string) => <li key={source}>{source}</li>)}
              </ul>
            </div>
          </div>
        )}
      </div>
    </Shell>
  );
}

function DocumentsPage() {
  const [docs, setDocs] = useState<any[]>([]);
  const [file, setFile] = useState<File | null>(null);

  useEffect(() => {
    apiFetch<any[]>('/documents').then(setDocs).catch(console.error);
  }, []);

  const handleUpload = async () => {
    if (!file) return;
    const response = await apiUpload('/documents/upload', file);
    setDocs((prev) => [response, ...prev]);
    setFile(null);
  };

  return (
    <Shell session={null}>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Documents</h1>
        <div className="card p-6">
          <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} className="block w-full rounded-xl border border-slate-200 p-3" />
          <button onClick={handleUpload} className="mt-4 rounded-xl bg-indigo-600 px-4 py-3 font-medium text-white">Upload document</button>
        </div>
        <div className="card overflow-hidden">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-slate-50">
              <tr><th className="p-3">Filename</th><th className="p-3">Type</th><th className="p-3">Status</th></tr>
            </thead>
            <tbody>
              {docs.map((doc) => (
                <tr key={doc.id} className="border-t border-slate-200">
                  <td className="p-3">{doc.filename}</td>
                  <td className="p-3">{doc.file_type}</td>
                  <td className="p-3">{doc.processing_status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </Shell>
  );
}

function AdminPage() {
  const [aiStatus, setAiStatus] = useState<{ provider: string; model: string; configured: boolean } | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    apiFetch<{ provider: string; model: string; configured: boolean }>('/admin/ai-status')
      .then(setAiStatus)
      .catch((err) => setError(err instanceof Error ? err.message : 'Unable to load AI status.'));
  }, []);

  return (
    <Shell session={null}>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Admin Panel</h1>
        <div className="card p-6">
          <h2 className="text-lg font-semibold">Gemini AI</h2>
          {error ? <p role="alert" className="mt-2 text-sm text-red-700">{error}</p> : aiStatus && (
            <div className="mt-3 space-y-2 text-sm text-slate-600">
              <p>Provider: {aiStatus.provider}</p>
              <p>Model: {aiStatus.model}</p>
              <p>API key: {aiStatus.configured ? 'Configured' : 'Missing; add GEMINI_API_KEY to backend/.env and restart the API.'}</p>
            </div>
          )}
        </div>
      </div>
    </Shell>
  );
}

function Shell({ session, children }: { session: UserSession | null; children: React.ReactNode }) {
  const location = useLocation();
  const navigate = useNavigate();

  const visibleNav = navItems.filter((item) => item.admin ? session?.role === 'ADMIN' : true);

  const handleLogout = async () => {
    try {
      await apiFetch('/auth/logout');
    } finally {
      clearAuthToken();
      navigate('/');
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-100">
      <aside className="hidden w-72 bg-slate-900 p-6 text-white lg:block">
        <div className="mb-8 text-2xl font-bold">SIP</div>
        <nav className="space-y-2">
          {visibleNav.map(({ to, label, icon: Icon }) => (
            <Link key={to} to={to} className={`flex items-center gap-3 rounded-xl px-4 py-3 ${location.pathname === to ? 'bg-indigo-500' : 'text-slate-300 hover:bg-slate-800'}`}>
              <Icon size={18} />
              {label}
            </Link>
          ))}
        </nav>
        <div className="mt-8 rounded-xl bg-slate-800 p-4">
          <div className="text-sm text-slate-400">Signed in as</div>
          <div className="mt-2 font-semibold">{session?.name || 'User'}</div>
          <div className="text-sm text-slate-400">{session?.role || 'ROLE'}</div>
          <button onClick={handleLogout} className="mt-4 w-full rounded-xl border border-slate-600 px-3 py-2 text-sm">Logout</button>
        </div>
      </aside>
      <main className="flex-1 p-6 md:p-8">
        <div className="mb-6 flex items-center justify-between">
          <div className="text-sm text-slate-500">Sentiment Intelligence Platform</div>
          <div className="flex items-center gap-3">
            <div className="rounded-full bg-white px-3 py-2 text-sm font-medium text-slate-700">{session?.role || 'USER'}</div>
            <button onClick={handleLogout} className="rounded-full border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700">Logout</button>
          </div>
        </div>
        {children}
      </main>
    </div>
  );
}

function StatCard({ label, value, tone }: { label: string; value: string | number; tone?: 'green' | 'red' | 'amber' | 'sky' | 'purple' }) {
  const classes = {
    green: 'bg-emerald-50 text-emerald-700',
    red: 'bg-red-50 text-red-700',
    amber: 'bg-amber-50 text-amber-700',
    sky: 'bg-sky-50 text-sky-700',
    purple: 'bg-violet-50 text-violet-700',
  };
  return (
    <div className="card p-4">
      <div className="text-sm text-slate-500">{label}</div>
      <div className={`mt-3 inline-flex rounded-full px-3 py-1 text-sm font-semibold ${classes[tone || 'sky']}`}>{value}</div>
    </div>
  );
}

export default App;
