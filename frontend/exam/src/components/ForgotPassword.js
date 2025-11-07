import React, { useState } from 'react';
import { requestPasswordReset, resetPassword } from '../services/authService';

const ForgotPassword = ({ onClose, onSuccess }) => {
    const [step, setStep] = useState(1); // 1: Enter Phone, 2: Enter OTP & New Password
    const [phoneNumber, setPhoneNumber] = useState('');
    const [otp, setOtp] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState('');

    const handleRequestOTP = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            const response = await requestPasswordReset(phoneNumber);
            setSuccessMessage('OTP sent successfully to your phone number');
            setStep(2);
        } catch (err) {
            setError(err.message || 'Failed to send OTP. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleResetPassword = async (e) => {
        e.preventDefault();
        setError('');

        // Validate passwords match
        if (newPassword !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        // Validate password length (4 digits)
        if (newPassword.length !== 4 || !/^\d{4}$/.test(newPassword)) {
            setError('Password must be exactly 4 digits');
            return;
        }

        setIsLoading(true);

        try {
            await resetPassword(phoneNumber, otp, newPassword);
            setSuccessMessage('Password reset successful! You can now login with your new password.');
            setTimeout(() => {
                if (onSuccess) onSuccess();
                onClose();
            }, 2000);
        } catch (err) {
            setError(err.message || 'Failed to reset password. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-8 relative">
                {/* Close Button */}
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
                >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>

                {/* Header */}
                <div className="text-center mb-6">
                    <h2 className="text-2xl font-bold text-gray-800">Reset Password</h2>
                    <p className="text-gray-600 mt-2">
                        {step === 1 ? 'Enter your phone number to receive an OTP' : 'Enter the OTP and your new password'}
                    </p>
                </div>

                {/* Error Message */}
                {error && (
                    <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                        {error}
                    </div>
                )}

                {/* Success Message */}
                {successMessage && (
                    <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
                        {successMessage}
                    </div>
                )}

                {/* Step 1: Request OTP */}
                {step === 1 && (
                    <form onSubmit={handleRequestOTP}>
                        <div className="mb-6">
                            <label className="block text-gray-700 text-sm font-semibold mb-2">
                                Phone Number
                            </label>
                            <input
                                type="tel"
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                                placeholder="Enter your phone number"
                                value={phoneNumber}
                                onChange={(e) => setPhoneNumber(e.target.value)}
                                required
                            />
                        </div>

                        <button
                            type="submit"
                            className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 shadow-md hover:shadow-lg disabled:bg-gray-400 disabled:cursor-not-allowed"
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

                {/* Step 2: Reset Password */}
                {step === 2 && (
                    <form onSubmit={handleResetPassword}>
                        <div className="mb-4">
                            <label className="block text-gray-700 text-sm font-semibold mb-2">
                                OTP Code
                            </label>
                            <input
                                type="text"
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                                placeholder="Enter 6-digit OTP"
                                maxLength="6"
                                value={otp}
                                onChange={(e) => setOtp(e.target.value)}
                                required
                            />
                        </div>

                        <div className="mb-4">
                            <label className="block text-gray-700 text-sm font-semibold mb-2">
                                New Password
                            </label>
                            <input
                                type="password"
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                                placeholder="Enter 4-digit password"
                                maxLength="4"
                                value={newPassword}
                                onChange={(e) => setNewPassword(e.target.value.replace(/\D/g, ''))}
                                required
                            />
                        </div>

                        <div className="mb-6">
                            <label className="block text-gray-700 text-sm font-semibold mb-2">
                                Confirm Password
                            </label>
                            <input
                                type="password"
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                                placeholder="Confirm 4-digit password"
                                maxLength="4"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value.replace(/\D/g, ''))}
                                required
                            />
                        </div>

                        <div className="flex gap-3">
                            <button
                                type="button"
                                onClick={() => setStep(1)}
                                className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold py-3 px-6 rounded-lg transition duration-200"
                            >
                                Back
                            </button>
                            <button
                                type="submit"
                                className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 shadow-md hover:shadow-lg disabled:bg-gray-400 disabled:cursor-not-allowed"
                                disabled={isLoading}
                            >
                                {isLoading ? (
                                    <span className="flex items-center justify-center">
                                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Resetting...
                                    </span>
                                ) : (
                                    'Reset Password'
                                )}
                            </button>
                        </div>
                    </form>
                )}
            </div>
        </div>
    );
};

export default ForgotPassword;
