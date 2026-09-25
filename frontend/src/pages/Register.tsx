import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Sparkles, ArrowRight } from "lucide-react";
import { useAuth, routeFor } from "../state/auth";
import { useToast } from "../state/toast";
import { Button, ErrorNote } from "../components/ui";

export default function RegisterPage() {
  const { register } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", phone: "", password: "", role: "tourist" });
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  const submit = async () => {
    if (!form.name || !form.email || form.password.length < 6) {
      setErr("Name, email and a password of 6+ characters are required.");
      return;
    }
    setBusy(true);
    setErr("");
    try {
      const u = await register(form);
      toast(`Welcome to Virsa, ${u.name.split(" ")[0]}!`);
      navigate(routeFor(u.role) || "/");
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Registration failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen bg-sand-100 px-6 py-10">
      <div className="mx-auto max-w-md">
        <Link to="/" className="mb-8 flex items-center gap-2.5">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal text-white"><Sparkles className="h-5 w-5" /></span>
          <span className="font-display text-xl font-bold text-ink">Virsa</span>
        </Link>
        <h2 className="font-display text-3xl font-bold text-ink">Join the ecosystem</h2>
        <p className="mt-1 text-sm text-ink-muted">Create an account — it's one login for every role.</p>

        {err && <div className="mt-4"><ErrorNote text={err} /></div>}

        <form
          className="card mt-6 space-y-3 p-6"
          onSubmit={(e) => {
            e.preventDefault();
            submit();
          }}
        >
          <div>
            <label className="label">Full name</label>
            <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Ananya Desai" />
          </div>
          <div>
            <label className="label">Email</label>
            <input className="input" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="you@example.com" />
          </div>
          <div>
            <label className="label">Phone</label>
            <input className="input" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} placeholder="98xxxxxx00" />
          </div>
          <div>
            <label className="label">Password</label>
            <input className="input" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="6+ characters" />
          </div>
          <div>
            <label className="label">I am a…</label>
            <select className="input" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
              <option value="tourist">Tourist</option>
              <option value="resident">Resident</option>
              <option value="artisan">Artisan / Local business</option>
            </select>
          </div>
          <Button type="submit" disabled={busy} size="lg" className="w-full">
            {busy ? "Creating…" : "Create account"} <ArrowRight className="h-4 w-4" />
          </Button>
        </form>
        <p className="mt-6 text-center text-sm text-ink-muted">
          Already registered? <Link to="/login" className="font-semibold text-teal-deep hover:text-saffron-deep">Sign in</Link>
        </p>
      </div>
    </div>
  );
}