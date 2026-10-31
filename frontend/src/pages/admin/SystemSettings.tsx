import React, { useState } from 'react';
import { Settings as SettingsIcon, Shield, Save } from 'lucide-react';

export const SystemSettings: React.FC = () => {
  // System Information State
  const [portalName, setPortalName] = useState('Apex');
  const [organizationName, setOrganizationName] = useState('');
  const [timeZone, setTimeZone] = useState('');

  // Security Settings State
  const [passwordMaxLength, setPasswordMaxLength] = useState(12);
  const [requireSpecialChar, setRequireSpecialChar] = useState(true);
  const [sessionTimeout, setSessionTimeout] = useState(30);
  const [enable2FA, setEnable2FA] = useState(true);

  const handleSaveSettings = (e: React.FormEvent) => {
    e.preventDefault();
    const settingsData = {
      portalName,
      organizationName,
      timeZone,
      passwordMaxLength,
      requireSpecialChar,
      sessionTimeout,
      enable2FA,
    };
    console.log('Saved Settings:', settingsData);
    alert('Settings saved successfully!');
  };

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-500 text-sm mt-1">Manage system configuration and preferences</p>
      </div>

      <form onSubmit={handleSaveSettings}>
        {/* Two-Column Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          
          {/* Left Column: System Information */}
          <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 flex flex-col justify-between">
            <div>
              {/* Card Header */}
              <div className="flex items-center gap-3 mb-8">
                <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
                  <SettingsIcon className="w-5 h-5" />
                </div>
                <h2 className="text-lg font-bold text-gray-900">System Information</h2>
              </div>

              {/* Form Inputs */}
              <div className="space-y-6">
                {/* Portal Name */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Portal Name</label>
                  <input
                    type="text"
                    value={portalName}
                    onChange={(e) => setPortalName(e.target.value)}
                    placeholder="Portal Name"
                    className="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all"
                  />
                </div>

                {/* Organization Name */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Organization Name</label>
                  <input
                    type="text"
                    value={organizationName}
                    onChange={(e) => setOrganizationName(e.target.value)}
                    placeholder="Enter organization name"
                    className="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all"
                  />
                </div>

                {/* Time Zone */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Time Zone</label>
                  <select
                    value={timeZone}
                    onChange={(e) => setTimeZone(e.target.value)}
                    className="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm text-gray-700 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all cursor-pointer"
                  >
                    <option value="" disabled>Select time zone</option>
                    <option value="UTC+06:30">Myanmar Time (UTC+06:30)</option>
                    <option value="UTC+00:00">UTC (Coordinated Universal Time)</option>
                    <option value="UTC-05:00">Eastern Time (EST)</option>
                    <option value="UTC-08:00">Pacific Time (PST)</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Security Settings */}
          <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 flex flex-col justify-between">
            <div>
              {/* Card Header */}
              <div className="flex items-center gap-3 mb-8">
                <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
                  <Shield className="w-5 h-5" />
                </div>
                <h2 className="text-lg font-bold text-gray-900">Security Settings</h2>
              </div>

              {/* Form Inputs & Switches */}
              <div className="space-y-6">
                {/* Password max length */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Password max length</label>
                  <input
                    type="number"
                    value={passwordMaxLength}
                    onChange={(e) => setPasswordMaxLength(Number(e.target.value))}
                    className="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all"
                  />
                </div>

                {/* Require special character toggle */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Require special character</label>
                  <div className="flex items-center gap-3 mt-1">
                    <button
                      type="button"
                      onClick={() => setRequireSpecialChar(!requireSpecialChar)}
                      className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                        requireSpecialChar ? 'bg-blue-600' : 'bg-gray-200'
                      }`}
                    >
                      <span
                        className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                          requireSpecialChar ? 'translate-x-5' : 'translate-x-0'
                        }`}
                      />
                    </button>
                    <span className="text-xs text-gray-500">Enable special character requirement</span>
                  </div>
                </div>

                {/* Session Timeout */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Session Timeout (minutes)</label>
                  <input
                    type="number"
                    value={sessionTimeout}
                    onChange={(e) => setSessionTimeout(Number(e.target.value))}
                    className="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all"
                  />
                </div>

                {/* 2 Factor Authentication toggle */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">2 Factor Authentication</label>
                  <div className="flex items-center gap-3 mt-1">
                    <button
                      type="button"
                      onClick={() => setEnable2FA(!enable2FA)}
                      className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                        enable2FA ? 'bg-blue-600' : 'bg-gray-200'
                      }`}
                    >
                      <span
                        className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                          enable2FA ? 'translate-x-5' : 'translate-x-0'
                        }`}
                      />
                    </button>
                    <span className="text-xs text-gray-500">Enable 2FA for users</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>

        {/* Save Button Footer */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center justify-end">
          <button
            type="submit"
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 shadow-md shadow-blue-600/20 transition-colors"
          >
            <Save className="w-4 h-4" /> Save Settings
          </button>
        </div>
      </form>
    </div>
  );
};

export default SystemSettings;