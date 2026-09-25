import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Sparkles, Send, Bot, User, ArrowUpRight } from "lucide-react";
import { clsx } from "clsx";
import { endpoints } from "../lib/api";
import { getDestCopy } from "../lib/destCopy";
import { useDestination } from "../state/destination";
import type { AssistantAnswer } from "../lib/types";
import { SectionTitle } from "../components/ui";
import { ListenButton } from "../components/a11y";
import { useLanguage } from "../state/language";

interface Msg {
  role: "user" | "bot";
  text: string;
  refs?: AssistantAnswer["references"];
  intents?: string[];
  error?: boolean;
}

export default function AssistantPage() {
  const { currentId } = useDestination();
  const { t } = useLanguage();
  const dc = getDestCopy(currentId);
  const suggestions = dc.assistantSuggestions;
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!msgs.length) {
      setMsgs([
        {
          role: "bot",
          text: dc.assistantIntro,
        },
      ]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [msgs.length]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs, busy]);

  const ask = async (question: string) => {
    const q = question.trim();
    if (!q || busy) return;
    setMsgs((p) => [...p, { role: "user", text: q }]);
    setInput("");
    setBusy(true);
    try {
      const a = await endpoints.assistant(q);
      setMsgs((p) => [...p, { role: "bot", text: a.answer, refs: a.references, intents: a.intents }]);
    } catch (e) {
      setMsgs((p) => [...p, { role: "bot", text: e instanceof Error ? e.message : "Something went wrong.", error: true }]);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="animate-fade-up mx-auto max-w-4xl px-6 py-10">
      <SectionTitle
        kicker={t("guide.kicker")}
        title={t("guide.title")}
        sub={t("guide.sub")}
      />

      <div className="card flex min-h-[520px] flex-col overflow-hidden">
        <div className="flex items-center gap-3 border-b border-ink/5 bg-gradient-to-r from-teal-deep to-teal p-4 text-white">
          <span className="flex h-10 w-10 items-center justify-center rounded-full bg-saffron text-teal-dark">
            <Bot className="h-5 w-5" />
          </span>
          <div>
            <p className="font-display text-base font-semibold">Virsa Guide</p>
            <p className="text-[11px] text-sand-200">Online · connected to the city's live data</p>
          </div>
        </div>

        <div className="flex-1 space-y-4 overflow-y-auto bg-sand-50 p-4 sm:p-6" style={{ maxHeight: "56vh" }}>
          {msgs.map((m, i) => (
            <div key={i} className={clsx("flex gap-3", m.role === "user" ? "justify-end" : "justify-start")}>
              {m.role === "bot" && (
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-teal/10 text-teal-deep">
                  <Bot className="h-4 w-4" />
                </span>
              )}
              <div className={clsx("max-w-[80%] rounded-3xl px-4 py-3 text-sm leading-relaxed", m.role === "user" ? "rounded-br-sm bg-teal text-white" : "rounded-bl-sm bg-white text-ink-soft shadow-card", m.error && "bg-blush-light text-blush")}>
                <p>{m.text}</p>
                {m.role === "bot" && (
                  <div className="mt-2">
                    <ListenButton
                      text={m.text}
                      label={t("tts.readAnswer")}
                      variant="outline"
                      iconOnly
                      className="!px-2 !py-1"
                    />
                  </div>
                )}
                {m.refs && m.refs.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {m.refs.map((r, j) => {
                      const to = r.type === "place" ? `/places/${r.place_id}` : r.type === "artisan" ? `/artisans/${r.business_id}` : r.type === "experience" ? `/experiences/${r.experience_id}` : null;
                      return to ? (
                        <Link key={j} to={to} className="inline-flex items-center gap-1 rounded-full bg-teal-soft px-3 py-1 text-[11px] font-semibold text-teal-deep hover:bg-teal/20">
                          {r.name} <ArrowUpRight className="h-3 w-3" />
                        </Link>
                      ) : (
                        <span key={j} className="rounded-full bg-teal-soft px-3 py-1 text-[11px] font-semibold text-teal-deep">{r.name}</span>
                      );
                    })}
                  </div>
                )}
              </div>
              {m.role === "user" && (
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-ink text-white">
                  <User className="h-4 w-4" />
                </span>
              )}
            </div>
          ))}
          {busy && (
            <div className="flex items-center gap-2 text-xs text-ink-muted">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-teal/10 text-teal-deep">
                <Bot className="h-4 w-4 animate-pulse" />
              </span>
              Virsa Guide is thinking…
            </div>
          )}
          <div ref={endRef} />
        </div>

        {!busy && msgs.length === 1 && (
          <div className="flex flex-wrap gap-2 px-4 pb-2 sm:px-6">
            {suggestions.map((s) => (
              <button key={s} onClick={() => ask(s)} className="rounded-full border border-teal/25 bg-white px-3 py-1.5 text-xs font-medium text-teal-deep transition hover:bg-teal hover:text-white">
                {s}
              </button>
            ))}
          </div>
        )}

        <form
          onSubmit={(e) => {
            e.preventDefault();
            ask(input);
          }}
          className="flex items-center gap-2 border-t border-ink/5 bg-white p-3"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={t("guide.placeholder")}
            className="input !flex-1"
          />
          <button type="submit" disabled={busy} className="btn btn-primary btn-lg !rounded-2xl !px-4">
            <Send className="h-5 w-5" />
          </button>
        </form>
      </div>

      <p className="mt-4 flex items-center gap-1.5 text-xs text-ink-muted">
        <Sparkles className="h-3.5 w-3.5 text-saffron-deep" />
        Virsa Guide answers only from the destination's real catalogue and live analytics — events, places, artisans, hotels,
        closures and crowd forecasts.
      </p>
    </div>
  );
}