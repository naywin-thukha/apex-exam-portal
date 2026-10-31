import React, { useState } from 'react';
import { Users, FileText, HelpCircle, Award, Clock } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const [showAll, setShowAll] = useState(false);

  const stats = [
    { title: 'Total User', count: '124', icon: Users, color: 'text-blue-600', bg: 'bg-blue-50' },
    { title: 'Total Exam', count: '18', icon: FileText, color: 'text-emerald-600', bg: 'bg-emerald-50' },
    { title: 'Total Question', count: '2450', icon: HelpCircle, color: 'text-purple-600', bg: 'bg-purple-50' },
    { title: 'Total Results', count: '1256', icon: Award, color: 'text-blue-600', bg: 'bg-blue-50' },
  ];

  const allActivities = [
    { time: '2025-05-28 10:24 AM', activity: 'New user registered', user: 'teacher 1', role: 'Teacher' },
    { time: '2025-05-28 09:17 AM', activity: 'Exam created: Mathematics 101', user: 'student 1', role: 'Student' },
    { time: '2025-05-28 08:45 AM', activity: 'Question added to Science Exam', user: 'teacher 1', role: 'Teacher' },
    { time: '2025-05-27 04:12 PM', activity: 'System settings updated', user: 'Sarah Johnson', role: 'Super Admin' },
    { time: '2025-05-27 02:30 PM', activity: 'Exam deleted: Physics 102', user: 'Sarah Johnson', role: 'Super Admin' },
  ];

  const displayedActivities = showAll ? allActivities : allActivities.slice(0, 3);

  return (
    <div className="p-8 bg-[#F0F5FA] min-h-screen">
      {/* Welcome Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Welcome, Ms. Sarah Johnson</h1>
        <p className="text-gray-500 text-sm mt-1">Super Admin Dashboard</p>
      </div>

      {/* Stats Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {stats.slice(0, 3).map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500 mb-1">{stat.title}</p>
                <h3 className="text-3xl font-bold text-gray-900">{stat.count}</h3>
              </div>
              <div className={`w-12 h-12 rounded-2xl ${stat.bg} ${stat.color} flex items-center justify-center shadow-sm`}>
                <Icon className="w-6 h-6" />
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-500 mb-1">Total Results</p>
            <h3 className="text-3xl font-bold text-gray-900">1256</h3>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center shadow-sm">
            <Award className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Recent Activities Section */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <Clock className="w-5 h-5 text-gray-500" />
            <h2 className="text-lg font-bold text-gray-900">
              {showAll ? 'All Activities' : 'Recent Activities'}
            </h2>
          </div>
          <button 
            onClick={() => setShowAll(!showAll)}
            className="text-sm font-semibold text-blue-600 hover:text-blue-700 cursor-pointer transition-colors"
          >
            {showAll ? 'Show Less ↑' : 'View All →'}
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-gray-100 text-gray-400 text-xs font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Time</th>
                <th className="py-3 px-4">Activity</th>
                <th className="py-3 px-4 text-right">User</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-sm">
              {displayedActivities.map((act, index) => (
                <tr key={index} className="hover:bg-gray-50/50 transition-colors">
                  <td className="py-4 px-4 text-gray-500 flex items-center gap-2">
                    <Clock className="w-4 h-4 text-gray-400 flex-shrink-0" />
                    {act.time}
                  </td>
                  <td className="py-4 px-4 font-medium text-gray-800">{act.activity}</td>
                  <td className="py-4 px-4 text-right">
                    <div className="font-semibold text-gray-900">{act.user}</div>
                    <div className="text-xs text-gray-400">{act.role}</div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;