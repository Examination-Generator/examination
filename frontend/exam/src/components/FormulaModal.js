import React, { useEffect, useState } from 'react';

const EMPTY_FORM = {
    superscriptBefore: '',
    subscriptBefore: '',
    mainText: '',
    superscriptAfter: '',
    subscriptAfter: '',
};

export default function FormulaModal({ open, onClose, onInsert }) {
    const [form, setForm] = useState(EMPTY_FORM);

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
                        <input value={form.superscriptBefore} onChange={event => updateField('superscriptBefore', event.target.value)} className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg font-normal focus:ring-2 focus:ring-blue-500 outline-none" placeholder="e.g. n" />
                    </label>
                    <label className="text-sm font-semibold text-gray-700">
                        Subscript before
                        <input value={form.subscriptBefore} onChange={event => updateField('subscriptBefore', event.target.value)} className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg font-normal focus:ring-2 focus:ring-blue-500 outline-none" placeholder="e.g. i" />
                    </label>
                    <label className="sm:col-span-2 text-sm font-semibold text-gray-700">
                        Main text *
                        <input autoFocus required value={form.mainText} onChange={event => updateField('mainText', event.target.value)} className="mt-1 w-full px-3 py-2 border border-blue-300 rounded-lg font-normal focus:ring-2 focus:ring-blue-500 outline-none" placeholder="e.g. H" />
                    </label>
                    <label className="text-sm font-semibold text-gray-700">
                        Superscript after
                        <input value={form.superscriptAfter} onChange={event => updateField('superscriptAfter', event.target.value)} className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg font-normal focus:ring-2 focus:ring-blue-500 outline-none" placeholder="e.g. 2" />
                    </label>
                    <label className="text-sm font-semibold text-gray-700">
                        Subscript after
                        <input value={form.subscriptAfter} onChange={event => updateField('subscriptAfter', event.target.value)} className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg font-normal focus:ring-2 focus:ring-blue-500 outline-none" placeholder="e.g. O" />
                    </label>
                </div>

                <div className="mt-4 p-3 bg-gray-50 rounded-lg text-sm text-gray-700">
                    <span className="font-semibold">Preview: </span>
                    <span className="inline-flex items-center align-middle">
                        <span className="inline-flex flex-col justify-center text-center leading-none mr-1">
                            <sup>{form.superscriptBefore}</sup>
                            <sub>{form.subscriptBefore}</sub>
                        </span>
                        <span>{form.mainText || 'X'}</span>
                        <span className="inline-flex flex-col justify-center text-center leading-none ml-1">
                            <sup>{form.superscriptAfter}</sup>
                            <sub>{form.subscriptAfter}</sub>
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
