
import React, { useState } from 'react';
import mammoth from 'mammoth';
import * as pdfjsLib from 'pdfjs-dist';

export default function BulkEntry({ onProcessed, onClear, currentIndex, total }) {
    const [bulkText, setBulkText] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        setIsProcessing(true);
        try {
            let text = '';
            if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
                text = await file.text();
            } else if (file.name.endsWith('.docx')) {
                const buf = await file.arrayBuffer();
                const result = await mammoth.extractRawText({ arrayBuffer: buf });
                text = result.value;
            } else if (file.name.endsWith('.pdf')) {
                const buf = await file.arrayBuffer();
                const pdf = await pdfjsLib.getDocument({ data: buf }).promise;
                for (let i = 1; i <= pdf.numPages; i++) {
                    const page = await pdf.getPage(i);
                    const content = await page.getTextContent();
                    text += content.items.map(item => item.str).join(' ') + '\n\n';
                }
            } else {
                alert('Unsupported file. Use .txt, .docx, or .pdf');
                return;
            }
            setBulkText(text);
        } catch (err) {
            alert('Error reading file: ' + err.message);
        } finally {
            setIsProcessing(false);
            e.target.value = '';
        }
    };

    const handleProcess = () => {
        if (!bulkText.trim()) return;
        const sections = bulkText.split('\n\n').filter(s => s.trim());
        onProcessed(sections);
    };

    const handleClear = () => {
        if (window.confirm('Clear all bulk entry data?')) {
            setBulkText('');
            onClear();
        }
    };

    return (
        <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-4 mb-6">
            <h3 className="font-bold text-blue-800 mb-3">📋 Bulk Entry</h3>

            {total > 0 && (
                <div className="mb-3 p-2 bg-blue-100 rounded text-sm text-blue-800 font-semibold">
                    Processing question {currentIndex + 1} of {total}
                </div>
            )}

            <label className="block mb-3">
                <span className="text-sm font-bold text-blue-700">Upload File (.txt, .docx, .pdf)</span>
                <div className="mt-1">
                    <label className="cursor-pointer bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm inline-flex items-center gap-2">
                        {isProcessing ? 'Loading...' : '📁 Browse File'}
                        <input type="file" accept=".txt,.docx,.pdf" onChange={handleFileUpload} className="hidden" />
                    </label>
                </div>
            </label>

            <div className="mb-3">
                <label className="block text-sm font-bold text-blue-700 mb-1">Or Paste Text</label>
                <textarea
                    value={bulkText}
                    onChange={e => setBulkText(e.target.value)}
                    rows={6}
                    className="w-full px-3 py-2 border-2 border-blue-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Paste questions separated by blank lines..."
                />
            </div>

            <div className="flex gap-2">
                <button
                    type="button"
                    onClick={handleProcess}
                    disabled={!bulkText.trim()}
                    className="flex-1 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-semibold disabled:opacity-50"
                >
                    Process ({bulkText.split('\n\n').filter(s => s.trim()).length} questions)
                </button>
                <button
                    type="button"
                    onClick={handleClear}
                    className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-semibold"
                >
                    Clear
                </button>
            </div>
        </div>
    );
}