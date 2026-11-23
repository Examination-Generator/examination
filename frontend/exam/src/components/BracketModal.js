import React, { useEffect, useState } from 'react';
import { BracketGlyph } from '../utils/renderTextWithImages';

export default function BracketModal({ open, onClose, onInsert }) {
    const [side, setSide] = useState('opening');
    const [shape, setShape] = useState('curly');
    const [height, setHeight] = useState('60');
    const [text, setText] = useState('');
    const [upper, setUpper] = useState('');
    const [lower, setLower] = useState('');

    useEffect(() => {
        if (!open) {
            setSide('opening');
            setShape('curly');
            setHeight('60');
            setText('');
            setUpper('');
            setLower('');
        }
    }, [open]);

    if (!open) return null;

    const insert = event => {
        event.preventDefault();
        const parsedHeight = Math.min(400, Math.max(20, parseInt(height, 10) || 60));
        if (shape === 'sum') {
            onInsert({ token: `[SUM:${encodeURIComponent(upper.trim())}|${encodeURIComponent(lower.trim())}|${text}]` });
            return;
        }
        onInsert({
            side,
            shape,
            height: parsedHeight,
            text,
        });
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <button type="button" aria-label="Close bracket builder" className="absolute inset-0 bg-black/50" onClick={onClose} />
            <form onSubmit={insert} className="relative z-10 bg-white rounded-xl shadow-2xl w-full max-w-lg p-6">
                <h3 className="text-xl font-bold text-gray-800 mb-1">Insert Bracket</h3>
                <p className="text-sm text-gray-600 mb-5">The text will remain inside the selected bracket.</p>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <label className="text-sm font-semibold text-gray-700">
                        Side
                        <select value={side} onChange={event => setSide(event.target.value)} className="mt-1 w-full px-3 py-2 border rounded-lg">
                            <option value="opening">Opening</option>
                            <option value="closing">Closing</option>
                        </select>
                    </label>
                    <label className="text-sm font-semibold text-gray-700">
                        Bracket
                        <select value={shape} onChange={event => setShape(event.target.value)} className="mt-1 w-full px-3 py-2 border rounded-lg">
                            <option value="curly">Curly</option>
                            <option value="rounded">Rounded</option>
                            <option value="square">Square</option>
                            <option value="sum">Summation (Σ)</option>
                        </select>
                    </label>
                    <label className="text-sm font-semibold text-gray-700">
                        Height (px)
                        <input type="number" min="20" max="400" value={height} onChange={event => setHeight(event.target.value)} className="mt-1 w-full px-3 py-2 border rounded-lg" />
                    </label>
                </div>

                {shape === 'sum' && (
                    <div className="grid grid-cols-2 gap-4 mt-4">
                        <label className="text-sm font-semibold text-gray-700">Upper limit
                            <input value={upper} onChange={event => setUpper(event.target.value)} className="mt-1 w-full px-3 py-2 border rounded-lg" placeholder="n" />
                        </label>
                        <label className="text-sm font-semibold text-gray-700">Lower limit
                            <input value={lower} onChange={event => setLower(event.target.value)} className="mt-1 w-full px-3 py-2 border rounded-lg" placeholder="i=1" />
                        </label>
                    </div>
                )}

                <label className="block text-sm font-semibold text-gray-700 mt-4">
                    {shape === 'sum' ? 'Expression to sum' : 'Text inside bracket'}
                    <textarea value={text} onChange={event => setText(event.target.value)} className="mt-1 w-full px-3 py-2 border rounded-lg min-h-24" placeholder="Enter text or an equation" />
                </label>

                <div className="mt-4 p-4 bg-gray-50 rounded-lg overflow-x-auto">
                    {shape === 'sum' ? (
                        <span className="inline-flex items-center gap-1">
                            <span className="inline-flex flex-col items-center text-center">
                                <span style={{ fontSize: '0.7em', minHeight: '1.1em' }}>{upper || '\u00a0'}</span>
                                <span style={{ fontSize: '1.9em', lineHeight: 1 }}>{'\u2211'}</span>
                                <span style={{ fontSize: '0.7em', minHeight: '1.1em' }}>{lower || '\u00a0'}</span>
                            </span>
                            <span className="whitespace-pre-wrap">{text || 'Expression'}</span>
                        </span>
                    ) : (
                    <span className="inline-flex items-stretch justify-center" style={{ minHeight: `${Math.min(400, Math.max(20, parseInt(height, 10) || 60))}px`, lineHeight: 1.2 }}>
                        {side === 'opening' && <BracketGlyph opening shape={shape} height={Math.min(400, Math.max(20, parseInt(height, 10) || 60))} />}
                        <span className="px-2 flex items-center text-left whitespace-pre-wrap">{text || 'Equation'}</span>
                        {side === 'closing' && <BracketGlyph opening={false} shape={shape} height={Math.min(400, Math.max(20, parseInt(height, 10) || 60))} />}
                    </span>
                    )}
                </div>

                <div className="flex justify-end gap-3 mt-6">
                    <button type="button" onClick={onClose} className="px-4 py-2 rounded-lg bg-gray-200">Cancel</button>
                    <button type="submit" className="px-4 py-2 rounded-lg bg-green-600 text-white font-semibold">Insert Bracket</button>
                </div>
            </form>
        </div>
    );
}
