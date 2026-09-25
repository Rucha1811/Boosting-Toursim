import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

export type Lang = "en" | "hi";
export type Dict = Record<string, string>;

/**
 * Bilingual string catalogs (English ↔ हिंदी). Every key maps to a single
 * translation that fits the same visual slot, so switching languages is a
 * pure dictionary swap — no layout breakage, no missing-message state.
 *
 * The catalogs intentionally cover the shared chrome (navigation, hero,
 * section titles, CTAs, account + authority labels, footer) plus the most
 * common destination copy so the whole app reads naturally in either language.
 */
export const STRINGS: Record<Lang, Dict> = {
  en: {
    "brand.tagline": "Cultural Tourism",
    "nav.map": "Explore Map",
    "nav.artisans": "Meet the Makers",
    "nav.experiences": "Experiences",
    "nav.festivals": "Festivals",
    "nav.stays": "Stays",
    "nav.guide": "Virsa Guide",
    "nav.authority": "Authority",
    "nav.business": "Business",
    "actions.signin": "Sign in",
    "actions.listen": "Listen",
    "actions.stop": "Stop",
    "actions.lang": "हिन्दी",
    "actions.langOff": "English",
    "switcher.label": "Destination",
    "switcher.hint": "Switch destination",
    "account.my": "My reports",
    "account.signout": "Sign out",
    "hero.kicker": "The people behind the heritage",
    "hero.title": "Where every place has a heartbeat — and a voice.",
    "hero.sub":
      "Discover the palaces, artisans and flavours of {city} through a living map — guided by crowds, festivals and the people who call this place home.",
    "hero.cta.explore": "Explore places",
    "hero.cta.listen": "Listen to the story",
    "hero.cta.speak": "Speak the story",
    "section.places": "Places",
    "section.artisans": "Artisans & makers",
    "section.experiences": "Experiences",
    "section.festivals": "Festivals",
    "section.stays": "Stays",
    "section.live": "Live now",
    "section.upcoming": "Coming up",
    "section.guide": "Ask the Virsa guide",
    "section.sub.places": "Heritage hotspots with live crowd intel",
    "section.sub.artisans": "The hands behind Kutch, Patola and more",
    "section.sub.experiences": "Hands-on ways to feel the culture",
    "section.sub.festivals": "When the destination truly comes alive",
    "section.sub.stays": "Sleep inside heritage",
    "marker.live": "LIVE",
    "footer.about": "Virsa pairs live civic infrastructure with heritage storytelling so every visitor — and every authority — sees the same picture.",
    "footer.links": "Explore",
    "footer.explore": "Explore",
    "footer.community": "Community",
    "footer.report": "Report an issue",
    "footer.track": "Track reports",
    "footer.askGuide": "Ask Virsa Guide",
    "footer.authority": "For authorities",
    "footer.business": "For the trade",
    "footer.make": "Made with ♥ for the people of Gujarat & Rajasthan",
    "auth.tos": "By continuing you agree to the Terms & Privacy policy.",
    "report.title": "Report an issue",
    "map.live": "LIVE · streaming footfall",
    "guide.banner": "Ask me anything about the city — I answer with live data.",
    "guide.placeholder": "e.g. Which heritage walk is closest right now?",
    "guide.send": "Ask",
    "tts.desc": "Hear it — an audio companion for those who prefer to listen.",
    "tts.readAnswer": "Read answer aloud",
    "guide.title": "Ask the Virsa Guide",
    "guide.kicker": "AI cultural guide",
    "guide.sub": "Grounded in live data — real events, real artisans, real crowd levels. No made-up answers.",
    "home.happening": "Happening in {city} now",
    "home.openMap": "Open the live map",
    "home.crowd.very": "Very busy",
    "home.crowd.heavy": "Heavy",
    "home.crowd.moderate": "Moderate",
    "home.crowd.quiet": "Quiet",
    "home.stats.legs": "heritage legs",
    "home.stats.languages": "languages",
    "home.stats.festivals": "festivals per year",
    "home.explore.kicker": "Curated by the community",
    "home.explore.title": "Ways to experience {city}",
    "home.explore.sub": "Heritage walks, living crafts, flavours and festivals — chosen with the city, not over it.",
    "home.live.kicker": "Live right now",
    "home.live.title": "Where the city is moving",
    "home.live.sub": "Live crowd levels refresh every minute. Click through to a full heritage page.",
    "home.live.openMap": "Open map",
    "home.live.visitors": "visitors near here now",
    "home.makers.kicker": "Direct from the community",
    "home.makers.title": "Makers & local spots",
    "home.makers.sub": "Every purchase keeps a craft alive in the family heir-loom of this city.",
    "home.makers.all": "All makers",
    "home.makers.verified": "Community-verified",
    "home.exp.kicker": "Hands-on culture",
    "home.exp.title": "Book a local experience",
    "home.exp.all": "All experiences",
    "home.festival.live": "live now",
    "home.festival.starts": "starts {date}",
    "home.festival.enter": "Enter festival mode",
    "dash.kicker": "For operators",
    "dash.title": "Authority & business dashboards",
    "dash.titleSigned": "Your dashboard",
    "dash.sub": "Live crowd command centre for tourism authorities, and a workspace for artisans and local businesses. Sign in with a demo role to open it.",
    "dash.signin": "Sign in to open",
    "dash.open": "Open dashboard",
    "dash.authoritySub": "Live map, crowd analytics, forecasts, alerts, road closures and community reports.",
    "dash.businessSub": "Keep your public profile, products and workshops up to date across the site.",
  },
  hi: {
    "brand.tagline": "सांस्कृतिक पर्यटन",
    "nav.map": "नक्शा खोजें",
    "nav.artisans": "कारीगरों से मिलें",
    "nav.experiences": "अनुभव",
    "nav.festivals": "त्योहार",
    "nav.stays": "ठहराव",
    "nav.guide": "विरसा गाइड",
    "nav.authority": "प्रशासन",
    "nav.business": "व्यापार",
    "actions.signin": "साइन इन",
    "actions.listen": "सुनें",
    "actions.stop": "रोकें",
    "actions.lang": "English",
    "actions.langOff": "हिन्दी",
    "switcher.label": "गंतव्य",
    "switcher.hint": "गंतव्य बदलें",
    "account.my": "मेरी रिपोर्टें",
    "account.signout": "साइन आउट",
    "hero.kicker": "विरासत के पीछे के लोग",
    "hero.title": "हर जगह की एक धड़कन — और एक आवाज़।",
    "hero.sub":
      "{city} के महलों, कारीगरों और स्वादों को एक जीवंत नक्शे के माध्यम से देखें — भीड़, त्योहार और उन लोगों के मार्गदर्शन में, जो इस जगह को घर कहते हैं।",
    "hero.cta.explore": "जगहें खोजें",
    "hero.cta.listen": "कहानी सुनें",
    "hero.cta.speak": "कहानी बोलें",
    "section.places": "जगहें",
    "section.artisans": "कारीगर और शिल्पकार",
    "section.experiences": "अनुभव",
    "section.festivals": "त्योहार",
    "section.stays": "ठहराव",
    "section.live": "अभी लाइव",
    "section.upcoming": "आगामी",
    "section.guide": "विरसा गाइड से पूछें",
    "section.sub.places": "लाइव भीड़ जानकारी के साथ धरोहर स्थल",
    "section.sub.artisans": "कच्छ, पाटोला और बहुत कुछ के पीछे के हाथ",
    "section.sub.experiences": "संस्कृति को महसूस करने के अनुभव",
    "section.sub.festivals": "जब गंतव्य सचमुच जीवंत हो उठता है",
    "section.sub.stays": "धरोहर के भीतर रात बिताएँ",
    "marker.live": "लाइव",
    "footer.about": "विरसा लाइव नागरिक सुविधाओं को धरोहर कहानियों से जोड़ता है, ताकि हर पर्यटक और हर प्रशासक एक ही तस्वीर देखें।",
    "footer.links": "खोजें",
    "footer.explore": "खोजें",
    "footer.community": "समुदाय",
    "footer.report": "समस्या की सूचना दें",
    "footer.track": "रिपोर्ट देखें",
    "footer.askGuide": "विरसा गाइड से पूछें",
    "footer.authority": "प्रशासन हेतु",
    "footer.business": "व्यापार हेतु",
    "footer.make": "गुजरात और राजस्थान के लोगों के लिए ♥ से बना",
    "auth.tos": "जारी रखकर आप सेवा शर्तों से सहमत हैं।",
    "report.title": "समस्या की रिपोर्ट करें",
    "map.live": "लाइव · चलती भीड़",
    "guide.banner": "शहर के बारे में कुछ भी पूछें — मैं लाइव डेटा से जवाब देता हूँ।",
    "guide.placeholder": "जैसे — अभी कौन सी धरोहर सैर सबसे नज़दीक है?",
    "guide.send": "पूछें",
    "tts.desc": "सुनें — उन लोगों के लिए जो पढ़ना नहीं चाहते या नहीं जानते।",
    "tts.readAnswer": "उत्तर सुनाएँ",
    "guide.title": "विरसा गाइड से पूछें",
    "guide.kicker": "एआई सांस्कृतिक गाइड",
    "guide.sub": "लाइव डेटा पर आधारित — असली कार्यक्रम, असली कारीगर, असली भीड़। कोई बनावटी जवाब नहीं।",
    "home.happening": "{city} में अभी चल रहा है",
    "home.openMap": "लाइव नक्शा खोलें",
    "home.crowd.very": "बहुत व्यस्त",
    "home.crowd.heavy": "भारी भीड़",
    "home.crowd.moderate": "सामान्य",
    "home.crowd.quiet": "शांत",
    "home.stats.legs": "धरोहर यात्राएँ",
    "home.stats.languages": "भाषाएँ",
    "home.stats.festivals": "प्रति वर्ष त्योहार",
    "home.explore.kicker": "समुदाय द्वारा चुना गया",
    "home.explore.title": "{city} को कैसे देखें",
    "home.explore.sub": "धरोहर सैर, जीवंत शिल्प, स्वाद और त्योहार — शहर के साथ, शहर पर नहीं।",
    "home.live.kicker": "अभी लाइव",
    "home.live.title": "शहर कहाँ चल रहा है",
    "home.live.sub": "लाइव भीड़ हर मिनट अपडेट होती है। पूरी जानकारी के लिए क्लिक करें।",
    "home.live.openMap": "नक्शा खोलें",
    "home.live.visitors": "यहाँ अभी पर्यटक",
    "home.makers.kicker": "सीधे समुदाय से",
    "home.makers.title": "कारीगर और स्थानीय दुकान",
    "home.makers.sub": "हर खरीद इस शहर की पारिवारिक विरासत में एक शिल्प को जीवित रखती है।",
    "home.makers.all": "सभी कारीगर",
    "home.makers.verified": "समुदाय-सत्यापित",
    "home.exp.kicker": "हाथों से संस्कृति",
    "home.exp.title": "स्थानीय अनुभव बुक करें",
    "home.exp.all": "सभी अनुभव",
    "home.festival.live": "अभी चल रहा है",
    "home.festival.starts": "शुरू {date}",
    "home.festival.enter": "फेस्टिवल मोड में जाएँ",
    "dash.kicker": "संचालकों के लिए",
    "dash.title": "प्रशासन और व्यवसाय डैशबोर्ड",
    "dash.titleSigned": "आपका डैशबोर्ड",
    "dash.sub": "पर्यटन प्रशासन के लिए लाइव भीड़ कमांड सेंटर, और कारीगरों व स्थानीय व्यवसायों के लिए वर्कस्पेस। खोलने के लिए डेमो भूमिका से साइन इन करें।",
    "dash.signin": "खोलने के लिए साइन इन",
    "dash.open": "डैशबोर्ड खोलें",
    "dash.authoritySub": "लाइव नक्शा, भीड़ विश्लेषण, पूर्वानुमान, अलर्ट, सड़क बंदी और सामुदायिक रिपोर्ट।",
    "dash.businessSub": "अपनी सार्वजनिक प्रोफ़ाइल, उत्पाद और कार्यशालाएँ पूरी साइट पर अपडेट रखें।",
  },
};

const VOICE_PREF: Record<Lang, string[]> = {
  hi: ["hi-in", "hi-bom", "hi", "mr-in", "mr", "en-in", "en"],
  en: ["en-in", "en-gb", "en-us", "en-au", "en"],
};

function normLocale(tag: string) {
  return (tag || "").toLowerCase().replace(/_/g, "-");
}

/** Best available voice for a language, preferring regional and local variants. */
function getVoice(lang: Lang): SpeechSynthesisVoice | null {
  if (typeof window === "undefined" || !("speechSynthesis" in window)) return null;
  const voices = window.speechSynthesis.getVoices();
  if (!voices.length) return null;
  const pref = VOICE_PREF[lang];
  for (const tag of pref) {
    const exact = voices.find((v) => normLocale(v.lang) === tag);
    if (exact) return exact;
  }
  for (const tag of pref) {
    const partial = voices.find((v) => normLocale(v.lang).startsWith(tag.split("-")[0]));
    if (partial) return partial;
  }
  return voices.find((v) => v.default) ?? voices[0] ?? null;
}

/** True when the text actually contains Devanagari, so we can pick a matching voice. */
function isHindiText(text: string) {
  return /[\u0900-\u097F]/.test(text);
}

/** City names written in Latin inside Hindi prose; a Hindi voice mangles them. */
const CITY_DEVA: Record<string, string> = {
  vadodara: "वडोदरा",
  ahmedabad: "अहमदाबाद",
  kutch: "कच्छ",
  jaipur: "जयपुर",
  varanasi: "वाराणसी",
  rajasthan: "राजस्थान",
  gujarat: "गुजरात",
  "uttar pradesh": "उत्तर प्रदेश",
};

function transliterateCities(text: string) {
  return text.replace(
    /\b(Vadodara|Ahmedabad|Kutch|Jaipur|Varanasi|Rajasthan|Gujarat|Uttar Pradesh)\b/gi,
    (m) => CITY_DEVA[m.toLowerCase()] ?? m,
  );
}

/** Remove Markdown/markup and collapse whitespace so TTS reads clean prose. */
function speakableText(raw: string) {
  return raw
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/`([^`]*)`/g, "$1")
    .replace(/!\[[^\]]*\]\([^)]*\)/g, " ")
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/^#{1,6}\s*/gm, "")
    .replace(/(\*\*|__|\*|_)/g, "")
    .replace(/^\s*[-*+]\s+/gm, "")
    .replace(/[|]/g, ", ")
    .replace(/\s{2,}/g, " ")
    .trim();
}

/** Speech engines truncate very long input, so split on sentence boundaries. */
function chunkText(text: string, max = 220): string[] {
  if (text.length <= max) return [text];
  const parts = text.split(/(?<=[.!?।\n])\s+/);
  const out: string[] = [];
  let buf = "";
  for (const p of parts) {
    if ((buf + " " + p).trim().length > max && buf) {
      out.push(buf.trim());
      buf = p;
    } else {
      buf = `${buf} ${p}`.trim();
    }
  }
  if (buf.trim()) out.push(buf.trim());
  return out.length ? out : [text];
}

interface LanguageState {
  lang: Lang;
  langName: string;
  t: (key: string) => string;
  setLang: (l: Lang) => void;
  toggle: () => void;
  speak: (text: string) => void;
  speaking: boolean;
  stop: () => void;
}

const Ctx = createContext<LanguageState>({
  lang: "en",
  langName: "English",
  t: (k) => STRINGS.en[k] ?? k,
  setLang: () => {},
  toggle: () => {},
  speak: () => {},
  speaking: false,
  stop: () => {},
});

const STORE = "virsa_lang";

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(() =>
    typeof localStorage !== "undefined" && localStorage.getItem(STORE) === "hi" ? "hi" : "en",
  );
  const [speaking, setSpeaking] = useState(false);

  useEffect(() => {
    try {
      localStorage.setItem(STORE, lang);
    } catch {
      /* private mode */
    }
  }, [lang]);

  // eager-prime the voice list (Chrome loads voices lazily on some platforms)
  useEffect(() => {
    if (!("speechSynthesis" in window)) return;
    window.speechSynthesis.getVoices();
    const onv = () => {};
    window.speechSynthesis.onvoiceschanged = onv;
    return () => {
      window.speechSynthesis.onvoiceschanged = null;
    };
  }, []);

  const t = useCallback((k: string) => STRINGS[lang][k] ?? STRINGS.en[k] ?? k, [lang]);

  const stop = useCallback(() => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    setSpeaking(false);
  }, []);

  const speak = useCallback(
    (raw: string) => {
      if (typeof window === "undefined" || !("speechSynthesis" in window) || !raw) return;
      const text = transliterateCities(speakableText(raw));
      if (!text) return;
      window.speechSynthesis.cancel();

      const chunks = chunkText(text);
      // Each chunk picks its own voice: Devanagari chunks use a Hindi voice,
      // Latin chunks keep an English voice. This keeps mixed content readable
      // instead of forcing English prose through a Hindi voice.
      const hiVoice = getVoice("hi");
      const enVoice = getVoice("en");

      let finished = 0;
      let cancelled = false;
      const total = chunks.length;

      const finish = () => {
        if (cancelled) return;
        finished += 1;
        if (finished >= total) setSpeaking(false);
      };

      chunks.forEach((chunk, i) => {
        const u = new SpeechSynthesisUtterance(chunk);
        const wantsHindi = isHindiText(chunk);
        const voice = wantsHindi ? hiVoice : enVoice ?? hiVoice;
        if (voice) u.voice = voice;
        u.lang = voice?.lang || (wantsHindi ? "hi-IN" : "en-IN");
        u.rate = wantsHindi ? 0.92 : 0.97;
        u.pitch = 1;
        u.onend = finish;
        u.onerror = finish;
        window.speechSynthesis.speak(u);
      });

      if (total > 0) setSpeaking(true);
      // Guard against engines that never fire onend for the first chunk.
      window.setTimeout(() => setSpeaking(false), Math.max(12000, text.length * 95));
    },
    [lang],
  );

  const setLang = useCallback(
    (l: Lang) => {
      if (l === lang) return;
      stop();
      setLangState(l);
    },
    [lang, stop],
  );

  const toggle = useCallback(() => setLang(lang === "en" ? "hi" : "en"), [lang, setLang]);

  const value = useMemo<LanguageState>(
    () => ({
      lang,
      langName: lang === "en" ? "English" : "हिन्दी",
      t,
      setLang,
      toggle,
      speak,
      speaking,
      stop,
    }),
    [lang, t, setLang, speak, speaking, stop],
  );

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useLanguage() {
  return useContext(Ctx);
}
