import React, { useState, useEffect, useRef } from 'react';

export default function FractionModal({ open, onClose, onInsert }) {
    const [whole, setWhole] = useState('');
    const [numerator, setNumerator] = useState('');
    const [denominator, setDenominator] = useState('');
    
    const numeratorRef = useRef(null);
    const denominatorRef = useRef(null);
    const wholeRef = useRef(null);

    useEffect(() => {
        if (!open) {
            setWhole('');
            setNumerator('');
            setDenominator('');
        }
    }, [open]);
    
    // Helper function to wrap selected text or insert at cursor position
    const insertFormatting = (inputRef, value, setValue, openTag, closeTag) => {
        const input = inputRef.current;
        if (!input) return;
        
        const start = input.selectionStart;
        const end = input.selectionEnd;
        const selectedText = value.substring(start, end);
        
        let newValue;
        let newCursorPos;
        
        if (selectedText) {
            // Wrap selected text
            newValue = value.substring(0, start) + openTag + selectedText + closeTag + value.substring(end);
            newCursorPos = start + openTag.length + selectedText.length + closeTag.length;
        } else {
            // Insert at cursor position
            newValue = value.substring(0, start) + openTag + closeTag + value.substring(end);
            newCursorPos = start + openTag.length;
        }
        
        setValue(newValue);
        
        // Set cursor position after state update
        setTimeout(() => {
            input.focus();
            input.setSelectionRange(newCursorPos, newCursorPos);
        }, 0);
    };

    if (!open) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            <div className="absolute inset-0 bg-black opacity-50" onClick={onClose}></div>
            <div className="bg-white rounded-lg shadow-lg z-10 p-6 w-full max-w-md">
                <h3 className="text-lg font-semibold mb-3">Insert Fraction</h3>

                <label className="block text-sm text-gray-700">Whole number (optional)</label>
                <div className="mb-3">
                    <input 
                        ref={wholeRef}
                        type="text" 
                        value={whole} 
                        onChange={e => setWhole(e.target.value)} 
                        className="w-full mt-1 p-2 border rounded" 
                        placeholder="e.g., 1 for 1 1/2" 
                    />
                    <div className="flex gap-2 mt-1">
                        <button
                            type="button"
                            onClick={() => insertFormatting(wholeRef, whole, setWhole, '[SUP]', '[/SUP]')}
                            className="text-xs px-2 py-1 bg-blue-100 hover:bg-blue-200 rounded border border-blue-300"
                            title="Add superscript"
                        >
                            x<sup>n</sup>
                        </button>
                        <button
                            type="button"
                            onClick={() => insertFormatting(wholeRef, whole, setWhole, '[SUB]', '[/SUB]')}
                            className="text-xs px-2 py-1 bg-blue-100 hover:bg-blue-200 rounded border border-blue-300"
                            title="Add subscript"
                        >
                            x<sub>n</sub>
                        </button>
                    </div>
                </div>

                <label className="block text-sm text-gray-700">Numerator</label>
                <div className="mb-3">
                    <input 
                        ref={numeratorRef}
                        type="text" 
                        value={numerator} 
                        onChange={e => setNumerator(e.target.value)} 
                        className="w-full mt-1 p-2 border rounded" 
                        placeholder="e.g., 3" 
                    />
                    <div className="flex gap-2 mt-1">
                        <button
                            type="button"
                            onClick={() => insertFormatting(numeratorRef, numerator, setNumerator, '[SUP]', '[/SUP]')}
                            className="text-xs px-2 py-1 bg-blue-100 hover:bg-blue-200 rounded border border-blue-300"
                            title="Add superscript to numerator"
                        >
                            x<sup>n</sup>
                        </button>
                        <button
                            type="button"
                            onClick={() => insertFormatting(numeratorRef, numerator, setNumerator, '[SUB]', '[/SUB]')}
                            className="text-xs px-2 py-1 bg-blue-100 hover:bg-blue-200 rounded border border-blue-300"
                            title="Add subscript to numerator"
                        >
                            x<sub>n</sub>
                        </button>
                        <button
                            type="button"
                            onClick={() => insertFormatting(numeratorRef, numerator, setNumerator, '**', '**')}
                            className="text-xs px-2 py-1 bg-blue-100 hover:bg-blue-200 rounded border border-blue-300"
                            title="Make bold"
                        >
                            <strong>B</strong>
                        </button>
                        <button
                            type="button"
                            onClick={() => insertFormatting(numeratorRef, numerator, setNumerator, '*', '*')}
                            className="text-xs px-2 py-1 bg-blue-100 hover:bg-blue-200 rounded border border-blue-300"
                            title="Make italic"
                        >
                            <em>I</em>
                        </button>
                    </div>
                </div>

                <label className="block text-sm text-gray-700">Denominator</label>
                <div className="mb-4">
                    <input 
                        ref={denominatorRef}
                        type="text" 
                        value={denominator} 
                        onChange={e => setDenominator(e.target.value)} 
                        className="w-full mt-1 p-2 border rounded" 
                        placeholder="e.g., 4" 
                    />
                    <div className="flex gap-2 mt-1">
                        <button
                            type="button"
                            onClick={() => insertFormatting(denominatorRef, denominator, setDenominator, '[SUP]', '[/SUP]')}
                            className="text-xs px-2 py-1 bg-blue-100 hover:bg-blue-200 rounded border border-blue-300"
                            title="Add superscript to denominator"
                        >
                            x<sup>n</sup>
                        </button>
                        <button
                            type="button"
                            onClick={() => insertFormatting(denominatorRef, denominator, setDenominator, '[SUB]', '[/SUB]')}
                            className="text-xs px-2 py-1 bg-blue-100 hover:bg-blue-200 rounded border border-blue-300"
                            title="Add subscript to denominator"
                        >
                            x<sub>n</sub>
                        </button>
                        <button
                            type="button"
                            onClick={() => insertFormatting(denominatorRef, denominator, setDenominator, '**', '**')}
                            className="text-xs px-2 py-1 bg-blue-100 hover:bg-blue-200 rounded border border-blue-300"
                            title="Make bold"
                        >
                            <strong>B</strong>
                        </button>
                        <button
                            type="button"
                            onClick={() => insertFormatting(denominatorRef, denominator, setDenominator, '*', '*')}
                            className="text-xs px-2 py-1 bg-blue-100 hover:bg-blue-200 rounded border border-blue-300"
                            title="Make italic"
                        >
                            <em>I</em>
                        </button>
                    </div>
                </div>

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
