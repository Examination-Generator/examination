import { useState, useRef, useEffect } from 'react';

const A4_CANVAS_SCALE = 2;
const A4_WIDTH_MM = 210;
const A4_HEIGHT_MM = 297;
const PX_PER_MM = 96 / 25.4;
export const A4_DISPLAY_WIDTH_PX = Math.round(A4_WIDTH_MM * PX_PER_MM);
export const A4_DISPLAY_HEIGHT_PX = Math.round(A4_HEIGHT_MM * PX_PER_MM);
const MM_PER_CM = 10;
export const MAX_GRAPH_BOXES_X = Math.floor(A4_WIDTH_MM / MM_PER_CM);
export const MAX_GRAPH_BOXES_Y = Math.floor(A4_HEIGHT_MM / MM_PER_CM);

export function useDrawing(canvasRef, showGraphPaper, graphBoxesX, graphBoxesY) {
    const [isDrawing, setIsDrawing] = useState(false);
    const [drawingTool, setDrawingTool] = useState('pen');
    const [drawingColor, setDrawingColor] = useState('#000000');
    const [drawingWidth, setDrawingWidth] = useState(2);
    const [startPos, setStartPos] = useState({ x: 0, y: 0 });
    const [isLassoErasing, setIsLassoErasing] = useState(false);
    const [lassoRect, setLassoRect] = useState(null);

    const drawGraphPaper = (ctx, width, height, boxesX, boxesY) => {
        const safeBoxesX = Math.max(1, Math.min(boxesX, MAX_GRAPH_BOXES_X));
        const safeBoxesY = Math.max(1, Math.min(boxesY, MAX_GRAPH_BOXES_Y));
        const totalMmX = safeBoxesX * MM_PER_CM;
        const totalMmY = safeBoxesY * MM_PER_CM;
        const graphWidth = Math.min(width, totalMmX * PX_PER_MM);
        const graphHeight = Math.min(height, totalMmY * PX_PER_MM);

        ctx.save();
        ctx.imageSmoothingEnabled = false;

        // ── Vertical lines ──────────────────────────────────────────────────
        for (let mmX = 0; mmX <= totalMmX; mmX++) {
            const x = Math.round(mmX * PX_PER_MM);
            if (x > graphWidth) break;

            if (mmX % MM_PER_CM === 0) {
                // 1 cm border / major grid line — dark, bold
                ctx.fillStyle = '#1a1a1a';
                const lw = 1.5;
                ctx.fillRect(
                    Math.round(x - lw / 2), 0,
                    Math.max(1, Math.round(lw)), Math.round(graphHeight)
                );
            } else if (mmX % 5 === 0) {
                // 5 mm (centre of each cm box) — medium green
                ctx.fillStyle = '#4CAF50';
                const lw = 0.8;
                ctx.fillRect(
                    Math.round(x - lw / 2), 0,
                    Math.max(1, Math.round(lw)), Math.round(graphHeight)
                );
            } else {
                // 1 mm — thin, light green
                ctx.fillStyle = '#A5D6A7';
                const lw = 0.4;
                ctx.fillRect(
                    Math.round(x - lw / 2), 0,
                    Math.max(1, Math.round(lw)), Math.round(graphHeight)
                );
            }
        }

        // ── Horizontal lines ────────────────────────────────────────────────
        for (let mmY = 0; mmY <= totalMmY; mmY++) {
            const y = Math.round(mmY * PX_PER_MM);
            if (y > graphHeight) break;

            if (mmY % MM_PER_CM === 0) {
                // 1 cm border / major grid line — dark, bold
                ctx.fillStyle = '#1a1a1a';
                const lw = 1.5;
                ctx.fillRect(
                    0, Math.round(y - lw / 2),
                    Math.round(graphWidth), Math.max(1, Math.round(lw))
                );
            } else if (mmY % 5 === 0) {
                // 5 mm (centre of each cm box) — medium green
                ctx.fillStyle = '#4CAF50';
                const lw = 0.8;
                ctx.fillRect(
                    0, Math.round(y - lw / 2),
                    Math.round(graphWidth), Math.max(1, Math.round(lw))
                );
            } else {
                // 1 mm — thin, light green
                ctx.fillStyle = '#A5D6A7';
                const lw = 0.4;
                ctx.fillRect(
                    0, Math.round(y - lw / 2),
                    Math.round(graphWidth), Math.max(1, Math.round(lw))
                );
            }
        }

        ctx.restore();
    };

    const initCanvas = () => {
        if (!canvasRef.current) return;
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        canvas.width = A4_DISPLAY_WIDTH_PX * A4_CANVAS_SCALE;
        canvas.height = A4_DISPLAY_HEIGHT_PX * A4_CANVAS_SCALE;
        canvas.style.width = A4_DISPLAY_WIDTH_PX + 'px';
        canvas.style.height = A4_DISPLAY_HEIGHT_PX + 'px';
        ctx.scale(A4_CANVAS_SCALE, A4_CANVAS_SCALE);
        ctx.imageSmoothingEnabled = true;
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, A4_DISPLAY_WIDTH_PX, A4_DISPLAY_HEIGHT_PX);
        if (showGraphPaper) {
            drawGraphPaper(ctx, A4_DISPLAY_WIDTH_PX, A4_DISPLAY_HEIGHT_PX, graphBoxesX, graphBoxesY);
        }
    };

    const applyLassoErase = (canvas, rect) => {
        if (!rect) return;
        const ctx = canvas.getContext('2d');
        const x = Math.min(rect.x1, rect.x2);
        const y = Math.min(rect.y1, rect.y2);
        const w = Math.abs(rect.x2 - rect.x1);
        const h = Math.abs(rect.y2 - rect.y1);
        ctx.clearRect(x, y, w, h);
        ctx.fillStyle = 'white';
        ctx.fillRect(x, y, w, h);
    };

    const clearCanvas = () => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, A4_DISPLAY_WIDTH_PX, A4_DISPLAY_HEIGHT_PX);
        if (showGraphPaper) {
            drawGraphPaper(ctx, A4_DISPLAY_WIDTH_PX, A4_DISPLAY_HEIGHT_PX, graphBoxesX, graphBoxesY);
        }
    };

    const startDraw = (e) => {
        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        if (drawingTool === 'lasso-erase') {
            setIsLassoErasing(true);
            setLassoRect({ x1: x, y1: y, x2: x, y2: y });
            return;
        }
        setIsDrawing(true);
        setStartPos({ x, y });
        const ctx = canvas.getContext('2d');
        if (drawingTool === 'pen' || drawingTool === 'eraser') {
            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.strokeStyle = drawingTool === 'eraser' ? 'white' : drawingColor;
            ctx.lineWidth = drawingTool === 'eraser' ? 20 : drawingWidth;
            ctx.lineCap = 'round';
        }
    };

    const onDraw = (e) => {
        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        if (isLassoErasing) {
            setLassoRect(prev => prev ? { ...prev, x2: x, y2: y } : null);
            return;
        }
        if (!isDrawing) return;
        const ctx = canvas.getContext('2d');
        if (drawingTool === 'pen') {
            ctx.strokeStyle = drawingColor;
            ctx.lineWidth = drawingWidth;
            ctx.lineCap = 'round'; ctx.lineJoin = 'round';
            ctx.lineTo(x, y); ctx.stroke();
        } else if (drawingTool === 'eraser') {
            ctx.strokeStyle = 'white';
            ctx.lineWidth = 20;
            ctx.lineCap = 'round';
            ctx.lineTo(x, y); ctx.stroke();
        }
    };

    const stopDraw = (e) => {
        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        if (isLassoErasing) {
            setIsLassoErasing(false);
            if (lassoRect) { applyLassoErase(canvas, lassoRect); setLassoRect(null); }
            return;
        }
        if (!isDrawing) return;
        setIsDrawing(false);

        if (['line', 'rectangle', 'circle'].includes(drawingTool)) {
            const ctx = canvas.getContext('2d');
            ctx.strokeStyle = drawingColor;
            ctx.lineWidth = drawingWidth;
            ctx.lineCap = 'round';
            if (drawingTool === 'line') {
                ctx.beginPath(); ctx.moveTo(startPos.x, startPos.y); ctx.lineTo(x, y); ctx.stroke();
            } else if (drawingTool === 'rectangle') {
                ctx.beginPath(); ctx.strokeRect(startPos.x, startPos.y, x - startPos.x, y - startPos.y);
            } else if (drawingTool === 'circle') {
                const rx = Math.abs(x - startPos.x) / 2;
                const ry = Math.abs(y - startPos.y) / 2;
                ctx.beginPath();
                ctx.ellipse(startPos.x + (x - startPos.x) / 2, startPos.y + (y - startPos.y) / 2, rx, ry, 0, 0, 2 * Math.PI);
                ctx.stroke();
            }
        }
    };

    const exportImage = (width, height) => {
        const canvas = canvasRef.current;
        const exportCanvas = document.createElement('canvas');
        exportCanvas.width = width * A4_CANVAS_SCALE;
        exportCanvas.height = height * A4_CANVAS_SCALE;
        const ctx = exportCanvas.getContext('2d');
        ctx.drawImage(canvas, 0, 0, exportCanvas.width, exportCanvas.height, 0, 0, exportCanvas.width, exportCanvas.height);
        return exportCanvas.toDataURL('image/png', 1.0);
    };

    return {
        isDrawing, drawingTool, setDrawingTool,
        drawingColor, setDrawingColor,
        drawingWidth, setDrawingWidth,
        isLassoErasing, lassoRect,
        initCanvas, clearCanvas,
        startDraw, onDraw, stopDraw,
        exportImage, drawGraphPaper,
    };
}