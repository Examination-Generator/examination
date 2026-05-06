import React from 'react';

export default function WorkingSpaceModal({
    open,
    onClose,
    onSave,
    targetSection = 'question',
    heightMm,
    setHeightMm,
}) {
    if (!open) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-2">
            <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-bold text-gray-800">
                        Add {targetSection === 'question' ? 'Question' : 'Answer'} Working Space
                    </h3>
                    <button type="button" onClick={onClose} className="text-gray-500 hover:text-gray-700">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-bold text-gray-700 mb-2">Height (millimeters) *</label>
                        <input
                            type="number"
                            min="10"
                            max="250"
                            value={heightMm}
                            onChange={(e) => {
                                const value = parseInt(e.target.value, 10);
                                if (!Number.isNaN(value) && value >= 10 && value <= 250) {
                                    setHeightMm(value);
                                }
                            }}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                            placeholder="e.g., 50"
                        />
                    </div>

                    <div className="bg-gray-50 rounded-lg p-4">
                        <p className="text-xs font-bold text-gray-700 mb-2">Preview:</p>
                        <div className="bg-white rounded border-2 border-dashed border-gray-300 overflow-hidden">
                            <div
                                style={{ height: `${Math.min(heightMm * 0.8, 120)}px`, background: 'white' }}
                                className="flex items-center justify-center text-gray-400 text-sm"
                            >
                                Blank working space ({heightMm}mm)
                            </div>
                        </div>
                    </div>
                </div>

                <div className="flex space-x-3 mt-6">
                    <button
                        type="button"
                        onClick={() => onSave({ heightMm }, targetSection)}
                        className="flex-1 bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200"
                    >
                        Add Working Space
                    </button>
                    <button
                        type="button"
                        onClick={onClose}
                        className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold py-3 px-6 rounded-lg transition duration-200"
                    >
                        Cancel
                    </button>
                </div>
            </div>
        </div>
    );
}