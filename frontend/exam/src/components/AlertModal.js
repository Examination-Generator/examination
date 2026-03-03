export default function AlertModal({ isOpen, onClose, title, message, type = 'info', buttonText = 'OK' }) {
    if (!isOpen) return null;

    const getConfig = () => {
        switch (type) {
            case 'success':
                return {
                    icon: (
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                    ),
                    iconBg: 'bg-green-100',
                    iconColor: 'text-green-600',
                    button: 'bg-green-600 hover:bg-green-700'
                };
            case 'error':
                return {
                    icon: (
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    ),
                    iconBg: 'bg-red-100',
                    iconColor: 'text-red-600',
                    button: 'bg-red-600 hover:bg-red-700'
                };
            case 'warning':
                return {
                    icon: (
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                    ),
                    iconBg: 'bg-yellow-100',
                    iconColor: 'text-yellow-600',
                    button: 'bg-yellow-600 hover:bg-yellow-700'
                };
            default:
                return {
                    icon: (
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    ),
                    iconBg: 'bg-blue-100',
                    iconColor: 'text-blue-600',
                    button: 'bg-blue-600 hover:bg-blue-700'
                };
        }
    };

    const config = getConfig();

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[100] p-4">
            <div className="bg-white rounded-xl shadow-2xl max-w-md w-full animate-fade-in">
                {/* Header */}
                <div className="p-6 border-b border-gray-200">
                    <div className="flex items-center gap-4">
                        <div className={`${config.iconBg} rounded-full p-3 ${config.iconColor}`}>
                            {config.icon}
                        </div>
                        <div>
                            <h3 className="text-lg font-bold text-gray-900">{title}</h3>
                        </div>
                    </div>
                </div>

                {/* Body */}
                <div className="p-6">
                    <p className="text-gray-700">{message}</p>
                </div>

                {/* Footer */}
                <div className="p-6 bg-gray-50 rounded-b-xl flex justify-end">
                    <button
                        onClick={onClose}
                        className={`px-6 py-2 ${config.button} text-white font-semibold rounded-lg transition`}
                    >
                        {buttonText}
                    </button>
                </div>
            </div>
        </div>
    );
}
