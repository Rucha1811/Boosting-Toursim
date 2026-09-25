import { useCallback, useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { Languages, Volume2, Square } from "lucide-react";
import { clsx } from "clsx";
import { useLanguage } from "../state/language";

/** EN | हिन्दी pill. Switches the whole app chrome + TTS voice. */
export function LangToggle({ className }: { className?: string }) {
  const { lang, setLang } = useLanguage();
  return (
    <div
      role="group"
      aria-label="Language / भाषा"
      className={clsx(
        "flex items-center overflow-hidden rounded-full border border-ink/15 bg-white shadow-card",
        className,
      )}
    >
      <button
        type="button"
        onClick={() => setLang("en")}
        aria-pressed={lang === "en"}
        className={clsx(
          "px-2.5 py-1.5 text-[11px] font-bold transition",
          lang === "en" ? "bg-teal text-white" : "text-ink-soft hover:bg-ink/5",
        )}
      >
        EN
      </button>
      <span className="h-4 w-px bg-ink/10" />
      <button
        type="button"
        onClick={() => setLang("hi")}
        aria-pressed={lang === "hi"}
        className={clsx(
          "px-2.5 py-1.5 text-[11px] font-bold transition",
          lang === "hi" ? "bg-teal text-white" : "text-ink-soft hover:bg-ink/5",
        )}
      >
        हिन्दी
      </button>
    </div>
  );
}

/** Mobile-friendly icon-only language toggle (uses a Languages glyph). */
export function LangToggleIcon({ className }: { className?: string }) {
  const { lang, toggle } = useLanguage();
  return (
    <button
      type="button"
      onClick={toggle}
      title={lang === "en" ? "Switch to हिन्दी" : "Switch to English"}
      aria-label={lang === "en" ? "Switch to हिन्दी" : "Switch to English"}
      className={clsx(
        "flex items-center gap-1 rounded-full border border-ink/15 bg-white px-2.5 py-1.5 text-[11px] font-bold text-ink shadow-card transition hover:border-teal/40",
        className,
      )}
    >
      <Languages className="h-4 w-4 text-teal" />
      <span className="hidden sm:inline">{lang === "en" ? "हिन्दी" : "EN"}</span>
    </button>
  );
}

/**
 * Read-aloud button for the visually / textually less comfortable.
 * Speaks the given text in the currently selected language (hi-IN / en-IN).
 */
export function ListenButton({
  text,
  label,
  className,
  variant = "saffron",
  iconOnly = false,
}: {
  text: string | (() => string);
  label?: string;
  className?: string;
  variant?: "saffron" | "outline" | "teal";
  iconOnly?: boolean;
}) {
  const { speak, stop, speaking, t } = useLanguage();
  const onClick = useCallback(() => {
    if (speaking) {
      stop();
      return;
    }
    speak(typeof text === "function" ? text() : text);
  }, [speaking, speak, stop, text]);

  const resolved = label ?? (speaking ? t("actions.stop") : t("actions.listen"));
  const base = clsx(
    "inline-flex items-center gap-1.5 rounded-full font-semibold transition",
    variant === "saffron" && "btn btn-saffron btn-sm",
    variant === "teal" && "btn btn-primary btn-sm",
    variant === "outline" && "btn btn-outline btn-sm",
    speaking && "ring-2 ring-teal/40",
    className,
  );
  const Icon = speaking ? Square : Volume2;

  if (iconOnly) {
    return (
      <button type="button" onClick={onClick} title={resolved} aria-label={resolved} className={base}>
        <Icon className="h-4 w-4" />
      </button>
    );
  }
  return (
    <button type="button" onClick={onClick} className={base}>
      <Icon className="h-4 w-4" />
      {resolved}
    </button>
  );
}

/**
 * "Read this page" control. The text is captured at click time so it always
 * reflects the current route, language and freshly loaded content rather than
 * a stale snapshot.
 */
export function ReadPageButton({ className }: { className?: string }) {
  const { lang, speak, stop, speaking, t } = useLanguage();
  const [hasText, setHasText] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const id = window.setTimeout(() => {
      const el = document.querySelector("main") as HTMLElement | null;
      setHasText(Boolean(el && (el.innerText || "").trim()));
    }, 350);
    return () => window.clearTimeout(id);
  }, [location.pathname, lang]);

  if (!hasText) return null;
  const label = speaking ? t("actions.stop") : t("actions.listen");
  return (
    <ListenButton
      text={() => {
        const el = document.querySelector("main") as HTMLElement | null;
        return el ? el.innerText : "";
      }}
      label={label}
      className={className}
      variant="outline"
      iconOnly
    />
  );
}
