import { useState } from "react";
import { NavLink, Outlet, Link, Routes, Route, useNavigate, Navigate } from "react-router-dom";
import {
  Store,
  Sparkles,
  ArrowLeft,
  LogOut,
  LayoutGrid,
  PlusCircle,
  Inbox,
} from "lucide-react";
import { clsx } from "clsx";
import { useAuth } from "../state/auth";
import BusinessOverview from "./BusinessOverview";
import BusinessManage from "./BusinessManage";

export default function BusinessApp() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen bg-sand-100">
      <aside className="flex w-56 shrink-0 flex-col border-r border-ink/10 bg-ink text-sand-200">
        <div className="flex items-center gap-2 px-4 py-4">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-saffron text-teal-dark"><Store className="h-4 w-4" /></span>
          <span className="leading-tight">
            <span className="block font-display text-base font-bold text-white">Maker Portal</span>
            <span className="block text-[9px] uppercase tracking-[0.18em] text-sand-400">Virsa · community</span>
          </span>
        </div>
        <nav className="flex-1 space-y-0.5 px-2 py-2">
          <NavLink to="/business" end className={({ isActive }) => clsx("flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium", isActive ? "bg-saffron/90 text-teal-dark" : "text-sand-300 hover:bg-white/5")}>
            <LayoutGrid className="h-4 w-4" /> My businesses
          </NavLink>
          <NavLink to="/business/new" className={({ isActive }) => clsx("flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium", isActive ? "bg-saffron/90 text-teal-dark" : "text-sand-300 hover:bg-white/5")}>
            <PlusCircle className="h-4 w-4" /> Register a business
          </NavLink>
          <Link to="/artisans" className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-sand-300 hover:bg-white/5">
            <Inbox className="h-4 w-4" /> Public profiles
          </Link>
        </nav>
        <div className="border-t border-white/10 p-3">
          <p className="mb-2 truncate px-1 text-[11px] font-semibold text-sand-400">{user?.name}</p>
          <button onClick={() => { logout(); navigate("/"); }} className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm text-sand-300 hover:bg-white/5">
            <LogOut className="h-4 w-4" /> Sign out
          </button>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between gap-3 border-b border-ink/10 bg-white/80 px-6 py-3 backdrop-blur">
          <Link to="/" className="flex items-center gap-1.5 text-xs font-medium text-ink-muted hover:text-teal">
            <ArrowLeft className="h-3.5 w-3.5" /> Public site
          </Link>
          <span className="flex items-center gap-2 text-xs font-semibold text-ink">
            <Sparkles className="h-4 w-4 text-saffron-deep" /> Business & artisan workspace
          </span>
        </header>
        <main className="flex-1 p-6">
          <Routes>
            <Route index element={<BusinessOverview />} />
            <Route path="new" element={<BusinessOverview create />} />
            <Route path=":id" element={<BusinessManage />} />
            <Route path="*" element={<Navigate to="/business" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}