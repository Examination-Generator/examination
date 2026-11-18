import React, { useEffect, useState } from 'react';

export default function ColumnsModal({ open, onClose, onInsert }) {
    const [count, setCount] = useState(2);
    const [line, setLine] = useState(true);

    useEffect(() => {
        if (!open) { setCount(2); setLine(true); }
    }, [open]);

    if (!open) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <button type="button" aria-label="Close" className="absolute inset-0 bg-black/50 cursor-default" onClick={onClose} />
            <div className="relative z-10 bg-white rounded-xl shadow-2xl w-full max-w-sm p-5">
                <h3 className="text-lg font-bold text-gray-800 mb-3">Columns</h3>

                <div className="flex gap-2 mb-3">
                    {[2, 3, 4].map(n => (
                        <button key={n} type="button" onClick={() => setCount(n)}
                            className={`flex-1 py-2 rounded-lg border text-sm font-semibold ${count === n ? 'bg-orange-500 border-orange-500 text-white' : 'bg-gray-50 border-gray-300 hover:bg-gray-100'}`}>
                            {n}
                        </button>
                    ))}
                </div>

                <label className="flex items-center gap-2 text-sm text-gray-700 mb-3">
                    <input type="checkbox" checked={line} onChange={event => setLine(event.target.checked)} className="h-4 w-4" />
                    Divider line
                </label>

                <div className="grid gap-2 p-2 bg-gray-50 rounded-lg mb-4" style={{ gridTemplateColumns: `repeat(${count}, 1fr)` }}>
                    {Array.from({ length: count }, (_, i) => (
                        <div key={i} className="h-10 bg-white rounded text-xs text-gray-400 flex items-center justify-center"
                            style={{ borderLeft: line && i > 0 ? '1px solid #111' : 'none' }}>{i + 1}</div>
                    ))}
                </div>

                <div className="flex justify-end gap-3">
                    <button type="button" onClick={onClose} className="px-4 py-2 rounded-lg bg-gray-200 hover:bg-gray-300 text-gray-800">Cancel</button>
                    <button type="button" onClick={() => onInsert({ count, line })} className="px-4 py-2 rounded-lg bg-green-600 hover:bg-green-700 text-white font-semibold">Insert</button>
                </div>
            </div>
        </div>
    );
}
