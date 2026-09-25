import { useCallback, useEffect, useRef, useState } from "react";
import { endpoints } from "../lib/api";
import type { DynamicInfo } from "../lib/types";

export function usePoll<T>(fetcher: () => Promise<T>, intervalMs = 20000, deps: unknown[] = []) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stamp, setStamp] = useState(0);
  const depKey = JSON.stringify(deps);

  const refresh = useCallback(() => setStamp((s) => s + 1), []);

  useEffect(() => {
    let alive = true;
    let timer: number;
    // Drop the previous destination's payload immediately so the UI never
    // renders one city's cards under another city's heading.
    setData(null);
    setError(null);
    setLoading(true);
    const run = async () => {
      try {
        const d = await fetcher();
        if (alive) {
          setData(d);
          setError(null);
        }
      } catch (e) {
        if (alive) setError(e instanceof Error ? e.message : "Failed to load");
      } finally {
        if (alive) setLoading(false);
      }
    };
    run();
    if (intervalMs > 0) timer = window.setTimeout(function tick() {
      run();
      timer = window.setTimeout(tick, intervalMs);
    }, intervalMs);
    return () => {
      alive = false;
      if (timer) clearTimeout(timer);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stamp, intervalMs, depKey]);

  return { data, loading, error, refresh };
}

export function useDynamicInfo(intervalMs = 20000, deps: unknown[] = []) {
  const res = usePoll<DynamicInfo>(() => endpoints.mapInfo(), intervalMs, deps);
  return res;
}