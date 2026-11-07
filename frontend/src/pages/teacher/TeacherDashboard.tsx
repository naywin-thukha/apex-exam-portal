import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, HelpCircle, Users, Calendar, MoreVertical } from 'lucide-react';

export const TeacherDashboard: React.FC = () => {
  const navigate = useNavigate();

  const upcomingExams = [
    { id: '1', name: 'Mathematics - Unit 1', date: 'Oct 28, 2026 10:00 AM', duration: '1 hour', status: 'Scheduled' },
    { id: '2', name: 'Physics - Chapter 3', date: 'Nov 4, 2026 02:00 PM', duration: '45 mins', status: 'Scheduled' },
    { id: '3', name: 'English - Grammar', date: 'Nov 15, 2026 10:00 AM', duration: '30 mins', status: 'Scheduled' },
  ];

  return (
    <div className="p-8 bg-[#F0F5FA] min-h-screen">
      {/* Welcome Banner */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Welcome back, Ms. Sarah! 👋</h1>
        <p className="text-gray-500 text-sm mt-0.5">Here’s what’s happening with your exams and students today.</p>
      </div>

      {/* Stats Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">My Exams</p>
            <h3 className="text-2xl font-bold text-gray-900">5</h3>
            <span onClick={() => navigate('/teacher/exams')} className="text-xs text-blue-600 font-medium cursor-pointer hover:underline mt-1 inline-block">View all →</span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <FileText className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Total Questions</p>
            <h3 className="text-2xl font-bold text-gray-900">320</h3>
            <span onClick={() => navigate('/teacher/exams')} className="text-xs text-blue-600 font-medium cursor-pointer hover:underline mt-1 inline-block">Manage questions →</span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <HelpCircle className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Total Students</p>
            <h3 className="text-2xl font-bold text-gray-900">45</h3>
            <span className="text-xs text-blue-600 font-medium cursor-pointer hover:underline mt-1 inline-block">View students →</span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <Users className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Upcoming Exams</p>
            <h3 className="text-2xl font-bold text-gray-900">3</h3>
            <span onClick={() => navigate('/teacher/exams')} className="text-xs text-blue-600 font-medium cursor-pointer hover:underline mt-1 inline-block">View schedule →</span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <Calendar className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Upcoming Exams Table Section */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-bold text-gray-900 text-base">Upcoming Exams</h2>
          <button onClick={() => navigate('/teacher/exams')} className="text-xs font-semibold text-blue-600 hover:underline cursor-pointer">View All</button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-gray-100 text-gray-400 text-xs font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Exam Name</th>
                <th className="py-3 px-4">Date & Time</th>
                <th className="py-3 px-4">Duration</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-sm">
              {upcomingExams.map((exam) => (
                <tr key={exam.id} className="hover:bg-gray-50/50 transition-colors">
                  <td className="py-3.5 px-4 font-semibold text-gray-900 flex items-center gap-2.5">
                    <FileText className="w-4 h-4 text-blue-600" />
                    {exam.name}
                  </td>
                  <td className="py-3.5 px-4 text-gray-600">{exam.date}</td>
                  <td className="py-3.5 px-4 text-gray-600">{exam.duration}</td>
                  <td className="py-3.5 px-4">
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-600">
                      {exam.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <button onClick={() => navigate('/teacher/exams')} className="text-xs font-semibold text-blue-600 hover:underline mr-4 cursor-pointer">View Details</button>
                    <button className="text-gray-400 hover:text-gray-600 cursor-pointer">
                      <MoreVertical className="w-4 h-4 inline" />
                    </button>
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

export default TeacherDashboard;