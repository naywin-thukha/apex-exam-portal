import React from 'react';

export const AdminLogin: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 max-w-md w-full">
        <h2 className="text-2xl font-bold text-gray-900">Super Admin Login</h2>
        <p className="text-sm text-gray-500 mt-1">Sign in to access your portal.</p>
      </div>
    </div>
  );
};

export default AdminLogin;