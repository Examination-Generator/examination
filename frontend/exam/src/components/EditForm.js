// src/components/EditForm.jsx
import React, { useState, useCallback } from 'react';
import RichTextEditor from './RichTextEditor';
import QuestionFlags from './QuestionFlags';
import SymbolPicker from './SymbolPicker';
import FractionModal from './FractionModal';
import TableMatrixModal from './TableMatrixModal';
import { renderTextWithImages } from '../utils/renderTextWithImages';
import { useError } from '../contexts/ErrorContext';
import * as questionService from '../services/questionService';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export default function EditForm({ editState, onSaved, onDeleted, onCancel }) {
    const { showError, showSuccess } = useError();
    const [showQuestionDraw, setShowQuestionDraw] = useState(false);
    const [showAnswerDraw, setShowAnswerDraw] = useState(false);
    const [showSymbolPicker, setShowSymbolPicker] = useState(false);
    const [symbolTarget, setSymbolTarget] = useState('question');
    const [showFractionModal, setShowFractionModal] = useState(false);
    const [fractionTarget, setFractionTarget] = useState(null);
    const [showTableModal, setShowTableModal] = useState(false);
    const [tableTarget, setTableTarget] = useState(null);
    const [tableType, setTableType] = useState('table');
    const [isSaving, setIsSaving] = useState(false);

    const {
        selectedQuestion,
        editQuestionText, setEditQuestionText,
        editAnswerText, setEditAnswerText,
        editMarks, setEditMarks,
        editTopic, setEditTopic,
        editSection, setEditSection,
        editIsActive, setEditIsActive,
        editIsNested, setEditIsNested,
        editIsEssayQuestion, setEditIsEssayQuestion,
        editIsGraphQuestion, setEditIsGraphQuestion,
        editIsMapQuestion, setEditIsMapQuestion,
        editQuestionInlineImages, setEditQuestionInlineImages,
        editAnswerInlineImages, setEditAnswerInlineImages,
        editQuestionImagePositions,
        editAnswerImagePositions,
        editQuestionAnswerLines, setEditQuestionAnswerLines,
        editAnswerAnswerLines, setEditAnswerAnswerLines,
        editQuestionWorkingSpaces,
        editAnswerWorkingSpaces,
        editQuestionTopics,
        editQuestionSections,
        editQuestionTextareaRef,
        editAnswerTextareaRef,
    } = editState;

    const applyFormat = useCallback((format, ref, setText) => {
        const ta = ref.current;
        if (!ta) return;
        const s = ta.selectionStart, e = ta.selectionEnd;
        const sel = ta.value.substring(s, e);
        if (!sel) { showError('Select text first'); return; }
        const map = { bold: ['**', '**'], italic: ['*', '*'], underline: ['__', '__'], superscript: ['[SUP]', '[/SUP]'], subscript: ['[SUB]', '[/SUB]'] };
        const [o, c] = map[format] || ['', ''];
        const formatted = `${o}${sel}${c}`;
        setText(ta.value.substring(0, s) + formatted + ta.value.substring(e));
        setTimeout(() => { ta.focus(); ta.setSelectionRange(s + formatted.length, s + formatted.length); }, 0);
    }, [showError]);

    const insertSym = useCallback((sym, target) => {
        const ref = target === 'question' ? editQuestionTextareaRef : editAnswerTextareaRef;
        const setText = target === 'question' ? setEditQuestionText : setEditAnswerText;
        const ta = ref.current;
        if (!ta) { setText(p => p + sym); return; }
        const s = ta.selectionStart, e = ta.selectionEnd;
        setText(ta.value.substring(0, s) + sym + ta.value.substring(e));
        setTimeout(() => { ta.focus(); ta.setSelectionRange(s + sym.length, s + sym.length); }, 0);
    }, [editQuestionTextareaRef, editAnswerTextareaRef, setEditQuestionText, setEditAnswerText]);

    const buildToolbar = useCallback((target) => {
        const ref = target === 'question' ? editQuestionTextareaRef : editAnswerTextareaRef;
        const setText = target === 'question' ? setEditQuestionText : setEditAnswerText;
        const setImages = target === 'question' ? setEditQuestionInlineImages : setEditAnswerInlineImages;

        return {
            onImageUpload: (e) => {
                Array.from(e.target.files).forEach(file => {
                    if (!file.type.startsWith('image/')) return;
                    const reader = new FileReader();
                    reader.onload = ev => {
                        const img = { id: Date.now() + Math.random(), url: ev.target.result, name: file.name, width: 300, height: 200 };
                        setImages(p => [...p, img]);
                        setText(p => p + `\n[IMAGE:${img.id}:${img.width}x${img.height}px]\n`);
                    };
                    reader.readAsDataURL(file);
                });
            },
            onToggleDraw: () => target === 'question' ? setShowQuestionDraw(v => !v) : setShowAnswerDraw(v => !v),
            onToggleGraph: () => target === 'question' ? setShowQuestionDraw(v => !v) : setShowAnswerDraw(v => !v),
            isDrawing: target === 'question' ? showQuestionDraw : showAnswerDraw,
            isGraph: false,
            onBold: () => applyFormat('bold', ref, setText),
            onItalic: () => applyFormat('italic', ref, setText),
            onUnderline: () => applyFormat('underline', ref, setText),
            onSuperscript: () => applyFormat('superscript', ref, setText),
            onSubscript: () => applyFormat('subscript', ref, setText),
            onFraction: () => { setFractionTarget({ ref, setText }); setShowFractionModal(true); },
            onTable: () => { setTableTarget({ ref, setText }); setTableType('table'); setShowTableModal(true); },
            onMatrix: () => { setTableTarget({ ref, setText }); setTableType('matrix'); setShowTableModal(true); },
            onSymbols: () => { setSymbolTarget(target); setShowSymbolPicker(true); },
            onLines: () => {
                const block = { id: Date.now() + Math.random(), numberOfLines: 5, lineHeight: 30, lineStyle: 'dotted', opacity: 0.5 };
                if (target === 'question') setEditQuestionAnswerLines(p => [...p, block]);
                else setEditAnswerAnswerLines(p => [...p, block]);
                setText(p => p + `\n[LINES:${block.id}]\n`);
            },
            onSpace: () => setText(p => p + `\n[SPACE:${Date.now()}]\n`),
            onMic: () => {},
            isListening: false,
        };
    }, [
        editQuestionTextareaRef, editAnswerTextareaRef,
        setEditQuestionText, setEditAnswerText,
        setEditQuestionInlineImages, setEditAnswerInlineImages,
        showQuestionDraw, showAnswerDraw,
        applyFormat,
        setEditQuestionAnswerLines, setEditAnswerAnswerLines,
    ]);

    const handleDrawSave = useCallback(({ type, imageUrl, width, height, graphBoxesX, graphBoxesY }, target) => {
        const setText = target === 'question' ? setEditQuestionText : setEditAnswerText;
        const setImages = target === 'question' ? setEditQuestionInlineImages : setEditAnswerInlineImages;
        if (type === 'graph') {
            setText(p => p + `\n[GRAPH:${Date.now()}:${graphBoxesX}x${graphBoxesY}cm]\n`);
        } else {
            const img = { id: Date.now() + Math.random(), url: imageUrl, name: `Drawing_${Date.now()}.png`, width, height };
            setImages(p => [...p, img]);
            setText(p => p + `\n[IMAGE:${img.id}:${img.width}x${img.height}px]\n`);
        }
        if (target === 'question') setShowQuestionDraw(false);
        else setShowAnswerDraw(false);
    }, [setEditQuestionText, setEditAnswerText, setEditQuestionInlineImages, setEditAnswerInlineImages]);

    const handleSave = async (e) => {
        e.preventDefault();
        if (!editQuestionText.trim() || !editAnswerText.trim()) {
            showError('Question and answer text are required');
            return;
        }
        setIsSaving(true);
        try {
            const payload = {
                subject: selectedQuestion.subject,
                paper: selectedQuestion.paper,
                topic: editTopic || selectedQuestion.topic,
                section: editSection || selectedQuestion.section || null,
                question_text: editQuestionText,
                answer_text: editAnswerText,
                marks: parseFloat(editMarks) || selectedQuestion.marks,
                is_active: editIsActive,
                is_nested: editIsNested,
                is_essay: editIsEssayQuestion,
                is_graph: editIsGraphQuestion,
                is_map: editIsMapQuestion,
                question_inline_images: editQuestionInlineImages,
                answer_inline_images: editAnswerInlineImages,
                question_image_positions: editQuestionImagePositions,
                answer_image_positions: editAnswerImagePositions,
                question_answer_lines: editQuestionAnswerLines,
                answer_answer_lines: editAnswerAnswerLines,
                question_working_spaces: editQuestionWorkingSpaces,
                answer_working_spaces: editAnswerWorkingSpaces,
            };
            await questionService.updateQuestion(selectedQuestion.id, payload);
            showSuccess('Question updated!');
            onSaved?.();
        } catch (err) {
            showError('Failed to update: ' + err.message);
        } finally {
            setIsSaving(false);
        }
    };

    const handleDelete = async () => {
        if (!window.confirm('Delete this question? This cannot be undone.')) return;
        try {
            await questionService.deleteQuestion(selectedQuestion.id);
            showSuccess('Question deleted!');
            onDeleted?.();
        } catch (err) {
            showError('Failed to delete: ' + err.message);
        }
    };

    const renderContent = useCallback((text, images, positions, lines, onRemoveImg, onRemoveLines) =>
        renderTextWithImages(text, images, positions, lines, onRemoveImg, onRemoveLines, 'edit'),
    []);

    if (!selectedQuestion) return null;

    return (
        <>
            <FractionModal open={showFractionModal} onClose={() => setShowFractionModal(false)}
                onInsert={({ whole, numerator, denominator }) => {
                    if (!fractionTarget) return;
                    const token = whole?.trim()
                        ? `[MIX:${whole.trim()}:${numerator.trim()}:${denominator.trim()}]`
                        : `[FRAC:${numerator.trim()}:${denominator.trim()}]`;
                    const ta = fractionTarget.ref?.current;
                    if (ta) {
                        const s = ta.selectionStart;
                        fractionTarget.setText(ta.value.substring(0, s) + token + ta.value.substring(s));
                    } else { fractionTarget.setText(p => p + token); }
                    setShowFractionModal(false);
                }} />

            <TableMatrixModal open={showTableModal} onClose={() => setShowTableModal(false)} type={tableType}
                onInsert={({ rows, cols, data, widths, heights, merged }) => {
                    if (!tableTarget) return;
                    const token = tableType === 'table'
                        ? `[TABLE:${rows}x${cols}:${data}${widths ? `:W:${widths}` : ''}${heights ? `:H:${heights}` : ''}${merged ? `:M:${merged}` : ''}]`
                        : `[MATRIX:${rows}x${cols}:${data}]`;
                    const ta = tableTarget.ref?.current;
                    if (ta) {
                        const s = ta.selectionStart;
                        tableTarget.setText(ta.value.substring(0, s) + token + ta.value.substring(s));
                    } else { tableTarget.setText(p => p + token); }
                    setShowTableModal(false);
                }} />

            {showSymbolPicker && (
                <SymbolPicker
                    onInsert={sym => insertSym(sym, symbolTarget)}
                    onClose={() => setShowSymbolPicker(false)}
                    targetType={symbolTarget} />
            )}

            <form onSubmit={handleSave} className="bg-white rounded-xl shadow-lg p-6">
                {/* Header */}
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-bold text-gray-800">Edit Question</h2>
                    <div className="flex gap-2">
                        <button type="button" onClick={onCancel}
                            className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition text-sm">
                            Cancel
                        </button>
                        <button type="button" onClick={handleDelete}
                            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition text-sm">
                            Delete
                        </button>
                        <button type="submit" disabled={isSaving}
                            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition text-sm disabled:opacity-50">
                            {isSaving ? 'Saving...' : 'Save Changes'}
                        </button>
                    </div>
                </div>

                {/* Meta info */}
                <div className="mb-6 p-4 bg-gray-50 rounded-lg grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div>
                        <span className="font-semibold text-gray-700">Subject: </span>
                        <span className="text-gray-600">{selectedQuestion.subject_name}</span>
                    </div>
                    <div>
                        <span className="font-semibold text-gray-700">Paper: </span>
                        <span className="text-gray-600">{selectedQuestion.paper_name}</span>
                    </div>
                    <div>
                        <label className="font-semibold text-gray-700 block mb-1">Topic</label>
                        <select value={editTopic} onChange={e => setEditTopic(e.target.value)}
                            className="w-full px-3 py-1.5 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500">
                            <option value="">Select topic...</option>
                            {editQuestionTopics.map(t => (
                                <option key={t.id} value={t.id}>{t.name}</option>
                            ))}
                        </select>
                    </div>
                    {editQuestionSections.length > 0 && (
                        <div>
                            <label className="font-semibold text-gray-700 block mb-1">Section</label>
                            <select value={editSection} onChange={e => setEditSection(e.target.value)}
                                className="w-full px-3 py-1.5 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500">
                                <option value="">Select section...</option>
                                {editQuestionSections.map(s => (
                                    <option key={s.id} value={s.id}>{s.name}</option>
                                ))}
                            </select>
                        </div>
                    )}
                </div>

                {/* Question editor */}
                <RichTextEditor
                    text={editQuestionText}
                    onTextChange={setEditQuestionText}
                    inlineImages={editQuestionInlineImages}
                    imagePositions={editQuestionImagePositions}
                    answerLines={editQuestionAnswerLines}
                    workingSpaces={editQuestionWorkingSpaces}
                    toolbarProps={buildToolbar('question')}
                    showDraw={showQuestionDraw}
                    onDrawSave={r => handleDrawSave(r, 'question')}
                    onDrawClose={() => setShowQuestionDraw(false)}
                    renderContent={renderContent}
                    section="question"
                    placeholder="Edit question..."
                    textareaRef={editQuestionTextareaRef}
                    onRemoveImage={id => {
                        setEditQuestionInlineImages(p => p.filter(i => i.id !== id));
                        setEditQuestionText(p => p.replace(new RegExp(`\\[IMAGE:${id}:\\d+x\\d+px\\]`, 'g'), ''));
                    }}
                    onRemoveLines={id => {
                        setEditQuestionAnswerLines(p => p.filter(l => l.id !== id));
                        setEditQuestionText(p => p.replace(`[LINES:${id}]`, ''));
                    }}
                />

                {/* Answer editor */}
                <RichTextEditor
                    text={editAnswerText}
                    onTextChange={setEditAnswerText}
                    inlineImages={editAnswerInlineImages}
                    imagePositions={editAnswerImagePositions}
                    answerLines={editAnswerAnswerLines}
                    workingSpaces={editAnswerWorkingSpaces}
                    toolbarProps={buildToolbar('answer')}
                    showDraw={showAnswerDraw}
                    onDrawSave={r => handleDrawSave(r, 'answer')}
                    onDrawClose={() => setShowAnswerDraw(false)}
                    renderContent={renderContent}
                    section="answer"
                    placeholder="Edit answer..."
                    textareaRef={editAnswerTextareaRef}
                    onRemoveImage={id => {
                        setEditAnswerInlineImages(p => p.filter(i => i.id !== id));
                        setEditAnswerText(p => p.replace(new RegExp(`\\[IMAGE:${id}:\\d+x\\d+px\\]`, 'g'), ''));
                    }}
                    onRemoveLines={id => {
                        setEditAnswerAnswerLines(p => p.filter(l => l.id !== id));
                        setEditAnswerText(p => p.replace(`[LINES:${id}]`, ''));
                    }}
                />

                {/* Marks */}
                <div className="mb-6">
                    <label className="block text-sm font-bold text-gray-700 mb-2">Marks</label>
                    <input type="number" value={editMarks} onChange={e => setEditMarks(e.target.value)}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                        step="0.5" min="0" />
                </div>

                {/* Flags */}
                <QuestionFlags
                    isQuestionActive={editIsActive} setIsQuestionActive={setEditIsActive}
                    isNested={editIsNested} setIsNested={setEditIsNested}
                    isEssayQuestion={editIsEssayQuestion} setIsEssayQuestion={setEditIsEssayQuestion}
                    isGraphQuestion={editIsGraphQuestion} setIsGraphQuestion={setEditIsGraphQuestion}
                    isMapQuestion={editIsMapQuestion} setIsMapQuestion={setEditIsMapQuestion}
                />
            </form>
        </>
    );
}