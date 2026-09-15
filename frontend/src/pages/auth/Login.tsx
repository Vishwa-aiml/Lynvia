import React, { useState } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { authService } from '../../api/services/auth.service';
import { Mail, Lock, Loader2, ArrowRight, Eye, EyeOff } from 'lucide-react';
import { signInWithPopup, signInWithEmailAndPassword, sendPasswordResetEmail } from 'firebase/auth';
import { auth, googleProvider } from '../../config/firebase';
import Navbar from '../../components/layout/Navbar';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [isForgotPassword, setIsForgotPassword] = useState(false);
  
  const { } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/workspace';

  const navigateBasedOnRole = () => {
    if (location.state?.from?.pathname) {
      navigate(from, { replace: true });
    } else {
      navigate('/', { replace: true });
    }
  };

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      if (!email.trim() || !password.trim()) {
        throw new Error("Please enter both email and password.");
      }
      
      // Use native Firebase authentication
      await signInWithEmailAndPassword(auth, email, password);
      
      // Wait for auth context to update and fetch the user profile from the backend
      // In a real flow, you might wait for the auth state listener to resolve.
      // We will redirect directly. The ProtectedRoute will handle any missing roles.
      navigateBasedOnRole();
    } catch (err: any) {
      if (err.code === 'auth/user-not-found' || err.code === 'auth/wrong-password' || err.code === 'auth/invalid-credential') {
        setError("Incorrect email or password.");
      } else {
        setError(err.message || 'Something went wrong. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setError('');
    setIsGoogleLoading(true);
    try {
      const result = await signInWithPopup(auth, googleProvider);
      // Still call our backend to ensure they have a profile created if it's their first time.
      const registerData = {
        email: result.user.email || '',
        full_name: result.user.displayName || result.user.email?.split('@')[0] || 'User',
        role: 'CLIENT' // Default to CLIENT if they sign up via Login page. They can change later if needed or we could prompt.
      };
      await authService.register(registerData);
      navigateBasedOnRole();
    } catch (err: any) {
      if (err.code === 'auth/popup-closed-by-user') {
        return;
      }
      setError(err.message || 'Google sign-in failed. Please try again.');
    } finally {
      setIsGoogleLoading(false);
    }
  };

  const handleForgotPasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');
    setIsLoading(true);

    try {
      if (!email.trim()) {
        throw new Error("Please enter a valid email address.");
      }
      
      // Use Firebase native password reset
      await sendPasswordResetEmail(auth, email);
      setSuccessMsg("If an account exists, a recovery link has been sent to your email.");
      setTimeout(() => {
        setIsForgotPassword(false);
        setSuccessMsg('');
      }, 5000);
    } catch (err: any) {
      setError(err.message || 'Failed to send recovery email. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0D0D0F] flex flex-col relative overflow-hidden font-sans">
      <Navbar />

      {/* Playful Colorful Background Gradients */}
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-gradient-to-br from-pink-500/20 to-purple-500/20 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-gradient-to-tr from-blue-500/20 to-teal-500/20 rounded-full blur-[100px] pointer-events-none" />

      <main className="flex-1 flex items-center justify-center px-6 py-32 z-10">
        <div className="max-w-[440px] w-full">
          
          <div className="mb-10 text-center">
            <h1 className="text-4xl md:text-5xl font-display font-black tracking-tight text-[#F5F5F5] uppercase mb-3">
              {isForgotPassword ? "Recover Account" : "Welcome to Lynvia"}
            </h1>
            <p className="text-[#9A9AA3] text-sm md:text-base">
              {isForgotPassword 
                ? "Enter your email to receive a recovery code." 
                : "Sign in to continue to Lynvia."}
            </p>
          </div>

          <div className="bg-[#15151A] p-8 md:p-10 rounded-xl border border-[#2A2A32] shadow-2xl">
            {error && (
              <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm text-center">
                {error}
              </div>
            )}
            
            {successMsg && (
              <div className="mb-6 p-4 rounded-lg bg-green-500/10 border border-green-500/20 text-green-400 text-sm text-center">
                {successMsg}
              </div>
            )}

            {!isForgotPassword ? (
              <div className="space-y-6">
                <button
                  type="button"
                  onClick={handleGoogleLogin}
                  disabled={isGoogleLoading || isLoading}
                  className="w-full flex justify-center items-center py-3.5 px-4 bg-white hover:bg-gray-100 rounded-lg text-sm font-bold text-black transition-colors disabled:opacity-70 disabled:cursor-not-allowed"
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
                      Continue with Google
                    </>
                  )}
                </button>

                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-[#2A2A32]"></div>
                  </div>
                  <div className="relative flex justify-center text-xs">
                    <span className="bg-[#15151A] px-3 text-[#9A9AA3] uppercase tracking-wider">
                      Or continue with email
                    </span>
                  </div>
                </div>

                <form onSubmit={handleLoginSubmit} className="space-y-6">
                  <div className="space-y-1">
                    <label className="block text-xs font-medium text-[#9A9AA3] uppercase tracking-wider mb-2">
                      Email
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Mail className="h-4 w-4 text-[#9A9AA3]" />
                      </div>
                      <input
                        type="email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="block w-full pl-11 pr-4 py-3.5 bg-[#0D0D0F] border border-[#2A2A32] rounded-lg text-[#F5F5F5] placeholder-[#9A9AA3]/50 focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-colors sm:text-sm"
                        placeholder="Enter your email"
                      />
                    </div>
                  </div>

                  <div className="space-y-1">
                    <div className="flex justify-between items-center mb-2">
                      <label className="block text-xs font-medium text-[#9A9AA3] uppercase tracking-wider">
                        Password
                      </label>
                      <button
                        type="button"
                        onClick={() => setIsForgotPassword(true)}
                        className="text-xs text-accent hover:text-white transition-colors"
                      >
                        Forgot password?
                      </button>
                    </div>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Lock className="h-4 w-4 text-[#9A9AA3]" />
                      </div>
                      <input
                        type={showPassword ? "text" : "password"}
                        required
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="block w-full pl-11 pr-12 py-3.5 bg-[#0D0D0F] border border-[#2A2A32] rounded-lg text-[#F5F5F5] placeholder-[#9A9AA3]/50 focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-colors sm:text-sm"
                        placeholder="Enter your password"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute inset-y-0 right-0 pr-4 flex items-center text-[#9A9AA3] hover:text-[#F5F5F5] transition-colors focus:outline-none"
                      >
                        {showPassword ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={isLoading || isGoogleLoading}
                    className="w-full flex justify-center items-center py-4 px-4 border border-transparent rounded-lg shadow-sm text-sm font-bold text-white bg-accent hover:bg-accent/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#0D0D0F] focus:ring-accent transition-all disabled:opacity-70 disabled:cursor-not-allowed"
                  >
                    {isLoading ? (
                      <Loader2 className="animate-spin h-5 w-5" />
                    ) : (
                      <>
                        Sign In
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </>
                    )}
                  </button>
                </form>
              </div>
            ) : (
              <form onSubmit={handleForgotPasswordSubmit} className="space-y-6">
                <div className="space-y-1">
                  <label className="block text-xs font-medium text-[#9A9AA3] uppercase tracking-wider mb-2">
                    Email
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <Mail className="h-4 w-4 text-[#9A9AA3]" />
                    </div>
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="block w-full pl-11 pr-4 py-3.5 bg-[#0D0D0F] border border-[#2A2A32] rounded-lg text-[#F5F5F5] placeholder-[#9A9AA3]/50 focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-colors sm:text-sm"
                      placeholder="Enter your email"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full flex justify-center items-center py-4 px-4 border border-transparent rounded-lg shadow-sm text-sm font-bold text-white bg-accent hover:bg-accent/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#0D0D0F] focus:ring-accent transition-all disabled:opacity-70 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <Loader2 className="animate-spin h-5 w-5" />
                  ) : (
                    "Send Recovery Code"
                  )}
                </button>

                <div className="text-center mt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setIsForgotPassword(false);
                      setError('');
                      setSuccessMsg('');
                    }}
                    className="text-sm text-[#9A9AA3] hover:text-[#F5F5F5] transition-colors"
                  >
                    Back to login
                  </button>
                </div>
              </form>
            )}

            {!isForgotPassword && (
              <div className="mt-8 text-center border-t border-[#2A2A32] pt-8">
                <p className="text-sm text-[#9A9AA3]">
                  Don't have an account?{' '}
                  <Link to="/register" className="font-medium text-[#F5F5F5] hover:text-accent transition-colors">
                    Create an account
                  </Link>
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
