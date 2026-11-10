import React from 'react';
import { Bell, Search, ShieldCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Navbar: React.FC = () => {
  const { user, role } = useAuth();

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-10 shadow-sm">
      <div className="flex items-center space-x-3 w-96">
        <div className="relative w-full">
          <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search skills, courses, target roles..."
            className="w-full pl-9 pr-4 py-1.5 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all"
          />
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-1.5 bg-emerald-50 text-emerald-700 px-2.5 py-1 rounded-full text-xs font-semibold border border-emerald-200">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>System Healthy</span>
        </div>

        <div className="w-px h-6 bg-slate-200" />

        <div className="flex items-center space-x-2">
          <div className="text-right">
            <span className="text-xs font-bold text-slate-800 block">{user?.full_name}</span>
            <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">{role}</span>
          </div>
        </div>
      </div>
    </header>
  );
};
