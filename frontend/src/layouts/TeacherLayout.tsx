import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FileText, 
  BarChart2 
} from 'lucide-react';
import { useProfile } from '../context/ProfileContext';

export const TeacherLayout: React.FC = () => {
  const navigate = useNavigate();
  const { name, avatar } = useProfile();

  const initials = name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .substring(0, 2)
    .toUpperCase();

  return (
    <div className="flex flex-col h-screen bg-[#F0F5FA] overflow-hidden">
      {/* Top Header Bar */}
      <header className="h-16 bg-[#F0F5FA] flex items-center px-6 border-b border-gray-200/50 flex-shrink-0">
        <div className="flex items-center gap-2">
          <div className="flex items-center">
            <span className="text-amber-500 font-extrabold text-2xl tracking-tighter">▲</span>
            <span className="text-[#0A2540] font-black text-2xl tracking-wider ml-1">PEX</span>
          </div>
          <span className="text-[9px] text-blue-600 uppercase font-bold tracking-widest block leading-tight border-l border-gray-300 pl-2 ml-1">
            TEACHER PORTAL
          </span>
        </div>
      </header>

      {/* Main Body Layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-60 bg-[#0B2545] text-white flex flex-col justify-between flex-shrink-0">
          <nav className="p-3 space-y-1.5 mt-2">
            <NavLink
              to="/teacher/dashboard"
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all ${
                  isActive ? 'bg-[#1E68F6] text-white shadow-lg shadow-blue-500/30' : 'text-blue-200 hover:bg-white/10 hover:text-white'
                }`
              }
            >
              <LayoutDashboard className="w-4 h-4" />
              Dashboard
            </NavLink>

            <NavLink
              to="/teacher/exams"
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all ${
                  isActive ? 'bg-[#1E68F6] text-white shadow-lg shadow-blue-500/30' : 'text-blue-200 hover:bg-white/10 hover:text-white'
                }`
              }
            >
              <FileText className="w-4 h-4" />
              Exams
            </NavLink>

            <NavLink
              to="/teacher/results"
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all ${
                  isActive ? 'bg-[#1E68F6] text-white shadow-lg shadow-blue-500/30' : 'text-blue-200 hover:bg-white/10 hover:text-white'
                }`
              }
            >
              <BarChart2 className="w-4 h-4" />
              Results
            </NavLink>
          </nav>

          {/* Fully Clickable User Profile Footer */}
          <div className="p-3 m-3">
            <button
              onClick={() => navigate('/teacher/profile')}
              className="w-full p-2.5 rounded-2xl bg-white/5 hover:bg-white/10 border border-white/10 flex items-center gap-3 transition-all cursor-pointer text-left"
            >
              <div className="w-9 h-9 rounded-full bg-blue-100 flex items-center justify-center border border-white/20 overflow-hidden flex-shrink-0">
                {avatar ? (
                  <img src={avatar} alt={name} className="w-full h-full object-cover" />
                ) : (
                  <span className="text-xs font-bold text-gray-700">{initials}</span>
                )}
              </div>
              <div className="overflow-hidden">
                <p className="text-xs font-semibold text-white truncate">
                  {name}
                </p>
                <p className="text-[10px] text-blue-300">Teacher Profile</p>
              </div>
            </button>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default TeacherLayout;