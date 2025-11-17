import PaperGenerationDashboard from './PaperGenerationDashboard';

export default function UserDashboard({ onLogout }) {
    return (
        <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100">
            {/* Header */}
            <header className="bg-white shadow-md print:hidden">
                <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <img src="/exam.png" alt="Exam Logo" className="w-12 h-12 object-contain" />
                            <h1 className="text-2xl font-bold text-green-600">Exam Generator</h1>
                        </div>
                        <button 
                            onClick={onLogout}
                            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition"
                        >
                            Logout
                        </button>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <PaperGenerationDashboard />
        </div>
    );
}
