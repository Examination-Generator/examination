import { useState } from 'react';
import * as authService from '../services/authService';
import ForgotPassword from './ForgotPassword';

export default function Login({ onSwitchToSignup, onLoginSuccess }){
    const [isEditor, setIsEditor] = useState(false);
    const [phoneNumber, setPhoneNumber] = useState('');
    const [password, setPassword] = useState('');
    const [rememberMe, setRememberMe] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [showForgotPassword, setShowForgotPassword] = useState(false);
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);
        
        try {
            // Validate inputs
            if (!phoneNumber.trim()) {
                throw new Error('Please enter your phone number');
            }
            if (!password.trim()) {
                throw new Error('Please enter your password');
            }
            
            // Call login API
            const response = await authService.login(phoneNumber, password);
            
            // Check if user role matches selected role
            if (isEditor && response.user.role !== 'editor' && response.user.role !== 'admin') {
                throw new Error('You do not have editor permissions. Please uncheck "Login as Editor" or contact an administrator.');
            }
            
            // Store remember me preference
            if (rememberMe) {
                localStorage.setItem('rememberMe', 'true');
                localStorage.setItem('rememberedPhone', phoneNumber);
            } else {
                localStorage.removeItem('rememberMe');
                localStorage.removeItem('rememberedPhone');
            }
            
            console.log('Login successful:', response.user);
            
            // Determine role based on checkbox and actual user role
            const role = isEditor ? 'editor' : 'user';
            onLoginSuccess(role);
        } catch (error) {
            console.error('Login error:', error);
            setError(error.message || 'Login failed. Please check your credentials and try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return(
        <>
        <div className="min-h-screen flex items-center justify-center p-4">
            <div className="w-full max-w-5xl bg-white">
                {/* Mobile/Small Screen Layout - Logo on top */}
                <div className="lg:hidden bg-white rounded-xl shadow-2xl p-8">
                    <div className="flex flex-col items-center mb-8">
                        <img 
                            src="/exam.png" 
                            alt="Exam Logo" 
                            className="w-32 h-32 object-contain mb-6"
                        />
                        <h2 className="text-3xl font-bold text-green-600 mb-2">Login</h2>
                        <p className="text-gray-600 text-center">Welcome back! Please login to your account.</p>
                    </div>
                    
                    <form onSubmit={handleSubmit}>
                        {error && (
                            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                                <p className="text-sm">{error}</p>
                            </div>
                        )}
                        <div className="mb-4">
                            <label className="flex items-center cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={isEditor}
                                    onChange={(e) => setIsEditor(e.target.checked)}
                                    className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                                />
                                <span className="ml-2 text-sm text-gray-700 font-medium">
                                    Login as Editor (Question Entry)
                                </span>
                            </label>
                            <p className="text-xs text-gray-500 mt-1 ml-6">
                                {isEditor ? 'You will access the Question Entry Dashboard' : 'You will access the Exam Generation Dashboard'}
                            </p>
                        </div>
                        <div className="mb-4">
                            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="phone-mobile">
                                Phone Number
                            </label>
                            <input
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                id="phone-mobile"
                                type="tel"
                                placeholder="+254-73-456-7890"
                                value={phoneNumber}
                                onChange={(e) => setPhoneNumber(e.target.value)}
                                required
                            />
                        </div>
                        <div className="mb-6">
                            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password-mobile">
                                Password (4 digits)
                            </label>
                            <input
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                id="password-mobile"
                                type="password"
                                placeholder="****"
                                maxLength="4"
                                value={password}
                                onChange={(e) => setPassword(e.target.value.replace(/\D/g, ''))}
                                required
                            />
                        </div>
                        <div className="flex items-center justify-between mb-6">
                            <label className="flex items-center cursor-pointer">
                                <input 
                                    type="checkbox" 
                                    className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                                    checked={rememberMe}
                                    onChange={(e) => setRememberMe(e.target.checked)}
                                />
                                <span className="ml-2 text-sm text-gray-600">Remember me</span>
                            </label>
                            <button
                                type="button"
                                onClick={() => setShowForgotPassword(true)}
                                className="text-sm text-green-600 hover:text-green-700 font-medium"
                            >
                                Forgot password?
                            </button>
                        </div>
                        <button
                            className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 shadow-md hover:shadow-lg disabled:bg-gray-400 disabled:cursor-not-allowed"
                            type="submit"
                            disabled={isLoading}
                        >
                            {isLoading ? (
                                <span className="flex items-center justify-center">
                                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Logging in...
                                </span>
                            ) : (
                                'Login'
                            )}
                        </button>
                    </form>
                    <div className="mt-6 text-center">
                        <p className="text-gray-600 text-sm">
                            Don't have an account?{' '}
                            <button 
                                onClick={onSwitchToSignup}
                                className="text-green-600 hover:text-green-700 font-medium"
                            >
                                Sign up
                            </button>
                        </p>
                    </div>
                </div>

                {/* Large Screen Layout - Logo side by side with form */}
                <div className="hidden lg:flex bg-white rounded-xl shadow-2xl overflow-hidden">
                    {/* Left Side - Logo */}
                    <div className="w-1/2 bg-gradient-to-br from-white to-white p-12 flex flex-col items-center justify-center">
                        <img 
                            src="/exam.png" 
                            alt="Exam Logo" 
                            className="w-64 h-64 object-contain mb-8"
                        />
                        <h2 className="text-4xl font-bold text-green-700 text-center mb-4">Exam App</h2>
                        <p className="text-green-600 text-center text-lg italic">
                            Test your students with quality examinations
                        </p>
                    </div>
                    
                    {/* Right Side - Login Form */}
                    <div className="w-1/2 p-12">
                        <div className="mb-8">
                            <h2 className="text-3xl font-bold text-green-600 mb-2">Login</h2>
                            <p className="text-gray-600">Welcome back! Please login to your account.</p>
                        </div>
                        
                        <form onSubmit={handleSubmit}>
                            {error && (
                                <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                                    <p className="text-sm">{error}</p>
                                </div>
                            )}
                            <div className="mb-4">
                                <label className="flex items-center cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={isEditor}
                                        onChange={(e) => setIsEditor(e.target.checked)}
                                        className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                                    />
                                    <span className="ml-2 text-sm text-gray-700 font-medium">
                                        Login as Editor (Question Entry)
                                    </span>
                                </label>
                                <p className="text-xs text-gray-500 mt-1 ml-6">
                                    {isEditor ? 'You will access the Question Entry Dashboard' : 'You will access the Exam Generation Dashboard'}
                                </p>
                            </div>
                            <div className="mb-4">
                                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="phone-desktop">
                                    Phone Number
                                </label>
                                <input
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                    id="phone-desktop"
                                    type="tel"
                                    placeholder="+254-73-456-7890"
                                    value={phoneNumber}
                                    onChange={(e) => setPhoneNumber(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="mb-6">
                                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password-desktop">
                                    Password (4 digits)
                                </label>
                                <input
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                    id="password-desktop"
                                    type="password"
                                    placeholder="****"
                                    maxLength="4"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value.replace(/\D/g, ''))}
                                    required
                                />
                            </div>
                            <div className="flex items-center justify-between mb-6">
                                <label className="flex items-center">
                                    <input 
                                        type="checkbox" 
                                        className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                                        checked={rememberMe}
                                        onChange={(e) => setRememberMe(e.target.checked)}
                                    />
                                    <span className="ml-2 text-sm text-gray-600">Remember me</span>
                                </label>
                                <button
                                    type="button"
                                    onClick={() => setShowForgotPassword(true)}
                                    className="text-sm text-green-600 hover:text-green-700 font-medium"
                                >
                                    Forgot password?
                                </button>
                            </div>
                            <button
                                className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 shadow-md hover:shadow-lg disabled:bg-gray-400 disabled:cursor-not-allowed"
                                type="submit"
                                disabled={isLoading}
                            >
                                {isLoading ? (
                                    <span className="flex items-center justify-center">
                                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Logging in...
                                    </span>
                                ) : (
                                    'Login'
                                )}
                            </button>
                        </form>
                        <div className="mt-6 text-center">
                            <p className="text-gray-600 text-sm">
                                Don't have an account?{' '}
                                <button 
                                    onClick={onSwitchToSignup}
                                    className="text-green-600 hover:text-green-700 font-medium"
                                >
                                    Sign up
                                </button>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        {/* Forgot Password Modal */}
        {showForgotPassword && (
            <ForgotPassword
                onClose={() => setShowForgotPassword(false)}
                onSuccess={() => {
                    // Optionally show a success message on login page
                    setError('');
                }}
            />
        )}
        </>
    );
}