// src/components/DrawingTool.jsx
import React, { useRef, useEffect, useState } from 'react';
import { useDrawing, A4_DISPLAY_WIDTH_PX, A4_DISPLAY_HEIGHT_PX, MAX_GRAPH_BOXES_X, MAX_GRAPH_BOXES_Y } from '../hooks/useDrawing';

export default function DrawingTool({ onSave, onClose, section = 'question' }) {
    const canvasRef = useRef(null);
    const [showGraphPaper, setShowGraphPaper] = useState(false);
    const [graphBoxesX, setGraphBoxesX] = useState(MAX_GRAPH_BOXES_X);
    const [graphBoxesY, setGraphBoxesY] = useState(MAX_GRAPH_BOXES_Y);

    const {
        drawingTool, setDrawingTool,
        drawingColor, setDrawingColor,
        drawingWidth, setDrawingWidth,
        isLassoErasing, lassoRect,
        initCanvas, clearCanvas,
        startDraw, onDraw, stopDraw,
        exportImage, drawGraphPaper,
    } = useDrawing(canvasRef, showGraphPaper, graphBoxesX, graphBoxesY);

    useEffect(() => {
        initCanvas();
    }, [showGraphPaper, graphBoxesX, graphBoxesY]);

    const handleSave = () => {
        if (showGraphPaper) {
            onSave({ type: 'graph', graphBoxesX, graphBoxesY });
            return;
        }
        const imageUrl = exportImage(A4_DISPLAY_WIDTH_PX, A4_DISPLAY_HEIGHT_PX);
        onSave({ type: 'image', imageUrl, width: A4_DISPLAY_WIDTH_PX, height: A4_DISPLAY_HEIGHT_PX });
    };

    const tools = [
        { id: 'pen', label: '✏️ Pen' },
        { id: 'eraser', label: '🧹 Eraser' },
        { id: 'line', label: '📏 Line' },
        { id: 'rectangle', label: '▭ Rect' },
        { id: 'circle', label: '⭕ Circle' },
        { id: 'lasso-erase', label: '⬚ Erase Region' },
    ];

    return (
        <div className="border-2 border-purple-300 rounded-lg p-4 bg-purple-50">
            {/* Header */}
            <div className="flex justify-between items-center mb-3">
                <h3 className="font-bold text-gray-800">Drawing Tools</h3>
                <button type="button" onClick={onClose} className="text-gray-500 hover:text-gray-700">✕</button>
            </div>

            {/* Toolbar */}
            <div className="flex flex-wrap gap-2 mb-3 bg-white p-3 rounded-lg border">
                {/* Tool buttons */}
                <div className="flex flex-wrap gap-1">
                    {tools.map(tool => (
                        <button
                            key={tool.id}
                            type="button"
                            onClick={() => setDrawingTool(tool.id)}
                            className={`px-3 py-1.5 rounded text-sm font-medium transition ${
                                drawingTool === tool.id
                                    ? 'bg-purple-600 text-white'
                                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                            }`}
                        >
                            {tool.label}
                        </button>
                    ))}
                </div>

                {/* Color */}
                <div className="flex items-center gap-2">
                    <label className="text-xs font-semibold">Color:</label>
                    <input
                        type="color"
                        value={drawingColor}
                        onChange={e => setDrawingColor(e.target.value)}
                        className="w-10 h-8 rounded cursor-pointer border"
                    />
                </div>

                {/* Width */}
                <div className="flex items-center gap-2">
                    <label className="text-xs font-semibold">Width: {drawingWidth}px</label>
                    <input
                        type="range"
                        min="1" max="20"
                        value={drawingWidth}
                        onChange={e => setDrawingWidth(Number(e.target.value))}
                        className="w-24"
                    />
                </div>

                {/* Graph paper toggle */}
                <label className="flex items-center gap-2 cursor-pointer">
                    <input
                        type="checkbox"
                        checked={showGraphPaper}
                        onChange={e => setShowGraphPaper(e.target.checked)}
                    />
                    <span className="text-xs font-semibold">Graph Paper</span>
                </label>

                {showGraphPaper && (
                    <div className="flex items-center gap-1">
                        <input
                            type="number" min="1" max={MAX_GRAPH_BOXES_X}
                            value={graphBoxesX}
                            onChange={e => setGraphBoxesX(Math.max(1, Math.min(MAX_GRAPH_BOXES_X, parseInt(e.target.value) || 1)))}
                            className="w-16 px-2 py-1 text-xs border rounded"
                        />
                        <span className="text-xs">x</span>
                        <input
                            type="number" min="1" max={MAX_GRAPH_BOXES_Y}
                            value={graphBoxesY}
                            onChange={e => setGraphBoxesY(Math.max(1, Math.min(MAX_GRAPH_BOXES_Y, parseInt(e.target.value) || 1)))}
                            className="w-16 px-2 py-1 text-xs border rounded"
                        />
                        <span className="text-xs">cm</span>
                    </div>
                )}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2 mb-3">
                <button type="button" onClick={clearCanvas} className="bg-red-500 text-white px-4 py-2 rounded-lg text-sm">
                    Clear
                </button>
                <button type="button" onClick={handleSave} className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-semibold">
                    Save & Insert
                </button>
            </div>

            {/* Canvas */}
            <div className="relative bg-white rounded-lg border-2 border-gray-300 overflow-auto">
                <canvas
                    ref={canvasRef}
                    onMouseDown={startDraw}
                    onMouseMove={onDraw}
                    onMouseUp={stopDraw}
                    onMouseLeave={stopDraw}
                    className="cursor-crosshair"
                    style={{ width: A4_DISPLAY_WIDTH_PX, height: A4_DISPLAY_HEIGHT_PX }}
                />
                {/* Lasso preview */}
                {isLassoErasing && lassoRect && (() => {
                    const x = Math.min(lassoRect.x1, lassoRect.x2);
                    const y = Math.min(lassoRect.y1, lassoRect.y2);
                    const w = Math.abs(lassoRect.x2 - lassoRect.x1);
                    const h = Math.abs(lassoRect.y2 - lassoRect.y1);
                    return (
                        <div
                            className="absolute pointer-events-none border-2 border-dashed border-red-500 bg-red-200 bg-opacity-20"
                            style={{ left: x, top: y, width: w, height: h }}
                        />
                    );
                })()}
            </div>
        </div>
    );
}