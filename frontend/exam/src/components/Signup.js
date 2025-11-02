import { useState } from 'react';

export default function Signup({ onSwitchToLogin }) {
    const [step, setStep] = useState(1); // 1: Phone & Name, 2: OTP, 3: Password
    const [formData, setFormData] = useState({
        name: '',
        phone: '',
        otp: '',
        password: '',
        confirmPassword: ''
    });

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handlePhoneSubmit = (e) => {
        e.preventDefault();
        // TODO: Send OTP to phone number
        console.log('Sending OTP to:', formData.phone);
        setStep(2);
    };

    const handleOtpSubmit = (e) => {
        e.preventDefault();
        // TODO: Verify OTP
        console.log('Verifying OTP:', formData.otp);
        setStep(3);
    };

    const handlePasswordSubmit = (e) => {
        e.preventDefault();
        // TODO: Create account with password
        console.log('Creating account:', formData);
        // Redirect to login or dashboard
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
                                    className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 shadow-md hover:shadow-lg"
                                    type="submit"
                                >
                                    Send OTP
                                </button>
                            </form>
                        )}

                        {/* Step 2: OTP Verification */}
                        {step === 2 && (
                            <form onSubmit={handleOtpSubmit}>
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
                                    className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 shadow-md hover:shadow-lg mb-4"
                                    type="submit"
                                >
                                    Verify OTP
                                </button>
                                <button
                                    className="w-full text-green-600 hover:text-green-700 font-medium text-sm"
                                    type="button"
                                    onClick={() => console.log('Resending OTP...')}
                                >
                                    Resend OTP
                                </button>
                            </form>
                        )}

                        {/* Step 3: Set Password */}
                        {step === 3 && (
                            <form onSubmit={handlePasswordSubmit}>
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
                                    className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 shadow-md hover:shadow-lg"
                                    type="submit"
                                >
                                    Complete Registration
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
                        <div className="w-1/2 bg-gradient-to-br p-12 flex flex-col items-center justify-center">
                            <img 
                                src="/exam.png" 
                                alt="Exam Logo" 
                                className="w-64 h-64 object-contain mb-8"
                            />
                            <h2 className="text-4xl font-bold text-white text-center mb-4 text-green-600">Exam App</h2>
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
                                        className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 shadow-md hover:shadow-lg"
                                        type="submit"
                                    >
                                        Send OTP
                                    </button>
                                </form>
                            )}

                            {/* Step 2: OTP Verification */}
                            {step === 2 && (
                                <form onSubmit={handleOtpSubmit}>
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
                                        className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 shadow-md hover:shadow-lg mb-4"
                                        type="submit"
                                    >
                                        Verify OTP
                                    </button>
                                    <button
                                        className="w-full text-green-600 hover:text-green-700 font-medium text-sm"
                                        type="button"
                                        onClick={() => console.log('Resending OTP...')}
                                    >
                                        Resend OTP
                                    </button>
                                </form>
                            )}

                            {/* Step 3: Set Password */}
                            {step === 3 && (
                                <form onSubmit={handlePasswordSubmit}>
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
                                        className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 shadow-md hover:shadow-lg"
                                        type="submit"
                                    >
                                        Complete Registration
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
