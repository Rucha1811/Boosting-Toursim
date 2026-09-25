import type { ReactNode, ButtonHTMLAttributes } from "react";
import { clsx } from "clsx";
import { X } from "lucide-react";

export function Button({
  className,
  variant = "primary",
  size = "md",
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "dark" | "outline" | "saffron" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
}) {
  const variants = {
    primary: "btn-primary",
    dark: "btn-dark",
    outline: "btn-outline",
    saffron: "btn-saffron",
    ghost: "text-ink-soft hover:bg-ink/5",
    danger: "bg-blush text-white hover:bg-red-700",
  };
  const sizes = { sm: "btn-sm", md: "btn-md", lg: "btn-lg" };
  return (
    <button className={clsx("btn", variants[variant], sizes[size], className)} {...rest} />
  );
}

export function Tile({ className, children }: { className?: string; children: ReactNode }) {
  return <div className={clsx("card p-5", className)}>{children}</div>;
}

export function SectionTitle({
  kicker,
  title,
  sub,
  right,
  className,
}: {
  kicker?: string;
  title: ReactNode;
  sub?: ReactNode;
  right?: ReactNode;
  className?: string;
}) {
  return (
    <div className={clsx("mb-6 flex flex-wrap items-end justify-between gap-4", className)}>
      <div>
        {kicker && (
          <p className="mb-1 text-xs font-bold uppercase tracking-[0.2em] text-saffron-deep">{kicker}</p>
        )}
        <h2 className="font-display text-2xl font-semibold text-ink sm:text-3xl">{title}</h2>
        {sub && <p className="mt-1 max-w-2xl text-sm text-ink-muted">{sub}</p>}
      </div>
      {right}
    </div>
  );
}

export function Modal({
  open,
  onClose,
  title,
  children,
  wide,
}: {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  wide?: boolean;
}) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-[2500] flex items-end justify-center sm:items-center">
      <div className="absolute inset-0 bg-ink/50 backdrop-blur-sm" onClick={onClose} />
      <div
        className={clsx(
          "relative z-10 max-h-[90vh] w-full overflow-y-auto rounded-t-3xl bg-sand-50 p-6 shadow-lift sm:rounded-3xl",
          wide ? "sm:max-w-3xl" : "sm:max-w-lg",
        )}
      >
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-display text-xl font-semibold text-ink">{title}</h3>
          <button onClick={onClose} className="rounded-full p-2 text-ink-muted hover:bg-ink/5">
            <X className="h-5 w-5" />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

export function Spinner({ className }: { className?: string }) {
  return (
    <div className={clsx("flex items-center justify-center py-16 text-ink-muted", className)}>
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-teal/25 border-t-teal" />
    </div>
  );
}

export function EmptyState({ icon, title, sub }: { icon: ReactNode; title: string; sub?: string }) {
  return (
    <div className="flex flex-col items-center gap-3 py-14 text-center">
      <div className="rounded-2xl bg-sand-100 p-4 text-ink-muted">{icon}</div>
      <p className="font-display text-lg text-ink">{title}</p>
      {sub && <p className="max-w-sm text-sm text-ink-muted">{sub}</p>}
    </div>
  );
}

export function ErrorNote({ text }: { text: string }) {
  return (
    <div className="rounded-xl bg-blush-light px-4 py-3 text-sm text-blush">{text}</div>
  );
}