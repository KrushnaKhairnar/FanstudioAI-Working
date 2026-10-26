import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { Search, Heart, ShoppingBag, Shield, Sparkles } from 'lucide-react';
import { useCatalogStore } from '../../features/catalog/store.js';

export const UserLayout = () => {
  const location = useLocation();
  const searchQuery = useCatalogStore((s) => s.searchQuery);
  const setSearchQuery = useCatalogStore((s) => s.setSearchQuery);

  const isCatalogActive = location.pathname === '/users' || location.pathname.startsWith('/users/products');
  const isVisualizerActive = location.pathname.startsWith('/users/visualizer');

  return (
    <div className="min-h-screen bg-[#FDFBF7] font-sans antialiased text-slate-900 selection:bg-amber-100 selection:text-amber-900 flex flex-col">
      {/* Global Header */}
      <header className="sticky top-0 z-40 bg-[#141B22] border-b border-slate-800 text-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-18 flex items-center justify-between gap-4">
          {/* Brand Text Logo */}
          <div className="flex items-center gap-8">
            <Link
              to="/users"
              className="flex items-center text-left focus:outline-none cursor-pointer group"
            >
              <span className="text-2xl font-bold tracking-tight text-white group-hover:text-amber-400 transition-colors">
                Fanstudio<span className="text-amber-500 font-extrabold">AI</span>
              </span>
            </Link>

            {/* Navigation Links */}
            <nav className="flex items-center gap-3 sm:gap-6 text-xs sm:text-sm font-medium">
              <Link
                to="/users"
                className={`py-5 transition-colors relative cursor-pointer font-bold ${
                  isCatalogActive
                    ? 'text-amber-400 font-extrabold'
                    : 'text-slate-300 hover:text-white'
                }`}
              >
                Fans
                {isCatalogActive && (
                  <span className="absolute bottom-0 left-0 right-0 h-0.75 bg-amber-500 rounded-t-sm" />
                )}
              </Link>

              <Link
                to="/users/visualizer"
                className={`py-5 transition-colors relative cursor-pointer flex items-center gap-1.5 ${
                  isVisualizerActive
                    ? 'text-amber-400 font-extrabold'
                    : 'text-slate-300 hover:text-white'
                }`}
              >
                <Sparkles className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                <span>AI Visualizer</span>
                {isVisualizerActive && (
                  <span className="absolute bottom-0 left-0 right-0 h-0.75 bg-amber-500 rounded-t-sm" />
                )}
              </Link>

              <a
                href="#how-it-works"
                className="hidden lg:inline text-slate-300 hover:text-white transition-colors cursor-pointer"
              >
                How It Works
              </a>

              <a
                href="#my-designs"
                className="hidden lg:inline text-slate-300 hover:text-white transition-colors cursor-pointer"
              >
                My Designs
              </a>
            </nav>
          </div>

          {/* Search Bar & User Actions */}
          <div className="flex items-center gap-4">
            <div className="relative hidden sm:block w-64 lg:w-80">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search fans, designs..."
                className="w-full pl-9 pr-4 py-2 bg-slate-900/90 border border-slate-700/80 rounded-lg text-sm text-white placeholder-slate-400 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 transition-all"
              />
            </div>

            {/* Quick Admin Panel Switcher */}
            <Link
              to="/admin"
              className="px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 border transition-all cursor-pointer bg-slate-800/80 hover:bg-slate-700 text-slate-200 border-slate-700 hover:border-amber-500/50"
              title="Switch to Admin Management Panel"
            >
              <Shield className="w-3.5 h-3.5 text-amber-400" />
              <span className="hidden sm:inline">Admin Panel</span>
            </Link>

            {/* Wishlist */}
            <button className="text-slate-300 hover:text-white p-2 rounded-lg hover:bg-slate-800/60 transition-colors cursor-pointer relative">
              <Heart className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-amber-500 rounded-full" />
            </button>

            {/* Cart */}
            <button className="text-slate-300 hover:text-white p-2 rounded-lg hover:bg-slate-800/60 transition-colors cursor-pointer relative">
              <ShoppingBag className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-amber-500 rounded-full" />
            </button>

            {/* User Profile Avatar */}
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-amber-500 to-amber-700 flex items-center justify-center font-bold text-white text-sm shadow-inner cursor-pointer ring-2 ring-amber-500/30">
              K
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1">
        <Outlet context={{ searchQuery, setSearchQuery }} />
      </main>
    </div>
  );
};
