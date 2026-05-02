import React from 'react';

export default function EditorToolbar({
    onImageUpload,
    onToggleDraw,
    onToggleGraph,
    isDrawing,
    isGraph,
    onBold, onItalic, onUnderline,
    onSuperscript, onSubscript,
    onFraction, onTable, onMatrix,
    onSymbols, onLines, onSpace,
    onMic, isListening,
    section = 'question',
}) {
    const accentColor = section === 'question' ? 'blue' : 'orange';

    return (
        <div className="flex items-center gap-2 flex-wrap">
            {/* Image Upload */}
            <label className={`bg-${accentColor}-500 hover:bg-${accentColor}-600 text-white px-3 py-1.5 rounded-lg cursor-pointer transition text-xs flex items-center gap-1.5`}>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                        d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Image
                <input type="file" accept="image/*" multiple onChange={onImageUpload} className="hidden" />
            </label>

            {/* Draw */}
            <button
                type="button"
                onClick={onToggleDraw}
                className={`${isDrawing ? 'bg-purple-600' : 'bg-gray-500'} hover:bg-purple-700 text-white px-3 py-1.5 rounded-lg transition text-xs flex items-center gap-1.5`}
            >
                ✏️ Draw
            </button>

            {/* Graph */}
            <button
                type="button"
                onClick={onToggleGraph}
                className={`${isGraph ? 'bg-green-600' : 'bg-gray-500'} hover:bg-green-700 text-white px-3 py-1.5 rounded-lg transition text-xs flex items-center gap-1.5`}
            >
                📊 Graph
            </button>

            {/* Formatting */}
            <div className="flex items-center gap-1 border-l border-gray-300 pl-2">
                <button type="button" onClick={onBold}
                    className="bg-gray-600 hover:bg-gray-700 text-white px-2 py-1.5 rounded transition text-xs font-bold"
                    title="Bold">B</button>
                <button type="button" onClick={onItalic}
                    className="bg-gray-600 hover:bg-gray-700 text-white px-2 py-1.5 rounded transition text-xs italic"
                    title="Italic">I</button>
                <button type="button" onClick={onUnderline}
                    className="bg-gray-600 hover:bg-gray-700 text-white px-2 py-1.5 rounded transition text-xs underline"
                    title="Underline">U</button>
                <button type="button" onClick={onSuperscript}
                    className="bg-gray-600 hover:bg-gray-700 text-white px-2 py-1.5 rounded transition text-xs"
                    title="Superscript">x<sup className="text-[8px]">2</sup></button>
                <button type="button" onClick={onSubscript}
                    className="bg-gray-600 hover:bg-gray-700 text-white px-2 py-1.5 rounded transition text-xs"
                    title="Subscript">H<sub className="text-[8px]">2</sub></button>
                <button type="button" onClick={onFraction}
                    className="bg-gray-600 hover:bg-gray-700 text-white px-2 py-1.5 rounded transition text-xs"
                    title="Fraction">a⁄b</button>
                <button type="button" onClick={onTable}
                    className="bg-gray-600 hover:bg-gray-700 text-white px-2 py-1.5 rounded transition text-xs"
                    title="Table">⊞</button>
                <button type="button" onClick={onMatrix}
                    className="bg-gray-600 hover:bg-gray-700 text-white px-2 py-1.5 rounded transition text-xs"
                    title="Matrix">⎡⎤</button>
            </div>

            {/* Extra tools */}
            <button type="button" onClick={onSymbols}
                className="bg-indigo-500 hover:bg-indigo-600 text-white px-3 py-1.5 rounded-lg transition text-xs flex items-center gap-1"
                title="Symbols">
                <span className="text-lg leading-none">Ω</span> Symbols
            </button>
            <button type="button" onClick={onLines}
                className="bg-indigo-500 hover:bg-indigo-600 text-white px-3 py-1.5 rounded-lg transition text-xs flex items-center gap-1"
                title="Answer Lines">
                ≡ Lines
            </button>
            <button type="button" onClick={onSpace}
                className="bg-purple-500 hover:bg-purple-600 text-white px-3 py-1.5 rounded-lg transition text-xs flex items-center gap-1"
                title="Working Space">
                □ Space
            </button>
            <button type="button" onClick={onMic}
                className={`${isListening ? 'bg-red-600 animate-pulse' : 'bg-orange-500'} hover:bg-orange-700 text-white px-3 py-1.5 rounded-lg transition text-xs flex items-center gap-1`}
                title={isListening ? 'Stop recording' : 'Voice input'}>
                🎤 {isListening ? 'Recording...' : 'Mic'}
            </button>
        </div>
    );
}