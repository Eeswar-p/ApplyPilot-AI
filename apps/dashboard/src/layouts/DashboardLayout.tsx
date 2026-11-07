import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { User, FileText, Settings, LogOut, Rocket, Sliders, Compass, PlayCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function DashboardLayout() {
  const { user, profile, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItems = [
    { to: "/profile", icon: User, label: "Career Profile" },
    { to: "/resumes", icon: FileText, label: "Resumes" },
    { to: "/preferences", icon: Sliders, label: "Job Preferences" },
    { to: "/discovery", icon: Compass, label: "Job Discovery" },
    { to: "/automation", icon: PlayCircle, label: "Automation Center" },
    { to: "/settings", icon: Settings, label: "Settings" },
  ];

  return (
    <div className="flex h-screen bg-background text-slate-200">
      {/* Sidebar */}
      <aside className="w-64 glass-panel border-r border-y-0 border-l-0 rounded-none hidden md:flex flex-col">
        <div className="p-6 flex items-center gap-3 border-b border-slate-700/50">
          <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center shadow-lg shadow-primary-500/30">
            <Rocket className="w-4 h-4 text-white" />
          </div>
          <div>
            <span className="font-bold text-base text-white tracking-tight">ApplyPilot AI</span>
            <p className="text-[10px] text-primary-400 font-medium">Autonomous Job Pilot</p>
          </div>
        </div>
        
        <nav className="flex-1 px-4 space-y-1 mt-4 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all font-medium text-sm ${
                  isActive 
                    ? 'bg-primary-500/15 text-primary-400 border border-primary-500/30 shadow-sm' 
                    : 'text-slate-400 hover:text-slate-200 hover:bg-surfaceHighlight/50'
                }`
              }
            >
              <item.icon className="w-4 h-4" />
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* User Card & Logout */}
        <div className="p-4 border-t border-slate-700/50 space-y-2">
          {user && (
            <div className="px-3 py-2 bg-surface/60 rounded-xl border border-slate-700/40">
              <p className="text-xs font-semibold text-white truncate">{profile?.full_name || 'Pilot Candidate'}</p>
              <p className="text-[11px] text-slate-400 truncate">{user.email}</p>
            </div>
          )}
          <button 
            onClick={handleLogout}
            className="flex w-full items-center gap-3 px-3 py-2 rounded-xl text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-colors font-medium text-sm cursor-pointer"
          >
            <LogOut className="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto bg-gradient-to-br from-background to-surface/40">
        <div className="p-6 md:p-8 max-w-6xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
