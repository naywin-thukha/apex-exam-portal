import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AdminLayout } from './layouts/AdminLayout';
import { Dashboard } from './pages/admin/Dashboard';
import { UserManagement } from './pages/admin/UserManagement';
import { Profile } from './pages/admin/Profile';
import { ProfileProvider } from './context/ProfileContext';

export function App() {
  return (
    <ProfileProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/admin/dashboard" replace />} />
          <Route path="/admin" element={<AdminLayout />}>
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="users" element={<UserManagement />} />
            <Route path="settings" element={<Profile />} />
            <Route path="profile" element={<Profile />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ProfileProvider>
  );
}

export default App;