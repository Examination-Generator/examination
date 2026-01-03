import React, { useState, useEffect } from 'react';

export default function TableMatrixModal({ open, onClose, onInsert, type = 'table' }) {
    const [rows, setRows] = useState(type === 'table' ? '3' : '2');
    const [cols, setCols] = useState(type === 'table' ? '3' : '2');
    const [showGrid, setShowGrid] = useState(false);
    const [cellData, setCellData] = useState([]);

    useEffect(() => {
        if (open) {
            setRows(type === 'table' ? '3' : '2');
            setCols(type === 'table' ? '3' : '2');
            setShowGrid(false);
            setCellData([]);
        }
    }, [open, type]);

    if (!open) return null;

    const handleCreateGrid = () => {
        const rowCount = parseInt(rows);
        const colCount = parseInt(cols);
        
        if (!rows || !cols || isNaN(rowCount) || isNaN(colCount) || rowCount < 1 || colCount < 1) {
            alert('Please enter valid positive numbers for rows and columns');
            return;
        }
        
        // Initialize cell data array
        const initialData = Array(rowCount).fill(null).map(() => 
            Array(colCount).fill('')
        );
        setCellData(initialData);
        setShowGrid(true);
    };

    const handleCellChange = (rowIndex, colIndex, value) => {
        const newData = [...cellData];
        newData[rowIndex][colIndex] = value;
        setCellData(newData);
    };

    const handleInsert = () => {
        const rowCount = parseInt(rows);
        const colCount = parseInt(cols);
        
        // Flatten cell data and join with pipe separator
        const cellValues = cellData.flat().map(cell => cell || '').join('|');
        onInsert({ rows: rowCount, cols: colCount, data: cellValues });
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            <div className="absolute inset-0 bg-black opacity-50" onClick={onClose}></div>
            <div className="bg-white rounded-lg shadow-lg z-10 p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
                <h3 className="text-lg font-semibold mb-3">
                    Insert {type === 'table' ? 'Table' : 'Matrix'}
                </h3>

                {!showGrid ? (
                    <>
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
                                onClick={handleCreateGrid}
                                className="px-4 py-2 rounded bg-green-600 text-white hover:bg-green-700"
                            >
                                Next
                            </button>
                        </div>
                    </>
                ) : (
                    <>
                        <p className="text-sm text-gray-600 mb-3">
                            {type === 'table' ? 'Enter text or numbers in each cell' : 'Enter values for each cell (fractions supported)'}
                        </p>
                        
                        <div className="overflow-x-auto mb-4">
                            <table className="border-collapse border border-gray-400 mx-auto">
                                <tbody>
                                    {cellData.map((row, rowIndex) => (
                                        <tr key={rowIndex}>
                                            {row.map((cell, colIndex) => (
                                                <td key={colIndex} className="border border-gray-400 p-1">
                                                    <input
                                                        type="text"
                                                        value={cell}
                                                        onChange={(e) => handleCellChange(rowIndex, colIndex, e.target.value)}
                                                        className="w-20 p-2 text-center border-0 focus:outline-none focus:ring-1 focus:ring-green-500"
                                                        placeholder={type === 'matrix' ? 'x' : ''}
                                                    />
                                                </td>
                                            ))}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        <div className="flex justify-end gap-2">
                            <button onClick={() => setShowGrid(false)} className="px-4 py-2 rounded bg-gray-200 hover:bg-gray-300">
                                Back
                            </button>
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
                    </>
                )}
            </div>
        </div>
    );
}
