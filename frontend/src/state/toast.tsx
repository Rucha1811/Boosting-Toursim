import { createContext, useContext, useState, useCallback, ReactNode } from "react";
import { CheckCircle2, AlertTriangle, Info } from "lucide-react";

interface Toast {
  id: number;
  kind: "success" | "error" | "info";
  text: string;
}

const ToastCtx = createContext<{ toast: (text: string, kind?: Toast["kind"]) => void }>({ toast: () => {} });

export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<Toast[]>([]);
  const toast = useCallback((text: string, kind: Toast["kind"] = "success") => {
    const id = Date.now() + Math.random();
    setItems((p) => [...p, { id, kind, text }]);
    setTimeout(() => setItems((p) => p.filter((t) => t.id !== id)), 3800);
  }, []);
  return (
    <ToastCtx.Provider value={{ toast }}>
      {children}
      <div className="fixed bottom-5 right-5 z-[3000] space-y-2 w-80 max-w-[90vw]">
        {items.map((t) => (
          <div
            key={t.id}
            className="report-enter flex items-start gap-3 rounded-2xl bg-ink px-4 py-3 text-white shadow-lift"
          >
            {t.kind === "success" && <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />}
            {t.kind === "error" && <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />}
            {t.kind === "info" && <Info className="w-5 h-5 text-sky-300 shrink-0 mt-0.5" />}
            <p className="text-sm leading-snug">{t.text}</p>
          </div>
        ))}
      </div>
    </ToastCtx.Provider>
  );
}

export const useToast = () => useContext(ToastCtx);