// src/components/SubjectsTab.jsx
import React, { useState, useEffect, useCallback } from 'react';
import * as subjectService from '../services/subjectService';
import { useError } from '../contexts/ErrorContext';

export default function SubjectsTab() {
    const { showError, showSuccess } = useError();
    const [subjects, setSubjects] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [expanded, setExpanded] = useState({});
    const [expandedPapers, setExpandedPapers] = useState({});

    // New subject form
    const [subjectName, setSubjectName] = useState('');
    const [papers, setPapers] = useState([{ name: '', durationHours: 2, durationMinutes: 0, topics: [''], sections: [''] }]);

    // Edit modal
    const [editingItem, setEditingItem] = useState(null);
    const [deletingItem, setDeletingItem] = useState(null);

    const load = useCallback(async () => {
        setIsLoading(true);
        try {
            const data = await subjectService.getAllSubjects();
            setSubjects(data);
        } catch (err) {
            showError('Failed to load subjects');
        } finally {
            setIsLoading(false);
        }
    }, [showError]);

    useEffect(() => { load(); }, [load]);

    const handleAddSubject = async (e) => {
        e.preventDefault();
        if (!subjectName.trim()) { showError('Enter a subject name'); return; }
        const validPapers = papers.filter(p => p.name.trim());
        if (validPapers.length === 0) { showError('Add at least one paper'); return; }
        try {
            await subjectService.createSubject({
                name: subjectName.trim(),
                papers: validPapers.map(p => ({
                    name: p.name.trim(),
                    durationHours: p.durationHours,
                    durationMinutes: p.durationMinutes,
                    topics: p.topics.filter(t => t.trim()),
                    sections: p.sections.filter(s => s.trim()),
                })),
            });
            showSuccess(`Subject "${subjectName}" added!`);
            setSubjectName('');
            setPapers([{ name: '', durationHours: 2, durationMinutes: 0, topics: [''], sections: [''] }]);
            load();
        } catch (err) {
            showError(err.message || 'Failed to add subject');
        }
    };

    const handleSaveEdit = async () => {
        if (!editingItem) return;
        try {
            const { type, data } = editingItem;
            if (type === 'subject') await subjectService.updateSubject(data.id, { name: data.name });
            else if (type === 'paper') await subjectService.updatePaper(data.subject.id, data.paper.id, { name: data.paper.name });
            else if (type === 'topic') await subjectService.updateTopic(data.topic.id, { name: data.topic.name });
            else if (type === 'section') await subjectService.updateSection(data.section.id, { name: data.section.name });
            showSuccess('Updated!');
            setEditingItem(null);
            load();
        } catch (err) {
            showError(err.message || 'Failed to update');
        }
    };

    const handleConfirmDelete = async () => {
        if (!deletingItem) return;
        try {
            const { type, data } = deletingItem;
            if (type === 'subject') await subjectService.deleteSubject(data.id);
            else if (type === 'paper') await subjectService.deletePaper(data.subject.id, data.paper.id);
            else if (type === 'topic') await subjectService.deleteTopic(data.topic.id);
            else if (type === 'section') await subjectService.deleteSection(data.section.id);
            showSuccess('Deleted!');
            setDeletingItem(null);
            load();
        } catch (err) {
            showError(err.message || 'Failed to delete');
        }
    };

    // Paper form helpers
    const addPaper = () => setPapers(p => [...p, { name: '', durationHours: 2, durationMinutes: 0, topics: [''], sections: [''] }]);
    const removePaper = (i) => setPapers(p => p.filter((_, idx) => idx !== i));
    const updatePaper = (i, field, val) => setPapers(p => p.map((pp, idx) => idx === i ? { ...pp, [field]: val } : pp));
    const addTopic = (pi) => setPapers(p => p.map((pp, idx) => idx === pi ? { ...pp, topics: [...pp.topics, ''] } : pp));
    const updateTopic = (pi, ti, val) => setPapers(p => p.map((pp, idx) => idx === pi ? { ...pp, topics: pp.topics.map((t, tIdx) => tIdx === ti ? val : t) } : pp));
    const removeTopic = (pi, ti) => setPapers(p => p.map((pp, idx) => idx === pi ? { ...pp, topics: pp.topics.filter((_, tIdx) => tIdx !== ti) } : pp));
    const addSection = (pi) => setPapers(p => p.map((pp, idx) => idx === pi ? { ...pp, sections: [...pp.sections, ''] } : pp));
    const updateSection = (pi, si, val) => setPapers(p => p.map((pp, idx) => idx === pi ? { ...pp, sections: pp.sections.map((s, sIdx) => sIdx === si ? val : s) } : pp));
    const removeSection = (pi, si) => setPapers(p => p.map((pp, idx) => idx === pi ? { ...pp, sections: pp.sections.filter((_, sIdx) => sIdx !== si) } : pp));

    return (
        <div className="space-y-8">
            {/* Existing subjects list */}
            <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-bold text-gray-800">Manage Subjects</h2>
                    <button onClick={load} disabled={isLoading}
                        className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm transition disabled:opacity-50">
                        {isLoading ? 'Loading...' : 'Refresh'}
                    </button>
                </div>

                <div className="max-h-96 overflow-y-auto space-y-3">
                    {subjects.map(subject => (
                        <div key={subject.id} className="border border-gray-300 rounded-lg overflow-hidden">
                            <div className="bg-green-50 p-3 flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <button onClick={() => setExpanded(p => ({ ...p, [subject.id]: !p[subject.id] }))}>
                                        <svg className={`w-5 h-5 transition-transform ${expanded[subject.id] ? 'rotate-90' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                        </svg>
                                    </button>
                                    <h3 className="font-bold text-gray-800">{subject.name}</h3>
                                    <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">{subject.papers?.length || 0} papers</span>
                                </div>
                                <div className="flex gap-1">
                                    <button onClick={() => setEditingItem({ type: 'subject', data: { ...subject } })}
                                        className="text-blue-600 hover:bg-blue-50 p-2 rounded transition">✏️</button>
                                    <button onClick={() => setDeletingItem({ type: 'subject', data: subject })}
                                        className="text-red-600 hover:bg-red-50 p-2 rounded transition">🗑️</button>
                                </div>
                            </div>

                            {expanded[subject.id] && (
                                <div className="p-3 space-y-2 bg-gray-50">
                                    {subject.papers?.map(paper => (
                                        <div key={paper.id} className="bg-white rounded-lg border border-gray-200 overflow-hidden">
                                            <div className="bg-blue-50 p-2 flex items-center justify-between">
                                                <div className="flex items-center gap-2">
                                                    <button onClick={() => setExpandedPapers(p => ({ ...p, [paper.id]: !p[paper.id] }))}>
                                                        <svg className={`w-4 h-4 transition-transform ${expandedPapers[paper.id] ? 'rotate-90' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                                        </svg>
                                                    </button>
                                                    <span className="font-semibold text-sm text-gray-700">{paper.name}</span>
                                                    <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">{paper.topics?.length || 0} topics</span>
                                                </div>
                                                <div className="flex gap-1">
                                                    <button onClick={() => setEditingItem({ type: 'paper', data: { subject, paper: { ...paper } } })}
                                                        className="text-blue-600 hover:bg-blue-50 p-1 rounded text-xs">✏️</button>
                                                    <button onClick={() => setDeletingItem({ type: 'paper', data: { subject, paper } })}
                                                        className="text-red-600 hover:bg-red-50 p-1 rounded text-xs">🗑️</button>
                                                </div>
                                            </div>

                                            {expandedPapers[paper.id] && (
                                                <div className="p-3 grid grid-cols-2 gap-4 text-sm">
                                                    <div>
                                                        <p className="font-semibold text-gray-600 mb-1">Topics:</p>
                                                        {paper.topics?.map(t => (
                                                            <div key={t.id} className="flex items-center justify-between py-0.5">
                                                                <span>{t.name}</span>
                                                                <div className="flex gap-1">
                                                                    <button onClick={() => setEditingItem({ type: 'topic', data: { subject, paper, topic: { ...t } } })} className="text-blue-600 text-xs">✏️</button>
                                                                    <button onClick={() => setDeletingItem({ type: 'topic', data: { subject, paper, topic: t } })} className="text-red-600 text-xs">🗑️</button>
                                                                </div>
                                                            </div>
                                                        ))}
                                                    </div>
                                                    <div>
                                                        <p className="font-semibold text-gray-600 mb-1">Sections:</p>
                                                        {paper.sections?.filter(s => s.name !== 'None').map(s => (
                                                            <div key={s.id} className="flex items-center justify-between py-0.5">
                                                                <span>{s.name}</span>
                                                                <div className="flex gap-1">
                                                                    <button onClick={() => setEditingItem({ type: 'section', data: { subject, paper, section: { ...s } } })} className="text-blue-600 text-xs">✏️</button>
                                                                    <button onClick={() => setDeletingItem({ type: 'section', data: { subject, paper, section: s } })} className="text-red-600 text-xs">🗑️</button>
                                                                </div>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    ))}
                    {subjects.length === 0 && !isLoading && (
                        <p className="text-center text-gray-500 py-8">No subjects yet. Add one below.</p>
                    )}
                </div>
            </div>

            {/* Add new subject form */}
            <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-bold text-gray-800 mb-4">Add New Subject</h2>
                <form onSubmit={handleAddSubject} className="space-y-4">
                    <div>
                        <label className="block text-sm font-bold text-gray-700 mb-2">Subject Name *</label>
                        <input value={subjectName} onChange={e => setSubjectName(e.target.value)}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
                            placeholder="e.g., Mathematics" required />
                    </div>

                    <div>
                        <div className="flex justify-between items-center mb-3">
                            <h3 className="font-bold text-gray-800">Papers</h3>
                            <button type="button" onClick={addPaper}
                                className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm">+ Add Paper</button>
                        </div>

                        {papers.map((paper, pi) => (
                            <div key={pi} className="border border-gray-300 rounded-lg p-4 mb-3">
                                <div className="flex justify-between items-center mb-3">
                                    <h4 className="font-semibold text-gray-700">Paper {pi + 1}</h4>
                                    {papers.length > 1 && (
                                        <button type="button" onClick={() => removePaper(pi)} className="text-red-600 text-sm font-semibold">Remove</button>
                                    )}
                                </div>

                                <input value={paper.name} onChange={e => updatePaper(pi, 'name', e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-green-500 outline-none mb-3"
                                    placeholder="Paper name e.g., Paper 1" required />

                                <div className="flex gap-3 mb-3">
                                    <div className="flex-1">
                                        <label className="text-xs font-semibold text-gray-600">Hours</label>
                                        <input type="number" min="0" max="24" value={paper.durationHours}
                                            onChange={e => updatePaper(pi, 'durationHours', +e.target.value)}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none" />
                                    </div>
                                    <div className="flex-1">
                                        <label className="text-xs font-semibold text-gray-600">Minutes</label>
                                        <input type="number" min="0" max="59" value={paper.durationMinutes}
                                            onChange={e => updatePaper(pi, 'durationMinutes', +e.target.value)}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none" />
                                    </div>
                                </div>

                                {/* Topics */}
                                <div className="mb-3">
                                    <div className="flex justify-between mb-1">
                                        <label className="text-xs font-bold text-gray-600">Topics</label>
                                        <button type="button" onClick={() => addTopic(pi)} className="text-green-600 text-xs font-semibold">+ Topic</button>
                                    </div>
                                    {paper.topics.map((t, ti) => (
                                        <div key={ti} className="flex gap-2 mb-1">
                                            <input value={t} onChange={e => updateTopic(pi, ti, e.target.value)}
                                                className="flex-1 px-3 py-1.5 border border-gray-300 rounded text-sm outline-none"
                                                placeholder={`Topic ${ti + 1}`} />
                                            {paper.topics.length > 1 && (
                                                <button type="button" onClick={() => removeTopic(pi, ti)} className="text-red-600">✕</button>
                                            )}
                                        </div>
                                    ))}
                                </div>

                                {/* Sections */}
                                <div>
                                    <div className="flex justify-between mb-1">
                                        <label className="text-xs font-bold text-gray-600">Sections (optional)</label>
                                        <button type="button" onClick={() => addSection(pi)} className="text-green-600 text-xs font-semibold">+ Section</button>
                                    </div>
                                    {paper.sections.map((s, si) => (
                                        <div key={si} className="flex gap-2 mb-1">
                                            <input value={s} onChange={e => updateSection(pi, si, e.target.value)}
                                                className="flex-1 px-3 py-1.5 border border-gray-300 rounded text-sm outline-none"
                                                placeholder={`Section ${si + 1}`} />
                                            {paper.sections.length > 1 && (
                                                <button type="button" onClick={() => removeSection(pi, si)} className="text-red-600">✕</button>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>

                    <button type="submit" className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 rounded-lg transition">
                        Add Subject
                    </button>
                </form>
            </div>

            {/* Edit Modal */}
            {editingItem && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
                        <h3 className="text-xl font-bold mb-4">Edit {editingItem.type}</h3>
                        <input
                            value={
                                editingItem.type === 'subject' ? editingItem.data.name :
                                editingItem.type === 'paper' ? editingItem.data.paper.name :
                                editingItem.type === 'topic' ? editingItem.data.topic.name :
                                editingItem.data.section.name
                            }
                            onChange={e => {
                                const val = e.target.value;
                                setEditingItem(prev => {
                                    if (prev.type === 'subject') return { ...prev, data: { ...prev.data, name: val } };
                                    if (prev.type === 'paper') return { ...prev, data: { ...prev.data, paper: { ...prev.data.paper, name: val } } };
                                    if (prev.type === 'topic') return { ...prev, data: { ...prev.data, topic: { ...prev.data.topic, name: val } } };
                                    return { ...prev, data: { ...prev.data, section: { ...prev.data.section, name: val } } };
                                });
                            }}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none mb-4" />
                        <div className="flex gap-3">
                            <button onClick={handleSaveEdit} className="flex-1 bg-blue-600 text-white py-3 rounded-lg font-semibold">Save</button>
                            <button onClick={() => setEditingItem(null)} className="flex-1 bg-gray-300 text-gray-800 py-3 rounded-lg font-semibold">Cancel</button>
                        </div>
                    </div>
                </div>
            )}

            {/* Delete Confirm Modal */}
            {deletingItem && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
                        <h3 className="text-xl font-bold text-gray-800 mb-4">Confirm Delete</h3>
                        <p className="text-gray-600 mb-6">
                            Delete <span className="font-semibold">
                                {deletingItem.type === 'subject' ? deletingItem.data.name :
                                 deletingItem.type === 'paper' ? deletingItem.data.paper.name :
                                 deletingItem.type === 'topic' ? deletingItem.data.topic.name :
                                 deletingItem.data.section.name}
                            </span>? This cannot be undone.
                        </p>
                        <div className="flex gap-3">
                            <button onClick={handleConfirmDelete} className="flex-1 bg-red-600 text-white py-3 rounded-lg font-semibold">Delete</button>
                            <button onClick={() => setDeletingItem(null)} className="flex-1 bg-gray-300 text-gray-800 py-3 rounded-lg font-semibold">Cancel</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}