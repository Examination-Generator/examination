import React, { useState, useEffect, useRef } from 'react';

export default function TableMatrixModal({ open, onClose, onInsert, type = 'table' }) {
    const [rows, setRows] = useState(type === 'table' ? '3' : '2');
    const [cols, setCols] = useState(type === 'table' ? '3' : '2');
    const [showGrid, setShowGrid] = useState(false);
    const [cellData, setCellData] = useState([]);
    
    // Track column widths and row heights
    const [colWidths, setColWidths] = useState([]);
    const [rowHeights, setRowHeights] = useState([]);
    
    // Track merged cells: {rowIndex: {colIndex: {colspan, rowspan, isMerged}}}
    const [mergedCells, setMergedCells] = useState({});
    
    // Selection state for merging
    const [selectedCells, setSelectedCells] = useState([]);
    const [isSelecting, setIsSelecting] = useState(false);
    const [selectionStart, setSelectionStart] = useState(null);
    
    // Resize state
    const [resizing, setResizing] = useState(null);
    const tableRef = useRef(null);

    useEffect(() => {
        if (open) {
            setRows(type === 'table' ? '3' : '2');
            setCols(type === 'table' ? '3' : '2');
            setShowGrid(false);
            setCellData([]);
            setColWidths([]);
            setRowHeights([]);
            setMergedCells({});
            setSelectedCells([]);
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
        
        // Initialize default column widths (120px each)
        setColWidths(Array(colCount).fill(120));
        
        // Initialize default row heights (40px each)
        setRowHeights(Array(rowCount).fill(40));
        
        // Initialize merged cells tracking
        setMergedCells({});
        
        setShowGrid(true);
    };

    const handleCellChange = (rowIndex, colIndex, value) => {
        const newData = [...cellData];
        newData[rowIndex][colIndex] = value;
        setCellData(newData);
    };
    
    // Handle column resize
    const handleColumnResize = (colIndex, startX) => {
        const startWidth = colWidths[colIndex];
        
        const onMouseMove = (e) => {
            const delta = e.clientX - startX;
            const newWidth = Math.max(60, startWidth + delta);
            const newWidths = [...colWidths];
            newWidths[colIndex] = newWidth;
            setColWidths(newWidths);
        };
        
        const onMouseUp = () => {
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
            setResizing(null);
        };
        
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    };
    
    // Handle row resize
    const handleRowResize = (rowIndex, startY) => {
        const startHeight = rowHeights[rowIndex];
        
        const onMouseMove = (e) => {
            const delta = e.clientY - startY;
            const newHeight = Math.max(30, startHeight + delta);
            const newHeights = [...rowHeights];
            newHeights[rowIndex] = newHeight;
            setRowHeights(newHeights);
        };
        
        const onMouseUp = () => {
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
            setResizing(null);
        };
        
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    };
    
    // Check if a cell is merged (hidden)
    const isCellMerged = (rowIndex, colIndex) => {
        // Check if this cell is part of a merged region but not the origin
        for (let r = 0; r <= rowIndex; r++) {
            for (let c = 0; c <= colIndex; c++) {
                const cell = mergedCells[r]?.[c];
                if (cell && cell.colspan > 1 || cell && cell.rowspan > 1) {
                    const endRow = r + (cell.rowspan || 1) - 1;
                    const endCol = c + (cell.colspan || 1) - 1;
                    if (rowIndex >= r && rowIndex <= endRow && colIndex >= c && colIndex <= endCol) {
                        if (r === rowIndex && c === colIndex) return false; // This is the origin cell
                        return true; // This cell is hidden
                    }
                }
            }
        }
        return false;
    };
    
    // Get cell merge info
    const getCellMergeInfo = (rowIndex, colIndex) => {
        return mergedCells[rowIndex]?.[colIndex] || { colspan: 1, rowspan: 1 };
    };
    
    // Handle cell selection for merging
    const handleCellMouseDown = (rowIndex, colIndex, e) => {
        // Don't interfere with input field interactions
        if (e.target.tagName === 'INPUT') return;
        
        if (e.button !== 0) return; // Only left click
        if (isCellMerged(rowIndex, colIndex)) return; // Don't select merged cells
        
        e.preventDefault(); // Prevent text selection
        setIsSelecting(true);
        setSelectionStart({ row: rowIndex, col: colIndex });
        setSelectedCells([{ row: rowIndex, col: colIndex }]);
    };
    
    const handleCellMouseEnter = (rowIndex, colIndex, e) => {
        if (!isSelecting || !selectionStart) return;
        if (isCellMerged(rowIndex, colIndex)) return;
        
        // Calculate selection range
        const minRow = Math.min(selectionStart.row, rowIndex);
        const maxRow = Math.max(selectionStart.row, rowIndex);
        const minCol = Math.min(selectionStart.col, colIndex);
        const maxCol = Math.max(selectionStart.col, colIndex);
        
        const newSelection = [];
        for (let r = minRow; r <= maxRow; r++) {
            for (let c = minCol; c <= maxCol; c++) {
                if (!isCellMerged(r, c)) {
                    newSelection.push({ row: r, col: c });
                }
            }
        }
        setSelectedCells(newSelection);
    };
    
    const handleMouseUp = () => {
        setIsSelecting(false);
    };
    
    // Handle clicking directly on cell background (not input)
    const handleCellClick = (rowIndex, colIndex, e) => {
        // Only handle clicks on the cell itself, not the input
        if (e.target.tagName === 'INPUT') return;
        
        if (isCellMerged(rowIndex, colIndex)) return;
        
        // Toggle selection for single cell
        const isAlreadySelected = selectedCells.some(cell => cell.row === rowIndex && cell.col === colIndex);
        
        if (e.ctrlKey || e.metaKey) {
            // Add or remove from selection with Ctrl/Cmd key
            if (isAlreadySelected) {
                setSelectedCells(selectedCells.filter(cell => !(cell.row === rowIndex && cell.col === colIndex)));
            } else {
                setSelectedCells([...selectedCells, { row: rowIndex, col: colIndex }]);
            }
        } else {
            // Single selection
            setSelectedCells([{ row: rowIndex, col: colIndex }]);
        }
    };
    
    // Merge selected cells
    const handleMergeCells = () => {
        if (selectedCells.length < 2) {
            alert('Please select at least 2 cells to merge');
            return;
        }
        
        // Find the bounds of selected cells
        const rows = selectedCells.map(c => c.row);
        const cols = selectedCells.map(c => c.col);
        const minRow = Math.min(...rows);
        const maxRow = Math.max(...rows);
        const minCol = Math.min(...cols);
        const maxCol = Math.max(...cols);
        
        const rowspan = maxRow - minRow + 1;
        const colspan = maxCol - minCol + 1;
        
        // Collect all text from selected cells
        const combinedText = selectedCells
            .map(cell => cellData[cell.row][cell.col])
            .filter(text => text.trim())
            .join(' ');
        
        // Update cell data - set origin cell to combined text, clear others
        const newData = [...cellData];
        newData[minRow][minCol] = combinedText;
        
        for (let r = minRow; r <= maxRow; r++) {
            for (let c = minCol; c <= maxCol; c++) {
                if (r !== minRow || c !== minCol) {
                    newData[r][c] = '';
                }
            }
        }
        setCellData(newData);
        
        // Update merged cells tracking
        const newMerged = { ...mergedCells };
        if (!newMerged[minRow]) newMerged[minRow] = {};
        newMerged[minRow][minCol] = { colspan, rowspan };
        setMergedCells(newMerged);
        
        setSelectedCells([]);
    };
    
    // Unmerge cells
    const handleUnmergeCells = () => {
        if (selectedCells.length !== 1) {
            alert('Please select a single merged cell to unmerge');
            return;
        }
        
        const cell = selectedCells[0];
        const mergeInfo = getCellMergeInfo(cell.row, cell.col);
        
        if (mergeInfo.colspan === 1 && mergeInfo.rowspan === 1) {
            alert('This cell is not merged');
            return;
        }
        
        // Remove merge info
        const newMerged = { ...mergedCells };
        if (newMerged[cell.row] && newMerged[cell.row][cell.col]) {
            delete newMerged[cell.row][cell.col];
            if (Object.keys(newMerged[cell.row]).length === 0) {
                delete newMerged[cell.row];
            }
        }
        setMergedCells(newMerged);
        setSelectedCells([]);
    };
    
    // Check if cell is selected
    const isCellSelected = (rowIndex, colIndex) => {
        return selectedCells.some(cell => cell.row === rowIndex && cell.col === colIndex);
    };

    const handleInsert = () => {
        const rowCount = parseInt(rows);
        const colCount = parseInt(cols);
        
        // Flatten cell data and join with pipe separator
        const cellValues = cellData.flat().map(cell => cell || '').join('|');
        
        // Encode column widths and row heights
        const widthsStr = colWidths.join(',');
        const heightsStr = rowHeights.join(',');
        
        // Encode merged cells
        const mergedStr = Object.entries(mergedCells)
            .flatMap(([rowIdx, cols]) => 
                Object.entries(cols).map(([colIdx, info]) => 
                    `${rowIdx},${colIdx},${info.colspan},${info.rowspan}`
                )
            )
            .join(';');
        
        onInsert({ 
            rows: rowCount, 
            cols: colCount, 
            data: cellValues,
            widths: widthsStr,
            heights: heightsStr,
            merged: mergedStr
        });
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
                            {type === 'table' ? 'Enter text or numbers in each cell. Drag borders to resize. Select cells and click Merge.' : 'Enter values for each cell (fractions supported)'}
                        </p>
                        
                        {/* Merge/Unmerge controls */}
                        {type === 'table' && (
                            <div className="flex flex-col gap-2 mb-3">
                                <div className="flex gap-2">
                                    <button
                                        onClick={handleMergeCells}
                                        disabled={selectedCells.length < 2}
                                        className={`px-3 py-1 rounded text-sm ${
                                            selectedCells.length < 2 
                                                ? 'bg-gray-200 text-gray-400 cursor-not-allowed' 
                                                : 'bg-blue-600 text-white hover:bg-blue-700'
                                        }`}
                                    >
                                        Merge Selected Cells
                                    </button>
                                    <button
                                        onClick={handleUnmergeCells}
                                        disabled={selectedCells.length !== 1}
                                        className={`px-3 py-1 rounded text-sm ${
                                            selectedCells.length !== 1 
                                                ? 'bg-gray-200 text-gray-400 cursor-not-allowed' 
                                                : 'bg-orange-600 text-white hover:bg-orange-700'
                                        }`}
                                    >
                                        Unmerge Cell
                                    </button>
                                    <button
                                        onClick={() => setSelectedCells([])}
                                        disabled={selectedCells.length === 0}
                                        className={`px-3 py-1 rounded text-sm ${
                                            selectedCells.length === 0
                                                ? 'bg-gray-200 text-gray-400 cursor-not-allowed' 
                                                : 'bg-gray-500 text-white hover:bg-gray-600'
                                        }`}
                                    >
                                        Clear Selection
                                    </button>
                                    {selectedCells.length > 0 && (
                                        <span className="text-sm text-gray-600 self-center">
                                            {selectedCells.length} cell(s) selected
                                        </span>
                                    )}
                                </div>
                                <p className="text-xs text-blue-600">
                                    💡 Click on cell borders to select. Drag to select multiple cells. Hold Ctrl/Cmd and click to select individual cells.
                                </p>
                            </div>
                        )}
                        
                        <div className="overflow-x-auto mb-4" onMouseUp={handleMouseUp}>
                            <table 
                                ref={tableRef}
                                className="border-collapse border-2 border-gray-500 mx-auto"
                                style={{ userSelect: 'none' }}
                            >
                                <tbody>
                                    {cellData.map((row, rowIndex) => (
                                        <tr key={rowIndex}>
                                            {row.map((cell, colIndex) => {
                                                if (isCellMerged(rowIndex, colIndex)) return null;
                                                
                                                const mergeInfo = getCellMergeInfo(rowIndex, colIndex);
                                                const isSelected = isCellSelected(rowIndex, colIndex);
                                                
                                                return (
                                                    <td 
                                                        key={colIndex} 
                                                        colSpan={mergeInfo.colspan}
                                                        rowSpan={mergeInfo.rowspan}
                                                        className={`border border-gray-400 p-0 relative ${
                                                            isSelected ? 'bg-blue-100 border-2 border-blue-500' : ''
                                                        }`}
                                                        style={{
                                                            width: `${colWidths[colIndex]}px`,
                                                            height: `${rowHeights[rowIndex]}px`,
                                                            position: 'relative',
                                                            cursor: 'pointer'
                                                        }}
                                                        onMouseDown={(e) => handleCellMouseDown(rowIndex, colIndex, e)}
                                                        onMouseEnter={(e) => handleCellMouseEnter(rowIndex, colIndex, e)}
                                                        onClick={(e) => handleCellClick(rowIndex, colIndex, e)}
                                                    >
                                                        {/* Selection indicator overlay */}
                                                        {isSelected && (
                                                            <div 
                                                                className="absolute inset-0 pointer-events-none"
                                                                style={{
                                                                    border: '2px solid #3b82f6',
                                                                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                                                                    zIndex: 1
                                                                }}
                                                            />
                                                        )}
                                                        
                                                        <input
                                                            type="text"
                                                            value={cell}
                                                            onChange={(e) => handleCellChange(rowIndex, colIndex, e.target.value)}
                                                            className="w-full h-full p-2 text-center border-0 focus:outline-none focus:ring-2 focus:ring-green-500 bg-transparent relative z-10"
                                                            placeholder={type === 'matrix' ? 'x' : ''}
                                                            onFocus={(e) => {
                                                                // Select this cell when focusing input
                                                                if (!isSelected) {
                                                                    setSelectedCells([{ row: rowIndex, col: colIndex }]);
                                                                }
                                                            }}
                                                        />
                                                        
                                                        {/* Right border resize handle */}
                                                        {type === 'table' && colIndex < cellData[0].length - 1 && (
                                                            <div
                                                                className="absolute top-0 right-0 w-1 h-full cursor-col-resize hover:bg-blue-400 bg-gray-300"
                                                                style={{ transform: 'translateX(50%)' }}
                                                                onMouseDown={(e) => {
                                                                    e.preventDefault();
                                                                    e.stopPropagation();
                                                                    setResizing({ type: 'col', index: colIndex });
                                                                    handleColumnResize(colIndex, e.clientX);
                                                                }}
                                                            />
                                                        )}
                                                        
                                                        {/* Bottom border resize handle */}
                                                        {type === 'table' && rowIndex < cellData.length - 1 && (
                                                            <div
                                                                className="absolute bottom-0 left-0 w-full h-1 cursor-row-resize hover:bg-blue-400 bg-gray-300"
                                                                style={{ transform: 'translateY(50%)' }}
                                                                onMouseDown={(e) => {
                                                                    e.preventDefault();
                                                                    e.stopPropagation();
                                                                    setResizing({ type: 'row', index: rowIndex });
                                                                    handleRowResize(rowIndex, e.clientY);
                                                                }}
                                                            />
                                                        )}
                                                    </td>
                                                );
                                            })}
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
