import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Lock, Eye, EyeOff } from 'lucide-react';

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Role-based routing logic
    if (username.toLowerCase().includes('student')) {
      navigate('/student/dashboard');
    } else if (username.toLowerCase().includes('admin')) {
      navigate('/admin/dashboard');
    } else {
      navigate('/teacher/dashboard');
    }
  };

  return (
    <div className="min-h-screen w-full flex flex-col md:flex-row bg-[#F0F5FA]">
      {/* Left Brand & Slogan Banner */}
      <div className="md:w-5/12 bg-[#0B2545] p-8 md:p-14 text-white flex flex-col justify-between relative overflow-hidden min-h-[280px] md:min-h-screen">
        {/* Logo */}
        <div className="flex items-center gap-2 z-10">
          <span className="text-amber-400 font-extrabold text-3xl tracking-tighter">▲</span>
          <div className="flex flex-col">
            <span className="text-white font-black text-2xl tracking-wider leading-none">PEX</span>
            <span className="text-[9px] text-blue-200 tracking-widest font-bold uppercase">Education Center</span>
          </div>
        </div>

        {/* Slogan Copy */}
        <div className="my-auto z-10 max-w-sm pt-8 md:pt-0">
          <h1 className="text-3xl md:text-4xl font-extrabold leading-tight mb-3">
            Learn. Grow. Achieve.
          </h1>
          <p className="text-blue-200/80 text-sm leading-relaxed">
            Your trusted education partner for a brighter future.
          </p>
        </div>

        {/* Decorative background overlay */}
        <div className="absolute right-0 bottom-0 top-0 w-20 bg-[#F0F5FA] rounded-l-full transform translate-x-10 hidden md:block opacity-10" />
      </div>

      {/* Right Login Form Section */}
      <div className="md:w-7/12 flex items-center justify-center p-6 md:p-12">
        <div className="bg-white rounded-3xl shadow-xl shadow-blue-900/5 max-w-md w-full p-8 md:p-10 border border-gray-100">
          {/* Header */}
          <div className="text-center mb-8">
            <h2 className="text-2xl font-extrabold text-[#0B2545] tracking-tight">Welcome Back</h2>
            <p className="text-gray-400 text-xs mt-1">Log in to your account</p>
          </div>

          {/* Form */}
          <form onSubmit={handleLogin} className="space-y-4">
            {/* Username Field */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1.5">Username</label>
              <div className="relative">
                <User className="w-4 h-4 text-gray-400 absolute left-4 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Enter your username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-11 pr-4 py-3 bg-gray-50/50 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all text-gray-800 placeholder-gray-400"
                  required
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1.5">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-gray-400 absolute left-4 top-1/2 -translate-y-1/2" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-11 pr-11 py-3 bg-gray-50/50 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all text-gray-800 placeholder-gray-400"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 cursor-pointer"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Remember Me Checkbox */}
            <div className="flex items-center text-xs pt-1">
              <label className="flex items-center gap-2 cursor-pointer text-gray-600 font-medium select-none">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                />
                Remember me
              </label>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              className="w-full py-3.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold text-sm transition-all shadow-md shadow-blue-600/25 cursor-pointer mt-3 flex items-center justify-center gap-2"
            >
              Log In &rarr;
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;