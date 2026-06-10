import { createContext, useCallback, useContext, useRef, useState } from "react";

type ToastKind = "success" | "error" | "info";

interface Toast {
  id: number;
  kind: ToastKind;
  message: string;
}

interface ToasterApi {
  toast: (kind: ToastKind, message: string) => void;
}

const ToasterContext = createContext<ToasterApi | null>(null);

const KIND_CLASS: Record<ToastKind, string> = {
  success: "border-brand-green/60 bg-brand-green/15 text-brand-green",
  error: "border-brand-red/60 bg-brand-red/15 text-brand-red",
  info: "border-brand-gold/60 bg-brand-gold/10 text-brand-gold",
};

export function ToasterProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const nextId = useRef(1);

  const toast = useCallback((kind: ToastKind, message: string) => {
    const id = nextId.current++;
    setToasts((cur) => [...cur, { id, kind, message }]);
    setTimeout(() => {
      setToasts((cur) => cur.filter((t) => t.id !== id));
    }, 3500);
  }, []);

  return (
    <ToasterContext.Provider value={{ toast }}>
      {children}
      <div className="pointer-events-none fixed inset-x-0 bottom-6 z-50 flex flex-col items-center gap-2 px-4">
        {toasts.map((t) => (
          <div
            key={t.id}
            role="status"
            className={`pointer-events-auto max-w-md rounded-lg border px-4 py-2 text-sm font-heading shadow-card backdrop-blur ${KIND_CLASS[t.kind]}`}
          >
            {t.message}
          </div>
        ))}
      </div>
    </ToasterContext.Provider>
  );
}

export function useToast(): ToasterApi {
  const ctx = useContext(ToasterContext);
  if (!ctx) throw new Error("useToast must be used inside <ToasterProvider>");
  return ctx;
}

// Helper for async actions: shows an error toast if the promise rejects, returns
// undefined in that case so callers can `if (result)` guard.
export async function runWithToast<T>(
  toast: ToasterApi,
  promise: Promise<T>,
  opts: { success?: string; failure: string },
): Promise<T | undefined> {
  try {
    const value = await promise;
    if (opts.success) toast.toast("success", opts.success);
    return value;
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    // Trim the leaky "${status}: ${detail}" shape from api.ts for user display.
    const cleaned = message.replace(/^\d{3}:\s*/, "");
    toast.toast("error", `${opts.failure}${cleaned ? ` — ${cleaned}` : ""}`);
    return undefined;
  }
}
