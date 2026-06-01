import { useEffect, useState } from "react";
import { Routes, Route, Navigate, Link } from "react-router-dom";
import type { Session } from "@supabase/supabase-js";
import { supabase } from "./lib/supabase";
import { Auth } from "./components/Auth";
import { CharacterList } from "./components/CharacterList";
import { CharacterEditor } from "./components/CharacterEditor";
import { SharePage } from "./pages/SharePage";

export default function App() {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session);
      setLoading(false);
    });
    const { data: sub } = supabase.auth.onAuthStateChange((_e, s) =>
      setSession(s)
    );
    return () => sub.subscription.unsubscribe();
  }, []);

  if (loading) return <div className="p-8">Loading…</div>;

  return (
    <Routes>
      {/* Public, read-only share view — available without auth. */}
      <Route path="/share/:versionId" element={<SharePage />} />
      <Route
        path="*"
        element={session ? <AppShell /> : <Auth />}
      />
    </Routes>
  );
}

function AppShell() {
  return (
    <div className="min-h-screen">
      <header className="flex items-center justify-between border-b border-slate-800 px-6 py-4">
        <Link to="/" className="text-xl font-bold text-arcane">
          ⚔ Arcane Architect
        </Link>
        <button
          className="text-sm text-slate-400 hover:text-slate-100"
          onClick={() => supabase.auth.signOut()}
        >
          Sign out
        </button>
      </header>
      <main className="mx-auto max-w-5xl p-6">
        <Routes>
          <Route path="/" element={<CharacterList />} />
          <Route path="/characters/:id" element={<CharacterEditor />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <footer className="px-6 py-8 text-center text-xs text-slate-500">
        Grounded in the Systems Reference Document 5.1, © Wizards of the Coast,
        licensed under CC-BY-4.0.
      </footer>
    </div>
  );
}
