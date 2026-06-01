import { useState } from "react";
import { supabase } from "../lib/supabase";

export function Auth() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [error, setError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const fn =
      mode === "signin"
        ? supabase.auth.signInWithPassword
        : supabase.auth.signUp;
    const { error } = await fn({ email, password });
    if (error) setError(error.message);
    else if (mode === "signup") setSent(true);
  }

  return (
    <div className="mx-auto mt-24 max-w-sm rounded-xl border border-slate-800 p-8">
      <h1 className="mb-6 text-center text-2xl font-bold text-arcane">
        ⚔ Arcane Architect
      </h1>
      {sent ? (
        <p className="text-center text-sm text-slate-300">
          Check your email to confirm your account.
        </p>
      ) : (
        <form onSubmit={submit} className="space-y-3">
          <input
            className="w-full rounded bg-slate-900 px-3 py-2"
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            className="w-full rounded bg-slate-900 px-3 py-2"
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          {error && <p className="text-sm text-red-400">{error}</p>}
          <button className="w-full rounded bg-arcane px-3 py-2 font-medium">
            {mode === "signin" ? "Sign in" : "Sign up"}
          </button>
          <button
            type="button"
            className="w-full text-sm text-slate-400"
            onClick={() => setMode(mode === "signin" ? "signup" : "signin")}
          >
            {mode === "signin"
              ? "Need an account? Sign up"
              : "Have an account? Sign in"}
          </button>
        </form>
      )}
    </div>
  );
}
