import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import {
  Package,
  Palette,
  Layers,
  FileText,
  ExternalLink,
  ChevronRight,
  Database
} from 'lucide-react';

export const AdminLayout = () => {
  const location = useLocation();

  const navItems = [
    {
      to: '/admin',
      label: 'Products',
      icon: Package,
      exact: true,
      isActive: location.pathname === '/admin' || location.pathname === '/admin/',
    },
    {
      to: '/admin/finishes',
      label: 'Finishes',
      icon: Palette,
      isActive: location.pathname.startsWith('/admin/finishes'),
    },
    {
      to: '/admin/import',
      label: 'Batch Import & Sync',
      icon: Layers,
      isActive: location.pathname.startsWith('/admin/import'),
    },
    {
      to: '/admin/audit-logs',
      label: 'Audit Trail Logs',
      icon: FileText,
      isActive: location.pathname.startsWith('/admin/audit-logs'),
    },
  ];

  return (
    <div className="min-h-screen bg-[#F4F6F9] text-slate-900 flex flex-col md:flex-row">
      {/* 1. Sleek Dark Admin Sidebar */}
      <aside className="w-full md:w-64 bg-[#0F172A] text-slate-300 flex flex-col justify-between shrink-0 border-r border-slate-800">
        <div>
          {/* Brand Header */}
          <div className="p-5 border-b border-slate-800/80 flex items-center justify-between">
            <div>
              <span className="text-xl font-bold tracking-tight text-white">
                Fanstudio<span className="text-amber-500 font-extrabold">AI</span>
              </span>
              <div className="text-[10px] text-slate-400 uppercase tracking-widest font-semibold mt-0.5">
                Admin Panel
              </div>
            </div>
            <Link
              to="/users"
              className="p-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors cursor-pointer"
              title="Return to Customer Storefront"
            >
              <ExternalLink className="w-4 h-4 text-amber-400" />
            </Link>
          </div>

          {/* Navigation Links */}
          <nav className="p-3 space-y-1.5 text-xs font-semibold">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl transition-all cursor-pointer ${
                    item.isActive
                      ? 'bg-amber-600 text-white shadow-xs font-bold'
                      : 'hover:bg-slate-800/70 text-slate-300 hover:text-white'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </div>
                  {item.isActive && <ChevronRight className="w-3.5 h-3.5 text-amber-200" />}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Database & System Info Footer */}
        <div className="p-4 border-t border-slate-800/80 space-y-3">
          <div className="bg-slate-900/90 rounded-xl p-3 border border-slate-800 text-[11px]">
            <div className="flex items-center justify-between text-slate-400 font-medium">
              <span className="flex items-center gap-1.5">
                <Database className="w-3.5 h-3.5 text-emerald-400" />
                MongoDB Engine
              </span>
              <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800/60">
                ACTIVE
              </span>
            </div>
            <div className="text-[10px] text-slate-500 mt-1">
              File-backed JSON / Live PyMongo
            </div>
          </div>

          <Link
            to="/users"
            className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-200 text-xs font-bold transition-colors cursor-pointer"
          >
            <span>Customer Storefront</span>
            <ExternalLink className="w-3.5 h-3.5 text-amber-400" />
          </Link>
        </div>
      </aside>

      {/* 2. Main Admin Content Area */}
      <main className="flex-1 min-w-0 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
};
