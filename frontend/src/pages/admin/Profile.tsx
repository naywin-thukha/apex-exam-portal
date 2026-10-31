import React, { useState } from 'react';
import { User, Upload, Check } from 'lucide-react';

export const Profile: React.FC = () => {
  const [formData, setFormData] = useState({
    fullName: 'Ms. Sarah Johnson',
    email: 'sarah.johnson@apex.edu.mm',
    phoneNumber: '+95 9 123 456 789',
    bio: 'Super Admin at APEX Education Center. Passionate about education and student success.',
  });

  const [profileImage, setProfileImage] = useState<string>(
    'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150'
  );
  const [successMessage, setSuccessMessage] = useState<string>('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Handle image selection and instant preview
  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const imageUrl = URL.createObjectURL(file);
      setProfileImage(imageUrl);
      console.log('Selected file for upload:', file);
    }
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Connect this payload and FormData to your Java Spring Boot backend API endpoint
    console.log('Saving profile data:', { ...formData, profileImage });
    setSuccessMessage('Profile updated successfully!');
    setTimeout(() => setSuccessMessage(''), 3000);
  };

  const handleDiscard = () => {
    setFormData({
      fullName: 'Ms. Sarah Johnson',
      email: 'sarah.johnson@apex.edu.mm',
      phoneNumber: '+95 9 123 456 789',
      bio: 'Super Admin at APEX Education Center. Passionate about education and student success.',
    });
  };

  return (
    <div className="p-8 bg-[#F0F5FA] min-h-screen">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Edit Profile</h1>
        {successMessage && (
          <div className="flex items-center gap-2 bg-emerald-50 text-emerald-600 px-4 py-2 rounded-xl text-sm font-semibold border border-emerald-200 shadow-sm animate-fade-in">
            <Check className="w-4 h-4" />
            {successMessage}
          </div>
        )}
      </div>

      {/* Profile Header Preview */}
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center gap-4 mb-6">
        <div className="w-16 h-16 rounded-full overflow-hidden bg-blue-50 flex items-center justify-center flex-shrink-0 border border-blue-100">
          <img 
            src={profileImage} 
            alt="Profile Preview" 
            className="w-full h-full object-cover"
          />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900">{formData.fullName}</h2>
          <p className="text-sm text-gray-400 font-medium">Super Admin</p>
        </div>
      </div>

      <form onSubmit={handleSave}>
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 mb-6">
          <div className="flex items-center gap-2 text-gray-900 font-bold text-lg mb-6 pb-4 border-b border-gray-100">
            <User className="w-5 h-5 text-blue-600" />
            <h3>Personal Information</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Full Name</label>
              <input
                type="text"
                name="fullName"
                value={formData.fullName}
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-xl border border-gray-200 text-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all bg-white"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Email Address</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-xl border border-gray-200 text-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all bg-white"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Phone Number</label>
              <input
                type="text"
                name="phoneNumber"
                value={formData.phoneNumber}
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-xl border border-gray-200 text-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all bg-white"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-semibold text-gray-700 mb-2">Bio</label>
              <textarea
                name="bio"
                rows={3}
                value={formData.bio}
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-xl border border-gray-200 text-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all resize-none bg-white"
              />
            </div>
          </div>

          <div className="pt-4 border-t border-gray-100">
            <label className="block text-sm font-semibold text-gray-700 mb-2">Profile Photo</label>
            
            {/* Functional Upload Box with Hidden File Input */}
            <label className="border-2 border-dashed border-blue-200 rounded-2xl p-6 text-center bg-blue-50/20 hover:bg-blue-50/40 cursor-pointer transition-colors block">
              <input 
                type="file" 
                accept="image/png, image/jpeg" 
                onChange={handleImageChange} 
                className="hidden" 
              />
              <div className="flex flex-col items-center justify-center gap-2">
                <div className="w-10 h-10 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center shadow-sm">
                  <Upload className="w-5 h-5" />
                </div>
                <p className="text-sm font-medium text-gray-700">
                  <span className="text-blue-600 font-semibold">Click to upload</span> or drag and drop
                </p>
                <p className="text-xs text-gray-400">Supports JPG, PNG (Max 5MB)</p>
              </div>
            </label>
          </div>
        </div>

        {/* Form Actions */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center justify-end gap-4">
          <button
            type="button"
            onClick={handleDiscard}
            className="px-6 py-2.5 rounded-xl text-sm font-medium text-gray-700 bg-white border border-gray-200 hover:bg-gray-50 transition-colors cursor-pointer"
          >
            Discard
          </button>
          <button
            type="submit"
            className="px-6 py-2.5 rounded-xl text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 shadow-md shadow-blue-600/20 transition-colors cursor-pointer"
          >
            Save
          </button>
        </div>
      </form>
    </div>
  );
};

export default Profile;