import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { Sparkles, ArrowRight, ShieldCheck } from "lucide-react";
import { useAuth, DEMO_ACCOUNTS, routeFor } from "../state/auth";
import { useDestination } from "../state/destination";
import { destShort } from "../lib/destCopy";
import { useToast } from "../state/toast";
import { Button, ErrorNote } from "../components/ui";

export default function LoginPage() {
  const { login } = useAuth();
  const { current } = useDestination();
  const { toast } = useToast();
  const navigate = useNavigate();
  const location = useLocation() as { state?: { from?: string } };
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  const doLogin = async (e: string, p: string) => {
    setBusy(true);
    setErr("");
    try {
      const u = await login(e, p);
      toast(`Welcome back, ${u.name.split(" ")[0]}!`);
      const dest = location.state?.from || routeFor(u.role) || "/";
      navigate(dest);
    } catch (er) {
      setErr(er instanceof Error ? er.message : "Login failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="relative hidden flex-col justify-between overflow-hidden bg-teal-dark p-10 text-white lg:flex">
        <div className="absolute inset-0 bg-mesh-soft" />
        <div className="absolute inset-0 bg-dots-light opacity-50" />
        <div className="relative flex items-center gap-2.5">
          <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-saffron text-teal-dark">
            <Sparkles className="h-5 w-5" />
          </span>
          <span className="leading-tight">
            <span className="block font-display text-xl font-bold">Virsa</span>
            <span className="block text-[10px] uppercase tracking-[0.22em] text-sand-200">{destShort(current)} tourism</span>
          </span>
        </div>
        <div className="relative">
          <h1 className="font-display text-4xl font-bold leading-tight text-glow-sun">
            One ecosystem.<br />Every role,<br />one city.
          </h1>
          <p className="mt-3 max-w-md text-sm text-sand-300">
            Tourists explore. Residents report. Makers sell. Authorities act. Sign in and pick your lane.
          </p>
          <div className="mt-6 flex items-center gap-3 text-xs text-sand-300">
            <ShieldCheck className="h-4 w-4 text-marigold" /> Demo instance — tap any account below to jump in.
          </div>
        </div>
        <p className="relative text-xs text-sand-400">© 2026 Virsa · Community-Centric Intelligent Tourism Ecosystem</p>
      </div>

      <div className="flex items-center justify-center bg-sand-100 px-6 py-12">
        <div className="w-full max-w-md">
          <div className="mb-6 lg:hidden">
            <Link to="/" className="flex items-center gap-2.5 text-ink">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal text-white"><Sparkles className="h-5 w-5" /></span>
              <span className="font-display text-xl font-bold">Virsa</span>
            </Link>
          </div>

          <h2 className="font-display text-3xl font-bold text-ink">Sign in</h2>
          <p className="mt-1 text-sm text-ink-muted">Pick a demo account or log in with your own.</p>

          {err && <div className="mt-4"><ErrorNote text={err} /></div>}

          <form
            className="card mt-6 space-y-3 p-6"
            onSubmit={(e) => {
              e.preventDefault();
              doLogin(email, password);
            }}
          >
            <div>
              <label className="label">Email</label>
              <input className="input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
            </div>
            <div>
              <label className="label">Password</label>
              <input className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
            </div>
            <Button type="submit" disabled={busy} size="lg" className="w-full">
              {busy ? "Signing in…" : "Sign in"} <ArrowRight className="h-4 w-4" />
            </Button>
          </form>

          <div className="mt-6">
            <p className="text-xs font-bold uppercase tracking-wider text-ink-faint">Demo accounts (<b className="text-ink">demo1234</b>)</p>
            <div className="mt-2 grid gap-2 sm:grid-cols-2">
              {DEMO_ACCOUNTS.map((a) => (
                <button
                  key={a.email}
                  onClick={() => doLogin(a.email, "demo1234")}
                  disabled={busy}
                  className="card group !p-3.5 text-left transition hover:border-teal/40 hover:shadow-card"
                >
                  <p className="text-sm font-semibold text-ink group-hover:text-teal-deep">{a.label}</p>
                  <p className="text-[11px] text-ink-faint">{a.email}</p>
                  <p className="mt-1 text-[11px] text-teal">{a.info}</p>
                </button>
              ))}
            </div>
          </div>

          <p className="mt-6 text-center text-sm text-ink-muted">
            New here? <Link to="/register" className="font-semibold text-teal-deep hover:text-saffron-deep">Create an account</Link>
          </p>
        </div>
      </div>
    </div>
  );
}