import React, { useState, useEffect } from 'react';

export default function TableMatrixModal({ open, onClose, onInsert, type = 'table' }) {
    const [rows, setRows] = useState(type === 'table' ? '3' : '2');
    const [cols, setCols] = useState(type === 'table' ? '3' : '2');

    useEffect(() => {
        if (open) {
            setRows(type === 'table' ? '3' : '2');
            setCols(type === 'table' ? '3' : '2');
        }
    }, [open, type]);

    if (!open) return null;

    const handleInsert = () => {
        const rowCount = parseInt(rows);
        const colCount = parseInt(cols);
        
        if (!rows || !cols || isNaN(rowCount) || isNaN(colCount) || rowCount < 1 || colCount < 1) {
            alert('Please enter valid positive numbers for rows and columns');
            return;
        }
        
        onInsert({ rows: rowCount, cols: colCount });
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            <div className="absolute inset-0 bg-black opacity-50" onClick={onClose}></div>
            <div className="bg-white rounded-lg shadow-lg z-10 p-6 w-full max-w-md">
                <h3 className="text-lg font-semibold mb-3">
                    Insert {type === 'table' ? 'Table' : 'Matrix'}
                </h3>

                <label className="block text-sm text-gray-700">Number of Rows</label>
                <input 
                    type="number" 
                    value={rows} 
                    onChange={e => setRows(e.target.value)} 
                    className="w-full mb-3 mt-1 p-2 border rounded" 
                    placeholder="e.g., 3" 
                    min="1"
                />

                <label className="block text-sm text-gray-700">Number of Columns</label>
                <input 
                    type="number" 
                    value={cols} 
                    onChange={e => setCols(e.target.value)} 
                    className="w-full mb-4 mt-1 p-2 border rounded" 
                    placeholder="e.g., 3"
                    min="1"
                />

                <div className="flex justify-end gap-2">
                    <button onClick={onClose} className="px-4 py-2 rounded bg-gray-200 hover:bg-gray-300">
                        Cancel
                    </button>
                    <button
                        onClick={handleInsert}
                        className="px-4 py-2 rounded bg-green-600 text-white hover:bg-green-700"
                    >
                        Insert
                    </button>
                </div>
            </div>
        </div>
    );
}
