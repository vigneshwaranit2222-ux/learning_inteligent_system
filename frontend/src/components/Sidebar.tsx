import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, User, FileText, BookOpen, 
  HelpCircle, Briefcase, Compass, Award, ShieldAlert, LogOut
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Sidebar: React.FC = () => {
  const { user, role, logout } = useAuth();

  const learnerNav = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'My Profile', path: '/profile', icon: User },
    { name: 'Resume Upload', path: '/resumes', icon: FileText },
    { name: 'Courses', path: '/courses', icon: BookOpen },
    { name: 'Assessments', path: '/assessments', icon: HelpCircle },
    { name: 'Target Jobs', path: '/jobs', icon: Briefcase },
    { name: 'Recommendations', path: '/recommendations', icon: Compass },
    { name: 'Career Reports', path: '/reports', icon: Award },
  ];

  const adminNav = [
    { name: 'Admin Console', path: '/admin', icon: ShieldAlert },
    { name: 'Course Catalog', path: '/courses', icon: BookOpen },
    { name: 'Job Master', path: '/jobs', icon: Briefcase },
  ];

  const navItems = role === 'admin' ? adminNav : learnerNav;

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col min-h-screen border-r border-slate-800">
      <div className="p-5 border-b border-slate-800 flex items-center space-x-3">
        <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-lg shadow-md">
          AI
        </div>
        <div>
          <h1 className="text-sm font-bold text-white tracking-tight">Career Intelligence</h1>
          <p className="text-xs text-slate-400 capitalize">{role || 'Learner'} Portal</p>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-colors duration-150 ${
                  isActive
                    ? 'bg-blue-600 text-white font-semibold shadow-sm'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`
              }
            >
              <Icon className="w-5 h-5 mr-3 flex-shrink-0" />
              {item.name}
            </NavLink>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-800">
        <div className="flex items-center space-x-3 mb-3">
          <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-xs font-semibold text-white">
            {user?.full_name ? user.full_name[0].toUpperCase() : 'U'}
          </div>
          <div className="flex-1 truncate">
            <p className="text-xs font-semibold text-white truncate">{user?.full_name}</p>
            <p className="text-[11px] text-slate-400 truncate">{user?.email}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center justify-center px-3 py-2 text-xs font-medium text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-lg transition-colors"
        >
          <LogOut className="w-4 h-4 mr-2" />
          Sign Out
        </button>
      </div>
    </aside>
  );
};
