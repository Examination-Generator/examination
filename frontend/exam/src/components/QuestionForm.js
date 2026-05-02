import React, { useState, useCallback, useRef } from 'react';
import RichTextEditor from './RichTextEditor';
import QuestionFlags from './QuestionFlags';
import SymbolPicker from './SymbolPicker';
import FractionModal from './FractionModal';
import TableMatrixModal from './TableMatrixModal';
import { useError } from '../contexts/ErrorContext';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export default function QuestionForm({
    // Subject selection ids
    selectedSubject,
    selectedPaper,
    selectedTopic,
    selectedSection,
    selectedSubjectId,
    selectedPaperId,
    selectedTopicId,
    selectedSectionId,
    // Form state from useQuestionForm hook
    formState,
    // Callbacks
    onSubmitSuccess,
    // Bulk mode
    bulkMode,
    currentBulkIndex,
    totalBulkQuestions,
}) {
    const { showError, showSuccess } = useError();

    const {
        questionText, setQuestionText,
        answerText, setAnswerText,
        marks, setMarks,
        isQuestionActive, setIsQuestionActive,
        isNested, setIsNested,
        isEssayQuestion, setIsEssayQuestion,
        isGraphQuestion, setIsGraphQuestion,
        isMapQuestion, setIsMapQuestion,
        questionInlineImages, setQuestionInlineImages,
        answerInlineImages, setAnswerInlineImages,
        questionImagePositions, setQuestionImagePositions,
        answerImagePositions, setAnswerImagePositions,
        questionAnswerLines, setQuestionAnswerLines,
        answerAnswerLines, setAnswerAnswerLines,
        questionWorkingSpaces, setQuestionWorkingSpaces,
        answerWorkingSpaces, setAnswerWorkingSpaces,
        questionTextareaRef,
        answerTextareaRef,
        resetForm,
    } = formState;

    // Local UI state
    const [showQuestionDraw, setShowQuestionDraw] = useState(false);
    const [showAnswerDraw, setShowAnswerDraw] = useState(false);
    const [showSymbolPicker, setShowSymbolPicker] = useState(false);
    const [symbolTarget, setSymbolTarget] = useState('question');
    const [showFractionModal, setShowFractionModal] = useState(false);
    const [fractionTarget, setFractionTarget] = useState(null);
    const [showTableModal, setShowTableModal] = useState(false);
    const [tableTarget, setTableTarget] = useState(null);
    const [tableType, setTableType] = useState('table');
    const [isSubmitting, setIsSubmitting] = useState(false);

    // ── Formatting helpers ──────────────────────────────────────────────
    const applyFormatting = useCallback((format, textareaRef, setText) => {
        const textarea = textareaRef.current;
        if (!textarea) return;
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const selected = textarea.value.substring(start, end);
        if (!selected) { showError('Please select text to format'); return; }

        const wrapMap = {
            bold: ['**', '**'],
            italic: ['*', '*'],
            underline: ['__', '__'],
            superscript: ['[SUP]', '[/SUP]'],
            subscript: ['[SUB]', '[/SUB]'],
        };
        const [open, close] = wrapMap[format] || ['', ''];
        const formatted = `${open}${selected}${close}`;
        const newText = textarea.value.substring(0, start) + formatted + textarea.value.substring(end);
        setText(newText);
        setTimeout(() => {
            textarea.focus();
            textarea.setSelectionRange(start + formatted.length, start + formatted.length);
        }, 0);
    }, [showError]);

    // ── Symbol insertion ────────────────────────────────────────────────
    const insertSymbol = useCallback((symbol, target) => {
        const ref = target === 'question' ? questionTextareaRef : answerTextareaRef;
        const setText = target === 'question' ? setQuestionText : setAnswerText;
        const textarea = ref.current;
        if (!textarea) { setText(prev => prev + symbol); return; }
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const newText = textarea.value.substring(0, start) + symbol + textarea.value.substring(end);
        setText(newText);
        setTimeout(() => {
            textarea.focus();
            textarea.setSelectionRange(start + symbol.length, start + symbol.length);
        }, 0);
    }, [questionTextareaRef, answerTextareaRef, setQuestionText, setAnswerText]);

    // ── Fraction insert ─────────────────────────────────────────────────
    const openFraction = useCallback((target) => {
        const ref = target === 'question' ? questionTextareaRef : answerTextareaRef;
        const setText = target === 'question' ? setQuestionText : setAnswerText;
        setFractionTarget({ ref, setText });
        setShowFractionModal(true);
    }, [questionTextareaRef, answerTextareaRef, setQuestionText, setAnswerText]);

    const handleFractionInsert = useCallback(({ whole, numerator, denominator }) => {
        if (!fractionTarget) return;
        const { ref, setText } = fractionTarget;
        const token = whole?.trim()
            ? `[MIX:${whole.trim()}:${numerator.trim()}:${denominator.trim()}]`
            : `[FRAC:${numerator.trim()}:${denominator.trim()}]`;
        const textarea = ref?.current;
        if (!textarea) { setText(prev => prev + token); }
        else {
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            setText(textarea.value.substring(0, start) + token + textarea.value.substring(end));
            setTimeout(() => {
                textarea.focus();
                textarea.setSelectionRange(start + token.length, start + token.length);
            }, 0);
        }
        setShowFractionModal(false);
    }, [fractionTarget]);

    // ── Table insert ────────────────────────────────────────────────────
    const openTable = useCallback((target, type) => {
        const ref = target === 'question' ? questionTextareaRef : answerTextareaRef;
        const setText = target === 'question' ? setQuestionText : setAnswerText;
        setTableTarget({ ref, setText });
        setTableType(type);
        setShowTableModal(true);
    }, [questionTextareaRef, answerTextareaRef, setQuestionText, setAnswerText]);

    const handleTableInsert = useCallback(({ rows, cols, data, widths, heights, merged }) => {
        if (!tableTarget) return;
        const { ref, setText } = tableTarget;
        let token = tableType === 'table'
            ? `[TABLE:${rows}x${cols}:${data}${widths ? `:W:${widths}` : ''}${heights ? `:H:${heights}` : ''}${merged ? `:M:${merged}` : ''}]`
            : `[MATRIX:${rows}x${cols}:${data}]`;
        const textarea = ref?.current;
        if (!textarea) { setText(prev => prev + token); }
        else {
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            setText(textarea.value.substring(0, start) + token + textarea.value.substring(end));
        }
        setShowTableModal(false);
    }, [tableTarget, tableType]);

    // ── Image upload ────────────────────────────────────────────────────
    const handleImageUpload = useCallback((e, target) => {
        const setImages = target === 'question' ? setQuestionInlineImages : setAnswerInlineImages;
        const setText = target === 'question' ? setQuestionText : setAnswerText;
        Array.from(e.target.files).forEach(file => {
            if (!file.type.startsWith('image/')) return;
            const reader = new FileReader();
            reader.onload = ev => {
                const img = {
                    id: Date.now() + Math.random(),
                    url: ev.target.result,
                    name: file.name,
                    width: 300,
                    height: 200,
                };
                setImages(prev => [...prev, img]);
                setText(prev => prev + `\n[IMAGE:${img.id}:${img.width}x${img.height}px]\n`);
            };
            reader.readAsDataURL(file);
        });
    }, [setQuestionInlineImages, setAnswerInlineImages, setQuestionText, setAnswerText]);

    // ── Drawing save ────────────────────────────────────────────────────
    const handleDrawSave = useCallback(({ type, imageUrl, width, height, graphBoxesX, graphBoxesY }, target) => {
        const setText = target === 'question' ? setQuestionText : setAnswerText;
        const setImages = target === 'question' ? setQuestionInlineImages : setAnswerInlineImages;

        if (type === 'graph') {
            const id = Date.now() + Math.random();
            setText(prev => prev + `\n[GRAPH:${id}:${graphBoxesX}x${graphBoxesY}cm]\n`);
        } else {
            const img = { id: Date.now() + Math.random(), url: imageUrl, name: `Drawing_${Date.now()}.png`, width, height };
            setImages(prev => [...prev, img]);
            setText(prev => prev + `\n[IMAGE:${img.id}:${img.width}x${img.height}px]\n`);
        }

        if (target === 'question') setShowQuestionDraw(false);
        else setShowAnswerDraw(false);
        showSuccess('Inserted!');
    }, [setQuestionText, setAnswerText, setQuestionInlineImages, setAnswerInlineImages, showSuccess]);

    // ── Answer lines insert ─────────────────────────────────────────────
    const insertLines = useCallback((config, target) => {
        const lineBlock = { id: Date.now() + Math.random(), ...config };
        const setLines = target === 'question' ? setQuestionAnswerLines : setAnswerAnswerLines;
        const ref = target === 'question' ? questionTextareaRef : answerTextareaRef;
        const setText = target === 'question' ? setQuestionText : setAnswerText;
        setLines(prev => [...prev, lineBlock]);
        const textarea = ref.current;
        const token = `\n[LINES:${lineBlock.id}]\n`;
        if (textarea) {
            const pos = textarea.selectionStart;
            setText(prev => prev.substring(0, pos) + token + prev.substring(pos));
        } else {
            setText(prev => prev + token);
        }
    }, [questionTextareaRef, answerTextareaRef, setQuestionText, setAnswerText, setQuestionAnswerLines, setAnswerAnswerLines]);

    // ── Build toolbar props ─────────────────────────────────────────────
    const buildToolbarProps = useCallback((target) => {
        const textareaRef = target === 'question' ? questionTextareaRef : answerTextareaRef;
        const setText = target === 'question' ? setQuestionText : setAnswerText;
        return {
            onImageUpload: e => handleImageUpload(e, target),
            onToggleDraw: () => target === 'question'
                ? setShowQuestionDraw(v => !v)
                : setShowAnswerDraw(v => !v),
            onToggleGraph: () => target === 'question'
                ? setShowQuestionDraw(v => !v)
                : setShowAnswerDraw(v => !v),
            isDrawing: target === 'question' ? showQuestionDraw : showAnswerDraw,
            isGraph: false,
            onBold: () => applyFormatting('bold', textareaRef, setText),
            onItalic: () => applyFormatting('italic', textareaRef, setText),
            onUnderline: () => applyFormatting('underline', textareaRef, setText),
            onSuperscript: () => applyFormatting('superscript', textareaRef, setText),
            onSubscript: () => applyFormatting('subscript', textareaRef, setText),
            onFraction: () => openFraction(target),
            onTable: () => openTable(target, 'table'),
            onMatrix: () => openTable(target, 'matrix'),
            onSymbols: () => { setSymbolTarget(target); setShowSymbolPicker(true); },
            onLines: () => insertLines({
                numberOfLines: 5, lineHeight: 30, lineStyle: 'dotted', opacity: 0.5
            }, target),
            onSpace: () => {
                const token = `\n[SPACE:${Date.now()}]\n`;
                setText(prev => prev + token);
            },
            onMic: () => {}, // voice recording handled separately if needed
            isListening: false,
        };
    }, [
        questionTextareaRef, answerTextareaRef,
        setQuestionText, setAnswerText,
        showQuestionDraw, showAnswerDraw,
        applyFormatting, openFraction, openTable,
        handleImageUpload, insertLines,
    ]);

    // ── Submit ──────────────────────────────────────────────────────────
    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!selectedSubject || !selectedPaper) { showError('Please select subject and paper'); return; }
        if (!selectedSubjectId || !selectedPaperId) { showError('Subject or Paper ID missing. Reselect your options.'); return; }
        if (!questionText.trim()) { showError('Please enter the question text'); return; }
        if (!answerText.trim()) { showError('Please enter the answer text'); return; }
        if (!marks || parseInt(marks) <= 0) { showError('Please enter valid marks'); return; }
        if (!selectedTopicId) { showError('Please select a topic'); return; }

        setIsSubmitting(true);
        try {
            const token = localStorage.getItem('token');
            if (!token) { showError('You must be logged in'); return; }

            const payload = {
                subject: selectedSubjectId,
                paper: selectedPaperId,
                topic: selectedTopicId,
                section: selectedSectionId || null,
                question_text: questionText,
                answer_text: answerText,
                marks: parseInt(marks),
                is_nested: isNested,
                is_essay: isEssayQuestion,
                is_graph: isGraphQuestion,
                is_map: isMapQuestion,
                is_active: isQuestionActive,
                question_inline_images: questionInlineImages,
                answer_inline_images: answerInlineImages,
                question_image_positions: questionImagePositions,
                answer_image_positions: answerImagePositions,
                question_answer_lines: questionAnswerLines,
                answer_answer_lines: answerAnswerLines,
                question_working_spaces: questionWorkingSpaces,
                answer_working_spaces: answerWorkingSpaces,
            };

            const response = await fetch(`${API_URL}/questions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(payload),
            });

            const result = await response.json();
            if (response.ok && result.success) {
                showSuccess('Question saved successfully!');
                resetForm();
                onSubmitSuccess?.(result.data);
            } else {
                showError(`Failed to save: ${result.message || 'Unknown error'}`);
            }
        } catch (err) {
            showError('Error submitting question. Check your connection.');
        } finally {
            setIsSubmitting(false);
        }
    };

    // ── Render content function (passed to RichTextEditor) ──────────────
    // Import your existing renderTextWithImages here or pass it as a prop
    const renderContent = useCallback((text, images, positions, lines, onRemoveImg, onRemoveLines) => {
        // Use your existing renderTextWithImages logic here
        // For brevity pointing to the original function
        return text; // replace with actual render call
    }, []);

    return (
        <>
            {/* Modals */}
            <FractionModal
                open={showFractionModal}
                onClose={() => setShowFractionModal(false)}
                onInsert={handleFractionInsert}
            />
            <TableMatrixModal
                open={showTableModal}
                onClose={() => setShowTableModal(false)}
                onInsert={handleTableInsert}
                type={tableType}
            />
            {showSymbolPicker && (
                <SymbolPicker
                    onInsert={symbol => insertSymbol(symbol, symbolTarget)}
                    onClose={() => setShowSymbolPicker(false)}
                    targetType={symbolTarget}
                />
            )}

            <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-bold text-gray-800 mb-4">
                    Question Entry
                    {bulkMode && ` (${currentBulkIndex + 1} of ${totalBulkQuestions})`}
                </h2>

                {/* Question editor */}
                <RichTextEditor
                    text={questionText}
                    onTextChange={setQuestionText}
                    inlineImages={questionInlineImages}
                    imagePositions={questionImagePositions}
                    answerLines={questionAnswerLines}
                    workingSpaces={questionWorkingSpaces}
                    toolbarProps={buildToolbarProps('question')}
                    showDraw={showQuestionDraw}
                    onDrawSave={result => handleDrawSave(result, 'question')}
                    onDrawClose={() => setShowQuestionDraw(false)}
                    renderContent={renderContent}
                    section="question"
                    placeholder="Start typing your question here..."
                    textareaRef={questionTextareaRef}
                    onRemoveImage={id => {
                        setQuestionInlineImages(prev => prev.filter(img => img.id !== id));
                        setQuestionText(prev => prev.replace(new RegExp(`\\[IMAGE:${id}:\\d+x\\d+px\\]`, 'g'), ''));
                    }}
                    onRemoveLines={id => {
                        setQuestionAnswerLines(prev => prev.filter(l => l.id !== id));
                        setQuestionText(prev => prev.replace(`[LINES:${id}]`, ''));
                    }}
                />

                {/* Answer editor */}
                <RichTextEditor
                    text={answerText}
                    onTextChange={setAnswerText}
                    inlineImages={answerInlineImages}
                    imagePositions={answerImagePositions}
                    answerLines={answerAnswerLines}
                    workingSpaces={answerWorkingSpaces}
                    toolbarProps={buildToolbarProps('answer')}
                    showDraw={showAnswerDraw}
                    onDrawSave={result => handleDrawSave(result, 'answer')}
                    onDrawClose={() => setShowAnswerDraw(false)}
                    renderContent={renderContent}
                    section="answer"
                    placeholder="Start with 'Solution:' or 'Answer:'..."
                    textareaRef={answerTextareaRef}
                    onRemoveImage={id => {
                        setAnswerInlineImages(prev => prev.filter(img => img.id !== id));
                        setAnswerText(prev => prev.replace(new RegExp(`\\[IMAGE:${id}:\\d+x\\d+px\\]`, 'g'), ''));
                    }}
                    onRemoveLines={id => {
                        setAnswerAnswerLines(prev => prev.filter(l => l.id !== id));
                        setAnswerText(prev => prev.replace(`[LINES:${id}]`, ''));
                    }}
                />

                {/* Marks */}
                <div className="mb-6">
                    <label className="block text-sm font-bold text-gray-700 mb-2">Marks *</label>
                    <input
                        type="number"
                        value={marks}
                        onChange={e => setMarks(e.target.value)}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
                        placeholder="Enter marks"
                        min="1"
                        required
                    />
                </div>

                {/* Flags */}
                <QuestionFlags
                    isQuestionActive={isQuestionActive} setIsQuestionActive={setIsQuestionActive}
                    isNested={isNested} setIsNested={setIsNested}
                    isEssayQuestion={isEssayQuestion} setIsEssayQuestion={setIsEssayQuestion}
                    isGraphQuestion={isGraphQuestion} setIsGraphQuestion={setIsGraphQuestion}
                    isMapQuestion={isMapQuestion} setIsMapQuestion={setIsMapQuestion}
                />

                {/* Submit */}
                <button
                    type="submit"
                    disabled={!selectedSubject || !selectedPaper || isSubmitting}
                    className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition shadow-md disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                    {isSubmitting
                        ? 'Saving...'
                        : bulkMode
                            ? `Save & Load Next (${currentBulkIndex + 1}/${totalBulkQuestions})`
                            : isQuestionActive
                                ? 'Submit Active Question'
                                : 'Save Inactive Question'}
                </button>
            </form>
        </>
    );
}