import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

import { authService } from '../../api/services/auth.service';
import { Mail, Lock, User, Loader2, ArrowRight, Eye, EyeOff, Sparkles, Paintbrush } from 'lucide-react';
import { createUserWithEmailAndPassword, signInWithPopup } from 'firebase/auth';
import { auth, googleProvider } from '../../config/firebase';
import Navbar from '../../components/layout/Navbar';

export default function Register() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    role: 'CLIENT'
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  
  const { fetchUser } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const setRole = (role: 'CLIENT' | 'DESIGNER') => {
    setFormData({ ...formData, role });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      if (!formData.full_name.trim() || !formData.email.trim() || !formData.password.trim()) {
        throw new Error("Please fill in all required fields.");
      }
      if (formData.password.length < 6) {
        throw new Error("Password must be at least 6 characters long.");
      }

      // Create user with Firebase Auth first
      await createUserWithEmailAndPassword(auth, formData.email, formData.password);
      
      // After Firebase is created, the backend MUST be notified to store the profile and role
      try {
        await authService.register(formData);
        await fetchUser(); // Populate context with the newly created profile
      } catch (backendError) {
        console.error("Backend registration failed", backendError);
        // The user is authenticated in Firebase but the backend failed to create a profile.
        // In a real app we might want to delete the Firebase user here to keep consistency.
      }
      
      navigate('/');
    } catch (err: any) {
      if (err.code === 'auth/email-already-in-use') {
         setError("This email is already in use. Please try logging in.");
      } else {
         setError(err.message || 'Failed to register. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleRegister = async () => {
    setError('');
    setIsGoogleLoading(true);
    try {
      const result = await signInWithPopup(auth, googleProvider);
      
      // Since Google sets auth.currentUser, apiClient will attach the token.
      // We just need to tell the backend to ensure the profile exists.
      const registerData = {
        email: result.user.email || '',
        full_name: result.user.displayName || result.user.email?.split('@')[0] || 'User',
        role: formData.role
      };
      
      const response = await authService.register(registerData);
      await fetchUser(); // Populate context
      
      if (response.data.role === 'ADMIN') {
        navigate('/admin', { replace: true });
      } else {
        navigate('/', { replace: true });
      }
    } catch (err: any) {
      if (err.code === 'auth/popup-closed-by-user') {
        return; // Ignore
      }
      setError(err.message || 'Google sign-up failed. Please try again.');
    } finally {
      setIsGoogleLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-100 via-fuchsia-100 to-indigo-100 flex flex-col relative overflow-hidden font-sans text-slate-900">
      <Navbar />

      <main className="flex-1 flex items-center justify-center px-6 py-32 z-10">
        <div className="max-w-[480px] w-full">
          
          <div className="mb-8 text-center">
            <h1 className="text-4xl md:text-5xl font-display font-black tracking-tight text-slate-900 uppercase mb-3 drop-shadow-sm">
              Let's Play
            </h1>
            <p className="text-slate-700 font-medium text-sm md:text-base">
              Create your Lynvia account and start creating magic.
            </p>
          </div>

          <div className="bg-white/80 backdrop-blur-xl p-8 md:p-10 rounded-3xl border border-white/40 shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
            {error && (
              <div className="mb-6 p-4 rounded-2xl bg-red-50 border border-red-100 text-red-600 text-sm text-center font-medium">
                {error}
              </div>
            )}
            
            <div className="space-y-6">
              
              {/* Custom Playful Role Selector */}
              <div className="space-y-2">
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
                  I want to...
                </label>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    type="button"
                    onClick={() => setRole('CLIENT')}
                    className={`relative p-5 rounded-2xl border-2 text-left transition-all duration-300 hover:-translate-y-1 ${
                      formData.role === 'CLIENT' 
                        ? 'border-emerald-400 bg-emerald-50 shadow-[0_4px_20px_rgba(52,211,153,0.3)]' 
                        : 'border-slate-200 bg-white hover:border-emerald-200'
                    }`}
                  >
                    <Sparkles className={`h-7 w-7 mb-3 ${formData.role === 'CLIENT' ? 'text-emerald-500' : 'text-slate-400'}`} />
                    <h3 className={`font-bold text-sm ${formData.role === 'CLIENT' ? 'text-emerald-700' : 'text-slate-700'}`}>Hire Talent</h3>
                    <p className={`text-xs mt-1 line-clamp-2 ${formData.role === 'CLIENT' ? 'text-emerald-600' : 'text-slate-500'}`}>Post projects and find top creatives.</p>
                  </button>
                  
                  <button
                    type="button"
                    onClick={() => setRole('DESIGNER')}
                    className={`relative p-5 rounded-2xl border-2 text-left transition-all duration-300 hover:-translate-y-1 ${
                      formData.role === 'DESIGNER' 
                        ? 'border-rose-400 bg-rose-50 shadow-[0_4px_20px_rgba(251,113,133,0.3)]' 
                        : 'border-slate-200 bg-white hover:border-rose-200'
                    }`}
                  >
                    <Paintbrush className={`h-7 w-7 mb-3 ${formData.role === 'DESIGNER' ? 'text-rose-500' : 'text-slate-400'}`} />
                    <h3 className={`font-bold text-sm ${formData.role === 'DESIGNER' ? 'text-rose-700' : 'text-slate-700'}`}>Work as Designer</h3>
                    <p className={`text-xs mt-1 line-clamp-2 ${formData.role === 'DESIGNER' ? 'text-rose-600' : 'text-slate-500'}`}>Showcase work and get hired.</p>
                  </button>
                </div>
              </div>

              <button
                type="button"
                onClick={handleGoogleRegister}
                disabled={isGoogleLoading || isLoading}
                className="w-full flex justify-center items-center py-4 px-4 bg-white hover:bg-slate-50 border border-slate-200 rounded-2xl shadow-sm text-sm font-bold text-slate-700 transition-all duration-300 disabled:opacity-70 disabled:cursor-not-allowed hover:-translate-y-0.5"
              >
                {isGoogleLoading ? (
                  <Loader2 className="animate-spin h-5 w-5" />
                ) : (
                  <>
                    <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
                      <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                      <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                      <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                      <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                    </svg>
                    Sign up with Google
                  </>
                )}
              </button>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-slate-200"></div>
                </div>
                <div className="relative flex justify-center text-xs">
                  <span className="bg-white/80 px-3 text-slate-500 uppercase tracking-wider font-bold rounded-full">
                    Or sign up with email
                  </span>
                </div>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="pt-2 space-y-5">
                  <div className="space-y-1">
                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                      Full Name
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <User className="h-4 w-4 text-slate-400" />
                      </div>
                      <input
                        type="text"
                        name="full_name"
                        required
                        value={formData.full_name}
                        onChange={handleChange}
                        className="block w-full pl-11 pr-4 py-4 bg-white/70 border border-slate-200 rounded-2xl text-slate-800 placeholder-slate-400 focus:outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-400/20 transition-all font-medium sm:text-sm"
                        placeholder="e.g. Jane Doe"
                      />
                    </div>
                  </div>

                  <div className="space-y-1">
                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                      Email
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Mail className="h-4 w-4 text-slate-400" />
                      </div>
                      <input
                        type="email"
                        name="email"
                        required
                        value={formData.email}
                        onChange={handleChange}
                        className="block w-full pl-11 pr-4 py-4 bg-white/70 border border-slate-200 rounded-2xl text-slate-800 placeholder-slate-400 focus:outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-400/20 transition-all font-medium sm:text-sm"
                        placeholder="Enter your email"
                      />
                    </div>
                  </div>

                  <div className="space-y-1">
                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                      Password
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Lock className="h-4 w-4 text-slate-400" />
                      </div>
                      <input
                        type={showPassword ? "text" : "password"}
                        name="password"
                        required
                        value={formData.password}
                        onChange={handleChange}
                        className="block w-full pl-11 pr-12 py-4 bg-white/70 border border-slate-200 rounded-2xl text-slate-800 placeholder-slate-400 focus:outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-400/20 transition-all font-medium sm:text-sm"
                        placeholder="Create a strong password"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-400 hover:text-slate-600 transition-colors focus:outline-none"
                      >
                        {showPassword ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>

                <div className="pt-2">
                  <button
                    type="submit"
                    disabled={isLoading || isGoogleLoading}
                    className="group w-full flex justify-center items-center py-4 px-4 border border-transparent rounded-2xl shadow-lg shadow-violet-500/25 text-sm font-bold text-white bg-gradient-to-r from-violet-500 to-fuchsia-500 hover:from-violet-600 hover:to-fuchsia-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-white focus:ring-violet-500 transition-all duration-300 disabled:opacity-70 disabled:cursor-not-allowed hover:-translate-y-0.5"
                  >
                    {isLoading ? (
                      <Loader2 className="animate-spin h-5 w-5" />
                    ) : (
                      <>
                        Create Account
                        <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>

            <div className="mt-8 text-center">
              <p className="text-sm font-medium text-slate-500">
                Already have an account?{' '}
                <Link to="/login" className="font-bold text-violet-600 hover:text-violet-700 transition-colors">
                  Sign in
                </Link>
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
