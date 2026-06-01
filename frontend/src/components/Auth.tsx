import { useState } from "react";
import { supabase } from "../lib/supabase";
import { Logo } from "./brand/Logo";

export function Auth() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [error, setError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const { error } =
      mode === "signin"
        ? await supabase.auth.signInWithPassword({ email, password })
        : await supabase.auth.signUp({ email, password });
    if (error) setError(error.message);
    else if (mode === "signup") setSent(true);
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4">
      <div className="mb-8 flex flex-col items-center text-center">
        <Logo size="lg" />
        <p className="mt-6 font-heading text-lg font-semibold uppercase tracking-[0.25em] text-brand-stone">
          Roll your legend. Build your story.
        </p>
        <p className="mt-1 text-sm text-brand-stone/50">
          An AI-powered D&amp;D character generator.
        </p>
      </div>

      <div className="w-full max-w-sm rounded-2xl border border-ink-600/70 bg-ink-800/70 p-8 shadow-card">
        {sent ? (
          <p className="text-center text-sm text-brand-stone/80">
            Check your email to confirm your account, then sign in.
          </p>
        ) : (
          <form onSubmit={submit} className="space-y-3">
            <input
              className="w-full rounded-lg border border-ink-600 bg-ink-900 px-3 py-2 text-sm outline-none focus:border-brand-gold focus:ring-1 focus:ring-brand-gold/60"
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <input
              className="w-full rounded-lg border border-ink-600 bg-ink-900 px-3 py-2 text-sm outline-none focus:border-brand-gold focus:ring-1 focus:ring-brand-gold/60"
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            {error && <p className="text-sm text-brand-red">{error}</p>}
            <button className="w-full rounded-lg bg-brand-red px-3 py-2 font-heading font-semibold text-white shadow-ember transition-colors hover:bg-[#d12222]">
              {mode === "signin" ? "Sign in" : "Create account"}
            </button>
            <button
              type="button"
              className="w-full font-heading text-sm text-brand-stone/50 hover:text-brand-gold"
              onClick={() => setMode(mode === "signin" ? "signup" : "signin")}
            >
              {mode === "signin"
                ? "New here? Create an account"
                : "Have an account? Sign in"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
