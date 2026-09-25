import { createContext, useContext, useEffect, useMemo, useState, ReactNode } from "react";
import { endpoints, setCurrentDestinationId, getSavedDestinationId } from "../lib/api";
import type { Destination } from "../lib/types";

interface DestinationState {
  destinations: Destination[];
  current: Destination | null;
  currentId: number;
  loading: boolean;
  select: (id: number) => void;
}

const Ctx = createContext<DestinationState>({
  destinations: [],
  current: null,
  currentId: 1,
  loading: true,
  select: () => {},
});

export function DestinationProvider({ children }: { children: ReactNode }) {
  const [destinations, setDestinations] = useState<Destination[]>([]);
  const [currentId, setCurrentId] = useState<number>(() => getSavedDestinationId());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    endpoints
      .destinations()
      .then((ds) => {
        if (!alive) return;
        setDestinations(ds);
        const saved = getSavedDestinationId();
        if (!ds.some((d) => d.id === saved)) {
          const fallback = ds[0]?.id ?? 1;
          localStorage.setItem("virsa_dest_id", String(fallback));
          setCurrentId(fallback);
        }
      })
      .finally(() => {
        if (alive) setLoading(false);
      });
    return () => {
      alive = false;
    };
  }, []);

  const select = (id: number) => {
    localStorage.setItem("virsa_dest_id", String(id));
    setCurrentId(id);
    setCurrentDestinationId(id);
  };

  // Keep the module-level id in sync so request()/endpoints defaults match the UI.
  useEffect(() => {
    setCurrentDestinationId(currentId);
  }, [currentId]);

  const current = useMemo(() => destinations.find((d) => d.id === currentId) ?? null, [destinations, currentId]);

  return <Ctx.Provider value={{ destinations, current, currentId, loading, select }}>{children}</Ctx.Provider>;
}

export function useDestination() {
  return useContext(Ctx);
}