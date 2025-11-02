export default function Login({ onSwitchToSignup, onLoginSuccess }){
    
    const handleSubmit = (e) => {
        e.preventDefault();
        // TODO: Add actual login validation
        console.log('Login submitted');
        onLoginSuccess();
    };

    return(
        <>
        <div className="min-h-screen flex items-center justify-center p-4">
            <div className="w-full max-w-5xl">
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
                        <div className="mb-4">
                            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="phone-mobile">
                                Phone Number
                            </label>
                            <input
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                id="phone-mobile"
                                type="tel"
                                placeholder="+254-73-456-7890"
                            />
                        </div>
                        <div className="mb-6">
                            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password-mobile">
                                Password
                            </label>
                            <input
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                id="password-mobile"
                                type="password"
                                placeholder="********"
                            />
                        </div>
                        <div className="flex items-center justify-between mb-6">
                            <label className="flex items-center">
                                <input type="checkbox" className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500" />
                                <span className="ml-2 text-sm text-gray-600">Remember me</span>
                            </label>
                            <a href="#" className="text-sm text-green-600 hover:text-green-700 font-medium">
                                Forgot password?
                            </a>
                        </div>
                        <button
                            className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 shadow-md hover:shadow-lg"
                            type="submit"
                        >
                            Login
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
                        <h2 className="text-4xl font-bold text-white text-center mb-4 text-green-600">Exam App</h2>
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
                            <div className="mb-4">
                                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="phone-desktop">
                                    Phone Number
                                </label>
                                <input
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                    id="phone-desktop"
                                    type="tel"
                                    placeholder="+254-73-456-7890"
                                />
                            </div>
                            <div className="mb-6">
                                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password-desktop">
                                    Password
                                </label>
                                <input
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                    id="password-desktop"
                                    type="password"
                                    placeholder="********"
                                />
                            </div>
                            <div className="flex items-center justify-between mb-6">
                                <label className="flex items-center">
                                    <input type="checkbox" className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500" />
                                    <span className="ml-2 text-sm text-gray-600">Remember me</span>
                                </label>
                                <a href="#" className="text-sm text-green-600 hover:text-green-700 font-medium">
                                    Forgot password?
                                </a>
                            </div>
                            <button
                                className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 shadow-md hover:shadow-lg"
                                type="submit"
                            >
                                Login
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
        </>
    );
}