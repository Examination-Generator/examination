import React, { useState, useEffect } from 'react';

export default function FractionModal({ open, onClose, onInsert }) {
    const [whole, setWhole] = useState('');
    const [numerator, setNumerator] = useState('');
    const [denominator, setDenominator] = useState('');

    useEffect(() => {
        if (!open) {
            setWhole('');
            setNumerator('');
            setDenominator('');
        }
    }, [open]);

    if (!open) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            <div className="absolute inset-0 bg-black opacity-50" onClick={onClose}></div>
            <div className="bg-white rounded-lg shadow-lg z-10 p-6 w-full max-w-md">
                <h3 className="text-lg font-semibold mb-3">Insert Fraction</h3>

                <label className="block text-sm text-gray-700">Whole number (optional)</label>
                <input type="text" value={whole} onChange={e => setWhole(e.target.value)} className="w-full mb-3 mt-1 p-2 border rounded" placeholder="e.g., 1 for 1 1/2" />

                <label className="block text-sm text-gray-700">Numerator</label>
                <input type="text" value={numerator} onChange={e => setNumerator(e.target.value)} className="w-full mb-3 mt-1 p-2 border rounded" placeholder="e.g., 3" />

                <label className="block text-sm text-gray-700">Denominator</label>
                <input type="text" value={denominator} onChange={e => setDenominator(e.target.value)} className="w-full mb-4 mt-1 p-2 border rounded" placeholder="e.g., 4" />

                <div className="flex justify-end gap-2">
                    <button onClick={onClose} className="px-4 py-2 rounded bg-gray-200">Cancel</button>
                    <button
                        onClick={() => {
                            if (!numerator || !denominator) return alert('Please enter numerator and denominator');
                            onInsert({ whole: whole?.trim(), numerator: numerator.trim(), denominator: denominator.trim() });
                        }}
                        className="px-4 py-2 rounded bg-green-600 text-white"
                    >
                        Insert
                    </button>
                </div>
            </div>
        </div>
    );
}
