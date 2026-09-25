import { useEffect } from "react";
import type { ImgHTMLAttributes } from "react";
import { useState } from "react";

export default function Img({
  src,
  alt,
  className,
  ...rest
}: ImgHTMLAttributes<HTMLImageElement> & { className?: string }) {
  const [failed, setFailed] = useState(false);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    setFailed(false);
    setLoaded(false);
  }, [src]);

  return (
    <div className={`relative overflow-hidden bg-gradient-to-br from-sand-200 via-saffron-light to-teal-soft ${className}`}>
      {!failed && src ? (
        <img
          src={src}
          alt={alt || ""}
          loading="lazy"
          onError={() => setFailed(true)}
          onLoad={() => setLoaded(true)}
          className={`h-full w-full object-cover transition-opacity duration-700 ${loaded ? "opacity-100" : "opacity-0"}`}
          {...rest}
        />
      ) : (
        <div className="flex h-full w-full flex-col items-center justify-center gap-2 p-6 text-center">
          <svg viewBox="0 0 64 64" className="w-16 opacity-70" aria-hidden>
            <circle cx="32" cy="28" r="9" fill="none" stroke="#c5a878" strokeWidth="3" />
            <path
              d="M10 54c4-10 12-15 22-15s18 5 22 15"
              fill="none"
              stroke="#c5a878"
              strokeWidth="3"
              strokeLinecap="round"
            />
            <path d="M32 19l3 7 7 1-5 4 1 7-6-3-6 3 1-7-5-4 7-1z" fill="#e8a710" opacity="0.9" />
          </svg>
          <span className="font-display text-sm text-ink-muted">{alt || "Heritage scene"}</span>
        </div>
      )}
    </div>
  );
}