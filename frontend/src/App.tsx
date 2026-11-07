import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Context
import { ProfileProvider } from './context/ProfileContext';

// Auth / Login Page
import { Login } from './pages/Login';

// Admin Layout & Pages
import { AdminLayout } from './layouts/AdminLayout';
import { Dashboard as AdminDashboard } from './pages/admin/Dashboard';
import { UserManagement } from './pages/admin/UserManagement';
import { Profile } from './pages/admin/Profile';

// Teacher Layout & Pages
import { TeacherLayout } from './layouts/TeacherLayout';
import { TeacherDashboard } from './pages/teacher/TeacherDashboard';
import { ExamManagement } from './pages/teacher/ExamManagement';
import { Results } from './pages/teacher/Results';

export function App() {
  return (
    <ProfileProvider>
      <BrowserRouter>
        <Routes>
          {/* Default Route redirects to Login */}
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/login" element={<Login />} />

          {/* Admin Portal Routes */}
          <Route path="/admin" element={<AdminLayout />}>
            <Route path="dashboard" element={<AdminDashboard />} />
            <Route path="users" element={<UserManagement />} />
            <Route path="settings" element={<Profile />} />
            <Route path="profile" element={<Profile />} />
          </Route>

          {/* Teacher Portal Routes */}
          <Route path="/teacher" element={<TeacherLayout />}>
            <Route path="dashboard" element={<TeacherDashboard />} />
            <Route path="exams" element={<ExamManagement />} />
            <Route path="results" element={<Results />} />
            <Route path="profile" element={<Profile />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ProfileProvider>
  );
}

export default App;