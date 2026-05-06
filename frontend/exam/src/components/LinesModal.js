import React from 'react';

const clampLines = value => {
    const numeric = parseFloat(value);
    if (Number.isNaN(numeric)) return 0.5;
    return Math.max(0.5, Math.min(400, numeric));
};

export default function LinesModal({
    open,
    onClose,
    onSave,
    targetSection = 'question',
    config,
    setConfig,
}) {
    if (!open) return null;

    const linePreviewCount = Math.min(3, Math.ceil(config.numberOfLines));

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-2">
            <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-4">
                <div className="flex items-center justify-between mb-3">
                    <h3 className="text-xl font-bold text-gray-800">
                        Add {targetSection === 'question' ? 'Question' : 'Answer'} Lines
                    </h3>
                    <button type="button" onClick={onClose} className="text-gray-500 hover:text-gray-700">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                <div className="space-y-3">
                    <div>
                        <label className="block text-sm font-bold text-gray-700 mb-2">Number of Lines *</label>
                        <input
                            type="text"
                            inputMode="decimal"
                            value={config.numberOfLines}
                            onChange={(e) => {
                                const value = e.target.value;
                                if (value === '' || /^\d*\.?\d*$/.test(value)) {
                                    setConfig(prev => ({ ...prev, numberOfLines: value === '' ? 0.5 : clampLines(value) }));
                                }
                            }}
                            onBlur={(e) => setConfig(prev => ({ ...prev, numberOfLines: clampLines(e.target.value) }))}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            placeholder="e.g., 5 or 2.5"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-bold text-gray-700 mb-2">Line Height (spacing) *</label>
                        <div className="flex items-center gap-2">
                            <input
                                type="range"
                                min="20"
                                max="80"
                                value={config.lineHeight}
                                onChange={(e) => setConfig(prev => ({ ...prev, lineHeight: parseInt(e.target.value, 10) }))}
                                className="flex-1"
                            />
                            <span className="text-sm font-semibold text-gray-700 w-12">{config.lineHeight}px</span>
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-bold text-gray-700 mb-2">Line Style *</label>
                        <div className="grid grid-cols-2 gap-3">
                            <button
                                type="button"
                                onClick={() => setConfig(prev => ({ ...prev, lineStyle: 'dotted' }))}
                                className={`px-4 py-3 rounded-lg border-2 transition ${
                                    config.lineStyle === 'dotted'
                                        ? 'border-indigo-600 bg-indigo-50 text-indigo-700 font-bold'
                                        : 'border-gray-300 hover:border-indigo-400'
                                }`}
                            >
                                <div className="border-b-2 border-dotted border-gray-600 mb-1"></div>
                                Dotted
                            </button>
                            <button
                                type="button"
                                onClick={() => setConfig(prev => ({ ...prev, lineStyle: 'solid' }))}
                                className={`px-4 py-3 rounded-lg border-2 transition ${
                                    config.lineStyle === 'solid'
                                        ? 'border-indigo-600 bg-indigo-50 text-indigo-700 font-bold'
                                        : 'border-gray-300 hover:border-indigo-400'
                                }`}
                            >
                                <div className="border-b-2 border-solid border-gray-600 mb-1"></div>
                                Solid
                            </button>
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-bold text-gray-700 mb-2">Line Visibility (Opacity) *</label>
                        <div className="flex items-center gap-2">
                            <input
                                type="range"
                                min="0.1"
                                max="1"
                                step="0.1"
                                value={config.opacity}
                                onChange={(e) => setConfig(prev => ({ ...prev, opacity: parseFloat(e.target.value) }))}
                                className="flex-1"
                            />
                            <span className="text-sm font-semibold text-gray-700 w-12">{Math.round(config.opacity * 100)}%</span>
                        </div>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-3">
                        <p className="text-xs font-bold text-gray-700 mb-1">Preview:</p>
                        <div className="bg-white p-3 rounded border border-gray-300 overflow-y-auto h-24">
                            {[...Array(linePreviewCount)].map((_, idx) => (
                                <div
                                    key={idx}
                                    style={{
                                        height: `${config.lineHeight}px`,
                                        borderBottom: `2px ${config.lineStyle} rgba(0, 0, 0, ${config.opacity})`,
                                    }}
                                />
                            ))}
                            {config.numberOfLines > 3 && (
                                <p className="text-xs text-gray-500 text-center mt-2">... and {config.numberOfLines - 3} more lines</p>
                            )}
                        </div>
                    </div>
                </div>

                <div className="flex space-x-3 mt-4">
                    <button
                        type="button"
                        onClick={() => onSave(config, targetSection)}
                        className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200"
                    >
                        Add Lines
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