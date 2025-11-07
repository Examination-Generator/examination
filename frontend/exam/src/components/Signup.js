import { useState } from 'react';
import * as authService from '../services/authService';

export default function Signup({ onSwitchToLogin }) {
    const [step, setStep] = useState(1); // 1: Phone & Name, 2: OTP, 3: Password
    const [formData, setFormData] = useState({
        name: '',
        phone: '',
        otp: '',
        password: '',
        confirmPassword: ''
    });
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState('');

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
        setError(''); // Clear error when user types
    };

    const handlePhoneSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccessMessage('');
        setIsLoading(true);
        
        try {
            // Validate inputs
            if (!formData.name.trim()) {
                throw new Error('Please enter your full name');
            }
            if (!formData.phone.trim()) {
                throw new Error('Please enter your phone number');
            }
            
            // Request OTP
            const response = await authService.requestOTP(formData.phone, formData.name);
            console.log('OTP requested:', response);
            setSuccessMessage(response.message || 'OTP sent successfully!');
            setStep(2);
        } catch (error) {
            console.error('Error requesting OTP:', error);
            setError(error.message || 'Failed to send OTP. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleOtpSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccessMessage('');
        setIsLoading(true);
        
        try {
            // Validate OTP
            if (!formData.otp.trim() || formData.otp.length !== 6) {
                throw new Error('Please enter a valid 6-digit OTP');
            }
            
            // Verify OTP
            const response = await authService.verifyOTP(formData.phone, formData.otp);
            console.log('OTP verified:', response);
            setSuccessMessage('OTP verified successfully!');
            setTimeout(() => {
                setStep(3);
                setSuccessMessage('');
            }, 1000);
        } catch (error) {
            console.error('Error verifying OTP:', error);
            setError(error.message || 'Invalid OTP. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const handlePasswordSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccessMessage('');
        setIsLoading(true);
        
        try {
            // Validate password
            if (!formData.password || formData.password.length !== 4) {
                throw new Error('Please enter a 4-digit PIN');
            }
            if (formData.password !== formData.confirmPassword) {
                throw new Error('PINs do not match');
            }
            if (!/^\d{4}$/.test(formData.password)) {
                throw new Error('PIN must be 4 digits');
            }
            
            // Register user
            const response = await authService.register(
                formData.phone,
                formData.name,
                formData.password,
                'user' // Default role is 'user', admin can change to 'editor' later
            );
            
            console.log('Registration successful:', response);
            setSuccessMessage('Registration successful! Redirecting to login...');
            
            // Redirect to login after 2 seconds
            setTimeout(() => {
                onSwitchToLogin();
            }, 2000);
        } catch (error) {
            console.error('Error registering:', error);
            setError(error.message || 'Registration failed. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };
    
    const handleResendOTP = async () => {
        setError('');
        setSuccessMessage('');
        setIsLoading(true);
        
        try {
            const response = await authService.requestOTP(formData.phone, formData.name);
            console.log('OTP resent:', response);
            setSuccessMessage('OTP resent successfully!');
        } catch (error) {
            console.error('Error resending OTP:', error);
            setError(error.message || 'Failed to resend OTP. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <>
            <div className="min-h-screen bg-gradient-to-br from-white to-white flex items-center justify-center p-4">
                <div className="w-full max-w-5xl">
                    {/* Mobile/Small Screen Layout - Logo on top */}
                    <div className="lg:hidden bg-white rounded-xl shadow-2xl p-8">
                        <div className="flex flex-col items-center mb-8">
                            <img 
                                src="/exam.png" 
                                alt="Exam Logo" 
                                className="w-32 h-32 object-contain mb-6"
                            />
                            <h2 className="text-3xl font-bold text-green-600 mb-2">Sign Up</h2>
                            <p className="text-gray-600 text-center">Create your account to get started</p>
                        </div>

                        {/* Progress Indicator */}
                        <div className="flex justify-center mb-8">
                            <div className="flex items-center space-x-2">
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 1 ? 'bg-green-600 text-white' : 'bg-gray-300 text-gray-600'}`}>
                                    1
                                </div>
                                <div className={`w-12 h-1 ${step >= 2 ? 'bg-green-600' : 'bg-gray-300'}`}></div>
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 2 ? 'bg-green-600 text-white' : 'bg-gray-300 text-gray-600'}`}>
                                    2
                                </div>
                                <div className={`w-12 h-1 ${step >= 3 ? 'bg-green-600' : 'bg-gray-300'}`}></div>
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 3 ? 'bg-green-600 text-white' : 'bg-gray-300 text-gray-600'}`}>
                                    3
                                </div>
                            </div>
                        </div>

                        {/* Step 1: Phone & Name */}
                        {step === 1 && (
                            <form onSubmit={handlePhoneSubmit}>
                                {error && (
                                    <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                                        <p className="text-sm">{error}</p>
                                    </div>
                                )}
                                {successMessage && (
                                    <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
                                        <p className="text-sm">{successMessage}</p>
                                    </div>
                                )}
                                <div className="mb-4">
                                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="name-mobile">
                                        Full Name
                                    </label>
                                    <input
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                        id="name-mobile"
                                        name="name"
                                        type="text"
                                        placeholder="Enter your full name"
                                        value={formData.name}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>
                                <div className="mb-6">
                                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="phone-mobile">
                                        Phone Number
                                    </label>
                                    <input
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                        id="phone-mobile"
                                        name="phone"
                                        type="tel"
                                        placeholder="+254-73-456-7890"
                                        value={formData.phone}
                                        onChange={handleChange}
                                        required
                                    />
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
                                            Sending OTP...
                                        </span>
                                    ) : (
                                        'Send OTP'
                                    )}
                                </button>
                            </form>
                        )}

                        {/* Step 2: OTP Verification */}
                        {step === 2 && (
                            <form onSubmit={handleOtpSubmit}>
                                {error && (
                                    <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                                        <p className="text-sm">{error}</p>
                                    </div>
                                )}
                                {successMessage && (
                                    <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
                                        <p className="text-sm">{successMessage}</p>
                                    </div>
                                )}
                                <div className="text-center mb-6">
                                    <p className="text-gray-600 text-sm">
                                        We've sent a verification code to
                                    </p>
                                    <p className="text-green-600 font-semibold">{formData.phone}</p>
                                </div>
                                <div className="mb-6">
                                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="otp-mobile">
                                        Enter OTP
                                    </label>
                                    <input
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition text-center text-2xl tracking-widest"
                                        id="otp-mobile"
                                        name="otp"
                                        type="text"
                                        placeholder="- - - - - -"
                                        maxLength="6"
                                        value={formData.otp}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>
                                <button
                                    className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 shadow-md hover:shadow-lg mb-4 disabled:bg-gray-400 disabled:cursor-not-allowed"
                                    type="submit"
                                    disabled={isLoading}
                                >
                                    {isLoading ? (
                                        <span className="flex items-center justify-center">
                                            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                            </svg>
                                            Verifying...
                                        </span>
                                    ) : (
                                        'Verify OTP'
                                    )}
                                </button>
                                <button
                                    className="w-full text-green-600 hover:text-green-700 font-medium text-sm disabled:text-gray-400"
                                    type="button"
                                    onClick={handleResendOTP}
                                    disabled={isLoading}
                                >
                                    Resend OTP
                                </button>
                            </form>
                        )}

                        {/* Step 3: Set Password */}
                        {step === 3 && (
                            <form onSubmit={handlePasswordSubmit}>
                                {error && (
                                    <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                                        <p className="text-sm">{error}</p>
                                    </div>
                                )}
                                {successMessage && (
                                    <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
                                        <p className="text-sm">{successMessage}</p>
                                    </div>
                                )}
                                <div className="text-center mb-6">
                                    <p className="text-gray-600 text-sm">
                                        Set a 4-digit PIN to secure your account
                                    </p>
                                </div>
                                <div className="mb-4">
                                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password-mobile">
                                        4-Digit PIN
                                    </label>
                                    <input
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition text-center text-2xl tracking-widest"
                                        id="password-mobile"
                                        name="password"
                                        type="password"
                                        placeholder="• • • •"
                                        maxLength="4"
                                        pattern="\d{4}"
                                        value={formData.password}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>
                                <div className="mb-6">
                                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="confirm-password-mobile">
                                        Confirm PIN
                                    </label>
                                    <input
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition text-center text-2xl tracking-widest"
                                        id="confirm-password-mobile"
                                        name="confirmPassword"
                                        type="password"
                                        placeholder="• • • •"
                                        maxLength="4"
                                        pattern="\d{4}"
                                        value={formData.confirmPassword}
                                        onChange={handleChange}
                                        required
                                    />
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
                                            Registering...
                                        </span>
                                    ) : (
                                        'Complete Registration'
                                    )}
                                </button>
                            </form>
                        )}

                        <div className="mt-6 text-center">
                            <p className="text-gray-600 text-sm">
                                Already have an account?{' '}
                                <button 
                                    onClick={onSwitchToLogin}
                                    className="text-green-600 hover:text-green-700 font-medium"
                                >
                                    Login
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
                        
                        {/* Right Side - Signup Form */}
                        <div className="w-1/2 p-12">
                            <div className="mb-8">
                                <h2 className="text-3xl font-bold text-green-600 mb-2">Sign Up</h2>
                                <p className="text-gray-600">Create your account to get started</p>
                            </div>

                            {/* Progress Indicator */}
                            <div className="flex justify-center mb-8">
                                <div className="flex items-center space-x-2">
                                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${step >= 1 ? 'bg-green-600 text-white' : 'bg-gray-300 text-gray-600'}`}>
                                        1
                                    </div>
                                    <div className={`w-16 h-1 ${step >= 2 ? 'bg-green-600' : 'bg-gray-300'}`}></div>
                                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${step >= 2 ? 'bg-green-600 text-white' : 'bg-gray-300 text-gray-600'}`}>
                                        2
                                    </div>
                                    <div className={`w-16 h-1 ${step >= 3 ? 'bg-green-600' : 'bg-gray-300'}`}></div>
                                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${step >= 3 ? 'bg-green-600 text-white' : 'bg-gray-300 text-gray-600'}`}>
                                        3
                                    </div>
                                </div>
                            </div>

                            {/* Step 1: Phone & Name */}
                            {step === 1 && (
                                <form onSubmit={handlePhoneSubmit}>
                                    {error && (
                                        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                                            <p className="text-sm">{error}</p>
                                        </div>
                                    )}
                                    {successMessage && (
                                        <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
                                            <p className="text-sm">{successMessage}</p>
                                        </div>
                                    )}
                                    <div className="mb-4">
                                        <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="name-desktop">
                                            Full Name
                                        </label>
                                        <input
                                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                            id="name-desktop"
                                            name="name"
                                            type="text"
                                            placeholder="Enter your full name"
                                            value={formData.name}
                                            onChange={handleChange}
                                            required
                                        />
                                    </div>
                                    <div className="mb-6">
                                        <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="phone-desktop">
                                            Phone Number
                                        </label>
                                        <input
                                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                            id="phone-desktop"
                                            name="phone"
                                            type="tel"
                                            placeholder="+254-73-456-7890"
                                            value={formData.phone}
                                            onChange={handleChange}
                                            required
                                        />
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
                                                Sending OTP...
                                            </span>
                                        ) : (
                                            'Send OTP'
                                        )}
                                    </button>
                                </form>
                            )}

                            {/* Step 2: OTP Verification */}
                            {step === 2 && (
                                <form onSubmit={handleOtpSubmit}>
                                    {error && (
                                        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                                            <p className="text-sm">{error}</p>
                                        </div>
                                    )}
                                    {successMessage && (
                                        <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
                                            <p className="text-sm">{successMessage}</p>
                                        </div>
                                    )}
                                    <div className="text-center mb-6">
                                        <p className="text-gray-600 text-sm">
                                            We've sent a verification code to
                                        </p>
                                        <p className="text-green-600 font-semibold">{formData.phone}</p>
                                    </div>
                                    <div className="mb-6">
                                        <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="otp-desktop">
                                            Enter OTP
                                        </label>
                                        <input
                                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition text-center text-2xl tracking-widest"
                                            id="otp-desktop"
                                            name="otp"
                                            type="text"
                                            placeholder="- - - - - -"
                                            maxLength="6"
                                            value={formData.otp}
                                            onChange={handleChange}
                                            required
                                        />
                                    </div>
                                    <button
                                        className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 shadow-md hover:shadow-lg mb-4 disabled:bg-gray-400 disabled:cursor-not-allowed"
                                        type="submit"
                                        disabled={isLoading}
                                    >
                                        {isLoading ? (
                                            <span className="flex items-center justify-center">
                                                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                                </svg>
                                                Verifying...
                                            </span>
                                        ) : (
                                            'Verify OTP'
                                        )}
                                    </button>
                                    <button
                                        className="w-full text-green-600 hover:text-green-700 font-medium text-sm disabled:text-gray-400"
                                        type="button"
                                        onClick={handleResendOTP}
                                        disabled={isLoading}
                                    >
                                        Resend OTP
                                    </button>
                                </form>
                            )}

                            {/* Step 3: Set Password */}
                            {step === 3 && (
                                <form onSubmit={handlePasswordSubmit}>
                                    {error && (
                                        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                                            <p className="text-sm">{error}</p>
                                        </div>
                                    )}
                                    {successMessage && (
                                        <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
                                            <p className="text-sm">{successMessage}</p>
                                        </div>
                                    )}
                                    <div className="text-center mb-6">
                                        <p className="text-gray-600 text-sm">
                                            Set a 4-digit PIN to secure your account
                                        </p>
                                    </div>
                                    <div className="mb-4">
                                        <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password-desktop">
                                            4-Digit PIN
                                        </label>
                                        <input
                                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition text-center text-2xl tracking-widest"
                                            id="password-desktop"
                                            name="password"
                                            type="password"
                                            placeholder="• • • •"
                                            maxLength="4"
                                            pattern="\d{4}"
                                            value={formData.password}
                                            onChange={handleChange}
                                            required
                                        />
                                    </div>
                                    <div className="mb-6">
                                        <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="confirm-password-desktop">
                                            Confirm PIN
                                        </label>
                                        <input
                                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition text-center text-2xl tracking-widest"
                                            id="confirm-password-desktop"
                                            name="confirmPassword"
                                            type="password"
                                            placeholder="• • • •"
                                            maxLength="4"
                                            pattern="\d{4}"
                                            value={formData.confirmPassword}
                                            onChange={handleChange}
                                            required
                                        />
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
                                                Registering...
                                            </span>
                                        ) : (
                                            'Complete Registration'
                                        )}
                                    </button>
                                </form>
                            )}

                            <div className="mt-6 text-center">
                                <p className="text-gray-600 text-sm">
                                    Already have an account?{' '}
                                    <button 
                                        onClick={onSwitchToLogin}
                                        className="text-green-600 hover:text-green-700 font-medium"
                                    >
                                        Login
                                    </button>
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
}
