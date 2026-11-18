import React, { useEffect, useRef, useState } from 'react';
import { renderTextWithImages, Radical } from '../utils/renderTextWithImages';

const EMPTY_FORM = {
    superscriptBefore: '',
    subscriptBefore: '',
    mainText: '',
    superscriptAfter: '',
    subscriptAfter: '',
    squareRoot: false,
    rootDegree: '',
};

const EMPTY_DEGREES = { superscriptBefore: '', subscriptBefore: '', mainText: '', superscriptAfter: '', subscriptAfter: '' };

const INPUT = 'min-w-0 px-2 py-1.5 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 outline-none';

export default function FormulaModal({ open, onClose, onInsert }) {
    const [form, setForm] = useState(EMPTY_FORM);
    // Each field keeps its own root degree, so different roots can sit in different places.
    const [degrees, setDegrees] = useState(EMPTY_DEGREES);
    const fieldRefs = useRef({});

    useEffect(() => {
        if (!open) {
            setForm(EMPTY_FORM);
            setDegrees(EMPTY_DEGREES);
        }
    }, [open]);

    if (!open) return null;

    const updateField = (field, value) => setForm(previous => ({ ...previous, [field]: value }));

    // Wrap the selection (or insert an empty root) using this field's own degree.
    const insertRoot = field => {
        const element = fieldRefs.current[field];
        const value = form[field];
        const start = element?.selectionStart ?? value.length;
        const end = element?.selectionEnd ?? value.length;
        const token = `[ROOT:${encodeURIComponent(degrees[field].trim())}|${value.slice(start, end)}]`;
        updateField(field, value.slice(0, start) + token + value.slice(end));
        setTimeout(() => {
            if (!element) return;
            element.focus();
            element.setSelectionRange(start + token.length - 1, start + token.length - 1);
        }, 0);
    };

    const handleSubmit = event => {
        event.preventDefault();
        if (!form.mainText.trim()) return;
        onInsert(form);
    };

    const preview = text => renderTextWithImages(text || '');

    const field = (key, label, placeholder, extra = {}) => (
        <div>
            <div className="text-xs font-semibold text-gray-600 mb-1">{label}</div>
            <div className="flex gap-1">
                <input
                    ref={el => { fieldRefs.current[key] = el; }}
                    value={form[key]}
                    onChange={event => updateField(key, event.target.value)}
                    className={`${INPUT} flex-1 ${extra.className || ''}`}
                    placeholder={placeholder}
                    {...extra.inputProps}
                />
                <input
                    value={degrees[key]}
                    onChange={event => setDegrees(previous => ({ ...previous, [key]: event.target.value }))}
                    className={`${INPUT} w-11 text-center px-1`}
                    placeholder="n"
                    title="Root degree for this field (blank = square root)"
                />
                <button type="button" onClick={() => insertRoot(key)} title="Insert root in this field"
                    className="px-2 rounded border border-purple-300 bg-purple-100 hover:bg-purple-200 text-lg leading-none">√</button>
            </div>
        </div>
    );

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <button type="button" aria-label="Close" className="absolute inset-0 bg-black/50 cursor-default" onClick={onClose} />
            <form onSubmit={handleSubmit} className="relative z-10 bg-white rounded-xl shadow-2xl w-full max-w-4xl p-5">
                <div className="flex items-center justify-between mb-3">
                    <h3 className="text-lg font-bold text-gray-800">Formula</h3>
                    <button type="button" onClick={onClose} className="text-gray-500 hover:text-gray-800 text-2xl leading-none" aria-label="Close">&times;</button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <div className="space-y-3">
                        {field('superscriptBefore', 'Sup before', 'xⁿ')}
                        {field('subscriptBefore', 'Sub before', 'xₙ')}
                    </div>

                    <div className="space-y-3">
                        {field('mainText', 'Main *', 'Main text', { inputProps: { autoFocus: true, required: true } })}
                        <div className="flex gap-1 items-center">
                            <button type="button" aria-pressed={form.squareRoot}
                                onClick={() => updateField('squareRoot', !form.squareRoot)}
                                title="Wrap the whole formula in a root"
                                className={`flex-1 px-2 py-1.5 rounded border text-sm font-semibold ${form.squareRoot ? 'bg-purple-600 border-purple-600 text-white' : 'bg-purple-100 border-purple-300 hover:bg-purple-200'}`}>
                                √ Wrap all
                            </button>
                            <input
                                value={form.rootDegree}
                                onChange={event => updateField('rootDegree', event.target.value)}
                                disabled={!form.squareRoot}
                                className={`${INPUT} w-11 text-center px-1 disabled:bg-gray-100`}
                                placeholder="n"
                                title="Root degree for the wrap (blank = square root)"
                            />
                        </div>
                    </div>

                    <div className="space-y-3">
                        {field('superscriptAfter', 'Sup after', 'xⁿ')}
                        {field('subscriptAfter', 'Sub after', 'xₙ')}
                    </div>
                </div>

                <div className="mt-4 px-4 py-3 bg-gray-50 rounded-lg flex items-center justify-center min-h-[3.5rem] overflow-x-auto">
                    <span className="inline-flex items-center">
                        <span className="inline-flex flex-col justify-center text-center leading-none mr-1 text-sm">
                            <sup>{preview(form.superscriptBefore)}</sup>
                            <sub>{preview(form.subscriptBefore)}</sub>
                        </span>
                        {form.squareRoot ? (
                            <Radical degree={form.rootDegree.trim() ? preview(form.rootDegree) : null}>
                                {form.mainText ? preview(form.mainText) : 'Equation'}
                            </Radical>
                        ) : (
                            <span>{form.mainText ? preview(form.mainText) : 'X'}</span>
                        )}
                        <span className="inline-flex flex-col justify-center text-center leading-none ml-1 text-sm">
                            <sup>{preview(form.superscriptAfter)}</sup>
                            <sub>{preview(form.subscriptAfter)}</sub>
                        </span>
                    </span>
                </div>

                <div className="flex justify-end gap-3 mt-4">
                    <button type="button" onClick={onClose} className="px-4 py-2 rounded-lg bg-gray-200 hover:bg-gray-300 text-gray-800">Cancel</button>
                    <button type="submit" className="px-4 py-2 rounded-lg bg-green-600 hover:bg-green-700 text-white font-semibold">Insert</button>
                </div>
            </form>
        </div>
    );
}
