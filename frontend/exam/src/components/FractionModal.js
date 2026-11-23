import React, { useEffect, useState } from 'react';
import { renderTextWithImages } from '../utils/renderTextWithImages';
import { Slot, defaultExpression, serialize, isComplete } from './ExpressionBuilder';

// Fraction / expression builder: nested fractions, roots, stretchy brackets and stacked scripts,
// serialised to the same tokens the rest of the app already renders.
export default function FractionModal({ open, onClose, onInsert }) {
    const [nodes, setNodes] = useState(defaultExpression);

    useEffect(() => {
        if (!open) setNodes(defaultExpression());
    }, [open]);

    if (!open) return null;

    const token = serialize(nodes).trim();

    const handleInsert = () => {
        if (!token || !isComplete(nodes)) {
            alert('Please fill in every box (numerators, denominators, roots and brackets).');
            return;
        }
        onInsert({ whole: '', numerator: '', denominator: '', expression: token });
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <button type="button" aria-label="Close" className="absolute inset-0 bg-black/50 cursor-default" onClick={onClose} />
            <div className="relative z-10 bg-white rounded-xl shadow-2xl w-full max-w-5xl max-h-[92vh] flex flex-col p-5">
                <div className="flex items-center justify-between mb-3">
                    <h3 className="text-lg font-bold text-gray-800">Fraction / Expression</h3>
                    <button type="button" onClick={onClose} className="text-gray-500 hover:text-gray-800 text-2xl leading-none" aria-label="Close">&times;</button>
                </div>

                <div className="border border-gray-300 rounded-lg p-4 pt-6 overflow-auto min-h-[8rem] bg-white">
                    <Slot nodes={nodes} onChange={setNodes} />
                </div>

                <div className="mt-3 px-4 py-3 bg-gray-50 rounded-lg overflow-x-auto flex items-center justify-center min-h-[5rem]" style={{ fontSize: '1.6rem' }}>
                    {token ? <div>{renderTextWithImages(token)}</div> : <span className="text-gray-400 text-base">Preview</span>}
                </div>

                <div className="flex justify-end gap-3 mt-4">
                    <button type="button" onClick={onClose} className="px-4 py-2 rounded-lg bg-gray-200 hover:bg-gray-300 text-gray-800">Cancel</button>
                    <button type="button" onClick={handleInsert} className="px-4 py-2 rounded-lg bg-green-600 hover:bg-green-700 text-white font-semibold">Insert</button>
                </div>
            </div>
        </div>
    );
}
