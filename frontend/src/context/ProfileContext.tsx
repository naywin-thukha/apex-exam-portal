import React, { createContext, useContext, useState, useEffect } from 'react';

interface ProfileContextType {
  name: string;
  email: string;
  phone: string;
  bio: string;
  avatar: string;
  updateProfile: (data: { name: string; email: string; phone: string; bio: string; avatar: string }) => void;
}

const ProfileContext = createContext<ProfileContextType | undefined>(undefined);

export const ProfileProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [profile, setProfile] = useState(() => {
    const saved = localStorage.getItem('apex_admin_profile');
    if (saved) {
      try { return JSON.parse(saved); } catch (e) { /* fallback */ }
    }
    return {
      name: 'Ms. Sarah Johnson',
      email: 'sarah.johnson@apex.edu.mm',
      phone: '+95 9 123 456 789',
      bio: 'Super Admin at APEX Education Center. Passionate about education and student success.',
      avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150',
    };
  });

  useEffect(() => {
    localStorage.setItem('apex_admin_profile', JSON.stringify(profile));
  }, [profile]);

  const updateProfile = (data: { name: string; email: string; phone: string; bio: string; avatar: string }) => {
    setProfile(data);
  };

  return (
    <ProfileContext.Provider value={{ ...profile, updateProfile }}>
      {children}
    </ProfileContext.Provider>
  );
};

export const useProfile = () => {
  const context = useContext(ProfileContext);
  if (!context) throw new Error('useProfile must be used within a ProfileProvider');
  return context;
};