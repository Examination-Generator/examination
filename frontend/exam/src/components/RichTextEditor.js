import React, { useRef, memo } from 'react';
import EditorToolbar from './EditorToolbar';
import DrawingTool from './DrawingTool';

const RichTextEditor = memo(function RichTextEditor({
    // Content
    text,
    onTextChange,
    inlineImages,
    imagePositions,
    answerLines,
    workingSpaces,
    // Toolbar handlers
    toolbarProps,
    // Drawing
    showDraw,
    onDrawSave,
    onDrawClose,
    // Rendering
    renderContent,
    // Config
    section,
    placeholder,
    textareaRef: externalRef,
    // Image handlers
    onRemoveImage,
    onRemoveLines,
}) {
    const internalRef = useRef(null);
    const textareaRef = externalRef || internalRef;

    return (
        <div className="mb-6">
            {/* Toolbar */}
            <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-bold text-gray-700">
                    {section === 'question' ? 'Question Content *' : 'Answer Content *'}
                </label>
                <EditorToolbar {...toolbarProps} section={section} />
            </div>

            {/* Split display / edit area */}
            <div
                className="relative border-2 border-gray-300 rounded-lg bg-white overflow-hidden"
                style={{ height: '60vh' }}
            >
                {/* Top 60%: rendered preview */}
                <div
                    className="p-4 overflow-y-auto"
                    style={{ height: '60%', whiteSpace: 'pre-wrap' }}
                >
                    {text.length > 0
                        ? renderContent(
                            text,
                            inlineImages,
                            imagePositions,
                            answerLines,
                            onRemoveImage,
                            onRemoveLines,
                            section
                        )
                        : <span className="text-gray-400 pointer-events-none select-none">{placeholder}</span>
                    }
                </div>

                {/* Bottom 40%: raw textarea */}
                <div
                    className="absolute bottom-0 left-0 right-0 bg-white border-t-2 border-gray-300"
                    style={{ height: '40%' }}
                >
                    <textarea
                        ref={textareaRef}
                        value={text}
                        onChange={e => onTextChange(e.target.value)}
                        className="w-full h-full px-4 py-3 focus:ring-2 focus:ring-green-500 focus:outline-none text-sm resize-none"
                        placeholder="Type or edit text here..."
                        style={{ fontFamily: 'monospace' }}
                        required
                    />
                </div>
            </div>

            {/* Drawing panel — only mounted when needed */}
            {showDraw && (
                <div className="mt-4">
                    <DrawingTool
                        onSave={onDrawSave}
                        onClose={onDrawClose}
                        section={section}
                    />
                </div>
            )}
        </div>
    );
});

export default RichTextEditor;