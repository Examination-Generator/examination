import React, { useEffect, useRef, useState } from 'react';
import { renderTextWithImages } from '../utils/renderTextWithImages';

const EMPTY_FORM = {
    superscriptBefore: '',
    subscriptBefore: '',
    mainText: '',
    superscriptAfter: '',
    subscriptAfter: '',
    squareRoot: false,
    rootDegree: '',
};

export default function FormulaModal({ open, onClose, onInsert }) {
    const [form, setForm] = useState(EMPTY_FORM);
    const fieldRefs = useRef({});

    // Wrap the selected text (or insert an empty root) in a [ROOT:degree|...] token inside one field.
    const insertRoot = field => {
        const element = fieldRefs.current[field];
        const value = form[field];
        const start = element?.selectionStart ?? value.length;
        const end = element?.selectionEnd ?? value.length;
        const token = `[ROOT:${encodeURIComponent(form.rootDegree.trim())}|${value.slice(start, end)}]`;
        setForm(previous => ({ ...previous, [field]: value.slice(0, start) + token + value.slice(end) }));
        setTimeout(() => {
            if (!element) return;
            element.focus();
            element.setSelectionRange(start + token.length - 1, start + token.length - 1);
        }, 0);
    };

    const rootButton = field => (
        <button type="button" onClick={() => insertRoot(field)} title="Insert a root (uses the root degree above; blank = square root)" className="mt-1 text-xs px-2 py-1 bg-purple-100 hover:bg-purple-200 rounded border border-purple-300 font-normal">
            <sup>{form.rootDegree}</sup>√
        </button>
    );

    const preview = text => renderTextWithImages(text || '');

    useEffect(() => {
        if (!open) setForm(EMPTY_FORM);
    }, [open]);

    if (!open) return null;

    const updateField = (field, value) => {
        setForm(previous => ({ ...previous, [field]: value }));
    };

    const handleSubmit = event => {
        event.preventDefault();
        if (!form.mainText.trim()) return;
        onInsert(form);
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <button
                type="button"
                aria-label="Close formula builder"
                className="absolute inset-0 bg-black/50 cursor-default"
                onClick={onClose}
            />
            <form onSubmit={handleSubmit} className="relative z-10 bg-white rounded-xl shadow-2xl w-full max-w-lg p-6">
                <div className="flex items-start justify-between gap-4 mb-5">
                    <div>
                        <h3 className="text-xl font-bold text-gray-800">Formula Builder</h3>
                        <p className="text-sm text-gray-600 mt-1">Add text before and after the main expression.</p>
                    </div>
                    <button type="button" onClick={onClose} className="text-gray-500 hover:text-gray-800 text-2xl leading-none" aria-label="Close">
                        &times;
                    </button>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <label className="text-sm font-semibold text-gray-700">
                        Superscript before
                        <input ref={el => { fieldRefs.current.superscriptBefore = el; }} value={form.superscriptBefore} onChange={event => updateField('superscriptBefore', event.target.value)} className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg font-normal focus:ring-2 focus:ring-blue-500 outline-none" placeholder="e.g. n" />
                    {rootButton('superscriptBefore')}
                    </label>
                    <label className="text-sm font-semibold text-gray-700">
                        Subscript before
                        <input ref={el => { fieldRefs.current.subscriptBefore = el; }} value={form.subscriptBefore} onChange={event => updateField('subscriptBefore', event.target.value)} className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg font-normal focus:ring-2 focus:ring-blue-500 outline-none" placeholder="e.g. i" />
                    {rootButton('subscriptBefore')}
                    </label>
                    <label className="sm:col-span-2 text-sm font-semibold text-gray-700">
                        Main text *
                        <input ref={el => { fieldRefs.current.mainText = el; }} autoFocus required value={form.mainText} onChange={event => updateField('mainText', event.target.value)} className="mt-1 w-full px-3 py-2 border border-blue-300 rounded-lg font-normal focus:ring-2 focus:ring-blue-500 outline-none" placeholder="e.g. H" />
                    {rootButton('mainText')}
                    </label>
                    <label className="sm:col-span-2 flex items-center gap-2 text-sm font-semibold text-gray-700">
                        <input type="checkbox" checked={form.squareRoot} onChange={event => updateField('squareRoot', event.target.checked)} className="h-4 w-4" />
                        Wrap the complete equation in a square-root symbol
                    </label>
                    <label className="sm:col-span-2 text-sm font-semibold text-gray-700">
                        Root degree (optional)
                        <input
                            value={form.rootDegree}
                            onChange={event => updateField('rootDegree', event.target.value)}
                            className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg font-normal"
                            placeholder="Leave blank for square root; enter 3, 5, n ... for 3rd, 5th, nth root"
                        />
                        <span className="block text-xs font-normal text-gray-500 mt-1">Used by the square-root checkbox above and by the √ buttons under each field.</span>
                    </label>
                    <label className="text-sm font-semibold text-gray-700">
                        Superscript after
                        <input ref={el => { fieldRefs.current.superscriptAfter = el; }} value={form.superscriptAfter} onChange={event => updateField('superscriptAfter', event.target.value)} className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg font-normal focus:ring-2 focus:ring-blue-500 outline-none" placeholder="e.g. 2" />
                    {rootButton('superscriptAfter')}
                    </label>
                    <label className="text-sm font-semibold text-gray-700">
                        Subscript after
                        <input ref={el => { fieldRefs.current.subscriptAfter = el; }} value={form.subscriptAfter} onChange={event => updateField('subscriptAfter', event.target.value)} className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg font-normal focus:ring-2 focus:ring-blue-500 outline-none" placeholder="e.g. O" />
                    {rootButton('subscriptAfter')}
                    </label>
                </div>

                <div className="mt-4 p-3 bg-gray-50 rounded-lg text-sm text-gray-700">
                    <span className="font-semibold">Preview: </span>
                    <span className="inline-flex items-center align-middle">
                        <span className="inline-flex flex-col justify-center text-center leading-none mr-1">
                            <sup>{preview(form.superscriptBefore)}</sup>
                            <sub>{preview(form.subscriptBefore)}</sub>
                        </span>
                        {form.squareRoot ? (
                            <span className="inline-flex items-start">
                                {form.rootDegree.trim() && (
                                    <sup className="text-xs mr-0.5 mt-1">{preview(form.rootDegree)}</sup>
                                )}
                                <span className="text-2xl leading-none">√</span>
                                <span className="border-t-2 border-black px-1 mt-2">{form.mainText ? preview(form.mainText) : 'Equation'}</span>
                            </span>
                        ) : (
                            <span>{form.mainText ? preview(form.mainText) : 'X'}</span>
                        )}
                        <span className="inline-flex flex-col justify-center text-center leading-none ml-1">
                            <sup>{preview(form.superscriptAfter)}</sup>
                            <sub>{preview(form.subscriptAfter)}</sub>
                        </span>
                    </span>
                </div>

                <div className="flex justify-end gap-3 mt-6">
                    <button type="button" onClick={onClose} className="px-4 py-2 rounded-lg bg-gray-200 hover:bg-gray-300 text-gray-800">Cancel</button>
                    <button type="submit" className="px-4 py-2 rounded-lg bg-green-600 hover:bg-green-700 text-white font-semibold">Insert Formula</button>
                </div>
            </form>
        </div>
    );
}
