import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { 
  Home, 
  Users, 
  Settings, 
  ChevronDown 
} from 'lucide-react';

export const AdminLayout: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col h-screen bg-[#F0F5FA] overflow-hidden">
      {/* Top Header Bar with APEX Logo */}
      <header className="h-16 bg-[#F0F5FA] flex items-center px-6 border-b border-gray-200/50 flex-shrink-0">
        <div className="flex items-center gap-2">
          {/* APEX Triangle Icon */}
          <div className="flex items-center">
            <span className="text-amber-500 font-extrabold text-2xl tracking-tighter">▲</span>
            <span className="text-[#0A2540] font-black text-2xl tracking-wider ml-1">PEX</span>
          </div>
          <span className="text-[9px] text-blue-600 uppercase font-bold tracking-widest block leading-tight border-l border-gray-300 pl-2 ml-1">
            EDUCATION CENTER
          </span>
        </div>
      </header>

      {/* Main Body Layout (Sidebar + Content) */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-60 bg-[#0B2545] text-white flex flex-col justify-between flex-shrink-0 relative overflow-hidden">
          {/* Top Nav Items */}
          <nav className="p-3 space-y-2 mt-2">
            <NavLink
              to="/admin/dashboard"
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all ${
                  isActive 
                    ? 'bg-[#1E68F6] text-white shadow-lg shadow-blue-500/30' 
                    : 'text-blue-200 hover:bg-white/10 hover:text-white'
                }`
              }
            >
              <Home className="w-5 h-5" />
              Dashboard
            </NavLink>

            <NavLink
              to="/admin/users"
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all ${
                  isActive 
                    ? 'bg-[#1E68F6] text-white shadow-lg shadow-blue-500/30' 
                    : 'text-blue-200 hover:bg-white/10 hover:text-white'
                }`
              }
            >
              <Users className="w-5 h-5" />
              User Management
            </NavLink>

            <NavLink
              to="/admin/settings"
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all ${
                  isActive 
                    ? 'bg-[#1E68F6] text-white shadow-lg shadow-blue-500/30' 
                    : 'text-blue-200 hover:bg-white/10 hover:text-white'
                }`
              }
            >
              <Settings className="w-5 h-5" />
              Settings
            </NavLink>
          </nav>

          {/* Decorative Background Mountain Shapes at bottom of sidebar */}
          <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-blue-900/40 to-transparent pointer-events-none" />

          {/* User Profile Footer in Sidebar */}
          <div className="p-3 border-t border-blue-900/40 z-10">
            <div 
              onClick={() => navigate('/admin/profile')}
              className="flex items-center justify-between p-2 rounded-xl cursor-pointer hover:bg-white/10 transition-colors group"
            >
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-orange-100 flex items-center justify-center border border-white/20 overflow-hidden">
                  <span className="text-xs font-bold text-gray-700">SJ</span>
                </div>
                <div>
                  <p className="text-xs font-semibold text-white group-hover:text-blue-300 transition-colors">
                    Ms. Sarah Johnson
                  </p>
                  <p className="text-[10px] text-blue-300">Super Admin</p>
                </div>
              </div>
              <ChevronDown className="w-4 h-4 text-blue-300 group-hover:translate-y-0.5 transition-transform" />
            </div>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto p-2">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;