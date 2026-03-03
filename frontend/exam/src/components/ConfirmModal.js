export default function ConfirmModal({ isOpen, onClose, onConfirm, title, message, confirmText = 'Confirm', cancelText = 'Cancel', type = 'warning' }) {
    if (!isOpen) return null;

    const getColors = () => {
        switch (type) {
            case 'danger':
                return {
                    icon: 'text-red-600',
                    bg: 'bg-red-100',
                    button: 'bg-red-600 hover:bg-red-700'
                };
            case 'success':
                return {
                    icon: 'text-green-600',
                    bg: 'bg-green-100',
                    button: 'bg-green-600 hover:bg-green-700'
                };
            default:
                return {
                    icon: 'text-yellow-600',
                    bg: 'bg-yellow-100',
                    button: 'bg-yellow-600 hover:bg-yellow-700'
                };
        }
    };

    const colors = getColors();

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[100] p-4">
            <div className="bg-white rounded-xl shadow-2xl max-w-md w-full animate-fade-in">
                {/* Header */}
                <div className="p-6 border-b border-gray-200">
                    <div className="flex items-center gap-4">
                        <div className={`${colors.bg} rounded-full p-3`}>
                            <svg className={`w-6 h-6 ${colors.icon}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                            </svg>
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
                <div className="p-6 bg-gray-50 rounded-b-xl flex justify-end gap-3">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold rounded-lg transition"
                    >
                        {cancelText}
                    </button>
                    <button
                        onClick={() => {
                            onConfirm();
                            onClose();
                        }}
                        className={`px-4 py-2 ${colors.button} text-white font-semibold rounded-lg transition`}
                    >
                        {confirmText}
                    </button>
                </div>
            </div>
        </div>
    );
}
