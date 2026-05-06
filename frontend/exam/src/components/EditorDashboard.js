// src/components/EditorDashboard.jsx
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useQuestionForm } from '../hooks/useQuestionForm';
import { usePagination } from '../hooks/usePagination';
import SubjectSelector from './SubjectSelector';
import QuestionForm from './QuestionForm';
import BulkEntry from './BulkEntry';
import SimilarQuestions from './SimilarQuestions';
import StatsTab from './StatsTab';
import SubjectsTab from './SubjectsTab';
import EditTab from './EditTab';
import MessagingTab from './MessagingTab';
import PrintableDocumentModal from './PrintableDocumentModal';
import FractionModal from './FractionModal';
import TableMatrixModal from './TableMatrixModal';
import { renderTextWithImages } from '../utils/renderTextWithImages';
import * as subjectService from '../services/subjectService';
import * as questionService from '../services/questionService';
import * as authService from '../services/authService';
import { getPrintableDocument } from '../services/paperService';
import { useError } from '../contexts/ErrorContext';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export default function EditorDashboard({ onLogout }) {
    const { showError, showSuccess } = useError();

    // ── Tab ────────────────────────────────────────────────────────────
    const [activeTab, setActiveTab] = useState(() => {
        try { return localStorage.getItem('editorActiveTab') || 'questions'; }
        catch { return 'questions'; }
    });

    useEffect(() => {
        try { localStorage.setItem('editorActiveTab', activeTab); }
        catch {}
    }, [activeTab]);

    // ── Subjects data ──────────────────────────────────────────────────
    const [subjects, setSubjects] = useState({});
    const [existingSubjects, setExistingSubjects] = useState([]);
    const [isLoadingSubjects, setIsLoadingSubjects] = useState(false);

    // ── Subject selection ──────────────────────────────────────────────
    const [selectedSubject, setSelectedSubject] = useState('');
    const [selectedPaper, setSelectedPaper] = useState('');
    const [selectedTopic, setSelectedTopic] = useState('');
    const [selectedSection, setSelectedSection] = useState('');
    const [selectedSubjectId, setSelectedSubjectId] = useState('');
    const [selectedPaperId, setSelectedPaperId] = useState('');
    const [selectedTopicId, setSelectedTopicId] = useState('');
    const [selectedSectionId, setSelectedSectionId] = useState('');

    // ── Form state ─────────────────────────────────────────────────────
    const formState = useQuestionForm();

    // ── Bulk entry ─────────────────────────────────────────────────────
    const [showBulkEntry, setShowBulkEntry] = useState(false);
    const [bulkQuestions, setBulkQuestions] = useState([]);
    const [currentBulkIndex, setCurrentBulkIndex] = useState(0);

    // New Subject Form States (borrowed from EditorDashboard1 implementation)
    const [newSubjectName, setNewSubjectName] = useState('');
    const [newSubjectPapers, setNewSubjectPapers] = useState([{ name: '', topics: [''], sections: [''], durationHours: 2, durationMinutes: 0 }]);

    // ── Similar questions ──────────────────────────────────────────────
    const [similarQuestions, setSimilarQuestions] = useState([]);
    const [isSearchingSimilar, setIsSearchingSimilar] = useState(false);

    // ── Printable modal ────────────────────────────────────────────────
    const [showPrintable, setShowPrintable] = useState(false);
    const [printableHtml, setPrintableHtml] = useState('');
    const [printableTitle, setPrintableTitle] = useState('');
    const [isLoadingPrintable, setIsLoadingPrintable] = useState(false);

    // ── Load subjects ──────────────────────────────────────────────────
    const loadSubjects = useCallback(async () => {
        setIsLoadingSubjects(true);
        try {
            const data = await subjectService.getAllSubjects();
            setExistingSubjects(data);

            const transformed = {};
            data.forEach(subject => {
                if (subject.isActive === false) return;
                const papersMap = {};
                const sectionsMap = {};
                const topicsMap = {};
                (subject.papers || []).forEach(paper => {
                    if (paper.isActive === false || !paper.name) return;
                    papersMap[paper.name] = paper;
                    sectionsMap[paper.name] = (paper.sections || []).filter(s => s?.name).map(s => s.name);
                    topicsMap[paper.name] = (paper.topics || []).filter(t => t?.name).map(t => t.name);
                });
                transformed[subject.name] = {
                    papers: Object.keys(papersMap),
                    sections: sectionsMap,
                    topics: topicsMap,
                    papersData: papersMap,
                    id: subject.id,
                };
            });
            setSubjects(transformed);
        } catch (err) {
            console.error('Failed to load subjects:', err);
        } finally {
            setIsLoadingSubjects(false);
        }
    }, []);

    useEffect(() => { loadSubjects(); }, [loadSubjects]);
    useEffect(() => {
        if (activeTab === 'questions' || activeTab === 'subjects') loadSubjects();
    }, [activeTab, loadSubjects]);

    // New Subject Management Functions (borrowed)
    const addPaper = () => {
        setNewSubjectPapers([...newSubjectPapers, { name: '', topics: [''], sections: [''], durationHours: 2, durationMinutes: 0 }]);
    };

    const removePaper = (index) => {
        const updated = newSubjectPapers.filter((_, i) => i !== index);
        setNewSubjectPapers(updated);
    };

    const updatePaperName = (index, name) => {
        const updated = [...newSubjectPapers];
        updated[index].name = name;
        setNewSubjectPapers(updated);
    };

    const updatePaperDuration = (index, field, value) => {
        const updated = [...newSubjectPapers];
        const numValue = parseInt(value) || 0;
        if (field === 'hours') {
            updated[index].durationHours = Math.max(0, Math.min(24, numValue));
        } else if (field === 'minutes') {
            updated[index].durationMinutes = Math.max(0, Math.min(59, numValue));
        }
        setNewSubjectPapers(updated);
    };

    const addTopic = (paperIndex) => {
        const updated = [...newSubjectPapers];
        updated[paperIndex].topics.push('');
        setNewSubjectPapers(updated);
    };

    const updateTopic = (paperIndex, topicIndex, value) => {
        const updated = [...newSubjectPapers];
        updated[paperIndex].topics[topicIndex] = value;
        setNewSubjectPapers(updated);
    };

    const removeTopic = (paperIndex, topicIndex) => {
        const updated = [...newSubjectPapers];
        updated[paperIndex].topics = updated[paperIndex].topics.filter((_, i) => i !== topicIndex);
        setNewSubjectPapers(updated);
    };

    const addSection = (paperIndex) => {
        const updated = [...newSubjectPapers];
        updated[paperIndex].sections.push('');
        setNewSubjectPapers(updated);
    };

    const updateSection = (paperIndex, sectionIndex, value) => {
        const updated = [...newSubjectPapers];
        updated[paperIndex].sections[sectionIndex] = value;
        setNewSubjectPapers(updated);
    };

    const removeSection = (paperIndex, sectionIndex) => {
        const updated = [...newSubjectPapers];
        updated[paperIndex].sections = updated[paperIndex].sections.filter((_, i) => i !== sectionIndex);
        setNewSubjectPapers(updated);
    };

    const handleSubmitNewSubject = async (e) => {
        e.preventDefault();
        if (!newSubjectName.trim()) { showError('Please enter a subject name'); return; }
        const validPapers = newSubjectPapers.filter(p => p.name.trim() !== '');
        if (validPapers.length === 0) { showError('Please add at least one paper'); return; }
        const subjectData = {
            name: newSubjectName.trim(),
            papers: validPapers.map(paper => ({
                name: paper.name.trim(),
                durationHours: paper.durationHours || 2,
                durationMinutes: paper.durationMinutes || 0,
                topics: paper.topics.filter(t => t.trim() !== ''),
                sections: paper.sections.filter(s => s.trim() !== '').length > 0 ? paper.sections.filter(s => s.trim() !== '') : []
            }))
        };
        try {
            const result = await subjectService.createSubject(subjectData);
            setExistingSubjects(prev => [...prev, result]);
            showSuccess(`Subject "${newSubjectName}" added successfully!`);
            setNewSubjectName('');
            setNewSubjectPapers([{ name: '', topics: [''], sections: [''], durationHours: 2, durationMinutes: 0 }]);
            // refresh
            setTimeout(() => { loadSubjects(); }, 500);
        } catch (error) {
            showError(error.message || 'Failed to add subject. Please try again.');
        }
    };

    // ── Subject selection handlers ─────────────────────────────────────
    const handleSubjectChange = useCallback((subject) => {
        setSelectedSubject(subject);
        setSelectedPaper(''); setSelectedTopic(''); setSelectedSection('');
        setSelectedSubjectId(subjects[subject]?.id || '');
        setSelectedPaperId(''); setSelectedTopicId(''); setSelectedSectionId('');
    }, [subjects]);

    const handlePaperChange = useCallback((paper) => {
        setSelectedPaper(paper);
        setSelectedTopic(''); setSelectedSection('');
        setSelectedPaperId(subjects[selectedSubject]?.papersData?.[paper]?.id || '');
        setSelectedTopicId(''); setSelectedSectionId('');
    }, [subjects, selectedSubject]);

    const handleTopicChange = useCallback((topic) => {
        setSelectedTopic(topic);
        const paperData = subjects[selectedSubject]?.papersData?.[selectedPaper];
        const topicData = paperData?.topics?.find(t => t.name === topic);
        setSelectedTopicId(topicData?.id || '');
    }, [subjects, selectedSubject, selectedPaper]);

    const handleSectionChange = useCallback((section) => {
        setSelectedSection(section);
        const paperData = subjects[selectedSubject]?.papersData?.[selectedPaper];
        const sectionData = paperData?.sections?.find(s => s.name === section);
        setSelectedSectionId(sectionData?.id || '');
    }, [subjects, selectedSubject, selectedPaper]);

    // ── Similar questions search ───────────────────────────────────────
    useEffect(() => {
        if (formState.questionText.length <= 15 || !selectedSubject) {
            setSimilarQuestions([]);
            return;
        }
        const timer = setTimeout(async () => {
            setIsSearchingSimilar(true);
            try {
                const token = localStorage.getItem('token');
                const clean = formState.questionText
                    .replace(/\[IMAGE:[\d.]+:(?:\d+x\d+|\d+)px\]/g, '')
                    .replace(/\[GRAPH:[\d.]+:[\d.]+x[\d.]+cm\]/g, '')
                    .trim();
                if (clean.length < 15) { setSimilarQuestions([]); return; }

                const res = await fetch(`${API_URL}/questions/search-similar/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                    body: JSON.stringify({ question_text: clean, subject: selectedSubject, limit: 5 }),
                });
                if (res.ok) {
                    const data = await res.json();
                    setSimilarQuestions(data.data?.similar_questions || data.similar_questions || []);
                } else {
                    setSimilarQuestions([]);
                }
            } catch { setSimilarQuestions([]); }
            finally { setIsSearchingSimilar(false); }
        }, 800);
        return () => clearTimeout(timer);
    }, [formState.questionText, selectedSubject]);

    // ── Bulk entry handlers ────────────────────────────────────────────
    const handleBulkProcessed = useCallback((sections) => {
        setBulkQuestions(sections);
        setCurrentBulkIndex(0);
        if (sections.length > 0) formState.setQuestionText(sections[0]);
    }, [formState]);

    const handleBulkClear = useCallback(() => {
        setBulkQuestions([]);
        setCurrentBulkIndex(0);
        formState.setQuestionText('');
        formState.setAnswerText('');
    }, [formState]);

    // ── Submit success ─────────────────────────────────────────────────
    const handleSubmitSuccess = useCallback(() => {
        if (bulkQuestions.length > 0) {
            const next = currentBulkIndex + 1;
            if (next < bulkQuestions.length) {
                setCurrentBulkIndex(next);
                formState.setQuestionText(bulkQuestions[next]);
                formState.setAnswerText('');
            } else {
                showSuccess('All bulk questions processed!');
                setBulkQuestions([]);
                setCurrentBulkIndex(0);
                setShowBulkEntry(false);
            }
        }
    }, [bulkQuestions, currentBulkIndex, formState, showSuccess]);

    // ── Printable modal ────────────────────────────────────────────────
    const handleOpenPrintableByPaper = useCallback(async (paperData) => {
        if (!paperData.subjectId || !paperData.paperId) {
            showError('Missing subject or paper ID');
            return;
        }
        setIsLoadingPrintable(true);
        setPrintableTitle(paperData.paper);
        setShowPrintable(true);
        setPrintableHtml('');
        try {
            const html = await getPrintableDocument(paperData.subjectId, { paperId: paperData.paperId });
            setPrintableHtml(html);
        } catch (err) {
            showError('Failed to generate document: ' + err.message);
            setShowPrintable(false);
        } finally {
            setIsLoadingPrintable(false);
        }
    }, [showError]);

    const handleOpenPrintableByTopic = useCallback(async (topicData) => {
        if (!topicData.subjectId || !topicData.topicId) {
            showError('Missing subject or topic ID');
            return;
        }
        setIsLoadingPrintable(true);
        setPrintableTitle(topicData.topic || 'Topic');
        setShowPrintable(true);
        setPrintableHtml('');
        try {
            const html = await getPrintableDocument(topicData.subjectId, { topicId: topicData.topicId });
            setPrintableHtml(html);
        } catch (err) {
            showError('Failed to generate document: ' + err.message);
            setShowPrintable(false);
        } finally {
            setIsLoadingPrintable(false);
        }
    }, [showError]);

    // ── Render content passed to QuestionForm ──────────────────────────
    const renderContent = useCallback((text, images, positions, lines, onRemoveImg, onRemoveLines) =>
        renderTextWithImages(text, images, positions, lines, onRemoveImg, onRemoveLines, 'preview'),
    []);

    // ── Tabs config ────────────────────────────────────────────────────
    const tabs = [
        { id: 'questions', label: 'Add Questions' },
        { id: 'stats', label: 'Statistics' },
        { id: 'subjects', label: 'Add New Subject' },
        { id: 'edit', label: 'Edit Questions' },
        { id: 'messaging', label: 'Messaging' },
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100">
            {/* Header */}
            <header className="bg-white shadow-md">
                <div className="max-w-8xl mx-auto px-4 py-4 flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <img src="/exam.png" alt="Logo" className="w-12 h-12 object-contain" />
                        <h1 className="text-2xl font-bold text-green-600">Editor Dashboard</h1>
                    </div>
                    <button
                        onClick={() => { authService.logout(); onLogout(); }}
                        className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition">
                        Logout
                    </button>
                </div>
            </header>

            {/* Navigation */}
            <div className="max-w-8xl mx-auto px-4 pt-6">
                <div className="bg-white rounded-lg shadow-md p-1 flex flex-wrap gap-1">
                    {tabs.map(tab => (
                        <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                            className={`flex-1 min-w-[140px] py-3 px-4 rounded-lg font-semibold transition ${
                                activeTab === tab.id
                                    ? 'bg-green-600 text-white shadow-md'
                                    : 'text-gray-600 hover:bg-gray-50'
                            }`}>
                            {tab.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Content */}
            <div className="max-w-8xl mx-auto px-4 py-8">

                {/*  Questions Tab  */}
                {activeTab === 'questions' && (
                    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                        <div className="lg:col-span-3 space-y-6">
                            {/* Bulk entry toggle */}
                            <div className="flex justify-end">
                                <button onClick={() => setShowBulkEntry(v => !v)}
                                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition">
                                    {showBulkEntry ? 'Hide' : 'Show'} Bulk Entry
                                </button>
                            </div>

                            {showBulkEntry && (
                                <BulkEntry
                                    onProcessed={handleBulkProcessed}
                                    onClear={handleBulkClear}
                                    currentIndex={currentBulkIndex}
                                    total={bulkQuestions.length}
                                />
                            )}

                            {/* Subject selector */}
                            <div className="bg-white rounded-xl shadow-lg p-6">
                                <h2 className="text-xl font-bold text-gray-800 mb-4">Exam Organization</h2>
                                <SubjectSelector
                                    subjects={subjects}
                                    isLoading={isLoadingSubjects}
                                    selectedSubject={selectedSubject}
                                    selectedPaper={selectedPaper}
                                    selectedTopic={selectedTopic}
                                    selectedSection={selectedSection}
                                    onSubjectChange={handleSubjectChange}
                                    onPaperChange={handlePaperChange}
                                    onTopicChange={handleTopicChange}
                                    onSectionChange={handleSectionChange}
                                    onGoToSubjects={() => setActiveTab('subjects')}
                                />
                            </div>

                            {/* Question form */}
                            <QuestionForm
                                selectedSubject={selectedSubject}
                                selectedPaper={selectedPaper}
                                selectedTopic={selectedTopic}
                                selectedSection={selectedSection}
                                selectedSubjectId={selectedSubjectId}
                                selectedPaperId={selectedPaperId}
                                selectedTopicId={selectedTopicId}
                                selectedSectionId={selectedSectionId}
                                formState={formState}
                                renderContent={renderContent}
                                onSubmitSuccess={handleSubmitSuccess}
                                bulkMode={bulkQuestions.length > 0}
                                currentBulkIndex={currentBulkIndex}
                                totalBulkQuestions={bulkQuestions.length}
                            />
                        </div>

                        {/* Similar questions sidebar */}
                        <div className="lg:col-span-1">
                            <div className="bg-white rounded-xl shadow-lg p-6 sticky top-4">
                                <h2 className="text-xl font-bold text-gray-800 mb-4">Similar Questions</h2>
                                <SimilarQuestions
                                    questions={similarQuestions}
                                    isSearching={isSearchingSimilar}
                                    questionText={formState.questionText}
                                />
                            </div>
                        </div>
                    </div>
                )}

                {/* Stats Tab  */}
                {activeTab === 'stats' && (
                    <StatsTab
                        existingSubjects={existingSubjects}
                        onOpenPrintableByPaper={handleOpenPrintableByPaper}
                        onOpenPrintableByTopic={handleOpenPrintableByTopic}
                    />
                )}

                {/*  Subjects Tab */}
                {activeTab === 'subjects' && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <div className="lg:col-span-2">
                            <SubjectsTab />
                        </div>

                        {/* Add New Subject Form (borrowed from EditorDashboard1) */}
                        <div className="lg:col-span-1">
                            <div className="bg-white rounded-xl shadow-lg p-8">
                                <h2 className="text-2xl font-bold text-gray-800 mb-6">Add New Subject</h2>
                                <form onSubmit={handleSubmitNewSubject}>
                                    <div className="mb-6">
                                        <label className="block text-sm font-bold text-gray-700 mb-2">Subject Name *</label>
                                        <input type="text" value={newSubjectName} onChange={e => setNewSubjectName(e.target.value)}
                                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 outline-none" placeholder="e.g., Computer Science" required />
                                    </div>

                                    <div className="mb-6">
                                        <div className="flex justify-between items-center mb-4">
                                            <h3 className="text-lg font-bold text-gray-800">Papers</h3>
                                            <button type="button" onClick={addPaper}
                                                className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm">+ Add Paper</button>
                                        </div>

                                        {newSubjectPapers.map((paper, paperIndex) => (
                                            <div key={paperIndex} className="border border-gray-200 rounded-lg p-4 mb-4">
                                                <div className="flex justify-between items-center mb-3">
                                                    <h4 className="text-md font-semibold">Paper {paperIndex + 1}</h4>
                                                    {newSubjectPapers.length > 1 && (
                                                        <button type="button" onClick={() => removePaper(paperIndex)} className="text-red-600 text-sm">Remove</button>
                                                    )}
                                                </div>

                                                <div className="mb-3">
                                                    <label className="block text-sm text-gray-700 mb-1">Paper Name</label>
                                                    <input type="text" value={paper.name} onChange={e => updatePaperName(paperIndex, e.target.value)}
                                                        className="w-full px-3 py-2 border border-gray-300 rounded" />
                                                </div>

                                                <div className="flex gap-2 mb-3">
                                                    <div>
                                                        <label className="block text-sm text-gray-700 mb-1">Hours</label>
                                                        <input type="number" min="0" max="24" value={paper.durationHours}
                                                            onChange={e => updatePaperDuration(paperIndex, 'hours', e.target.value)}
                                                            className="w-24 px-2 py-1 border border-gray-300 rounded" />
                                                    </div>
                                                    <div>
                                                        <label className="block text-sm text-gray-700 mb-1">Minutes</label>
                                                        <input type="number" min="0" max="59" value={paper.durationMinutes}
                                                            onChange={e => updatePaperDuration(paperIndex, 'minutes', e.target.value)}
                                                            className="w-24 px-2 py-1 border border-gray-300 rounded" />
                                                    </div>
                                                </div>

                                                <div className="mb-2">
                                                    <div className="flex items-center justify-between mb-2">
                                                        <h5 className="text-sm font-semibold text-gray-600">Topics</h5>
                                                        <button type="button" onClick={() => addTopic(paperIndex)} className="text-sm text-blue-600">+ Topic</button>
                                                    </div>
                                                    {paper.topics.map((t, ti) => (
                                                        <div key={ti} className="flex items-center gap-2 mb-2">
                                                            <input type="text" value={t} onChange={e => updateTopic(paperIndex, ti, e.target.value)}
                                                                className="flex-1 px-3 py-1 border border-gray-300 rounded" />
                                                            <button type="button" onClick={() => removeTopic(paperIndex, ti)} className="text-red-600">Remove</button>
                                                        </div>
                                                    ))}
                                                </div>

                                                <div>
                                                    <div className="flex items-center justify-between mb-2">
                                                        <h5 className="text-sm font-semibold text-gray-600">Sections</h5>
                                                        <button type="button" onClick={() => addSection(paperIndex)} className="text-sm text-blue-600">+ Section</button>
                                                    </div>
                                                    {paper.sections.map((s, si) => (
                                                        <div key={si} className="flex items-center gap-2 mb-2">
                                                            <input type="text" value={s} onChange={e => updateSection(paperIndex, si, e.target.value)}
                                                                className="flex-1 px-3 py-1 border border-gray-300 rounded" />
                                                            <button type="button" onClick={() => removeSection(paperIndex, si)} className="text-red-600">Remove</button>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        ))}
                                    </div>

                                    <div className="flex justify-end">
                                        <button type="submit" className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg">Create Subject</button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                )}

                {/*  Edit Tab */}
                {activeTab === 'edit' && (
                    <EditTab existingSubjects={existingSubjects} />
                )}

                {/*  Messaging Tab */}
                {activeTab === 'messaging' && <MessagingTab />}
            </div>

            {/* Printable Modal */}
            <PrintableDocumentModal
                isOpen={showPrintable}
                onClose={() => setShowPrintable(false)}
                htmlContent={printableHtml}
                topicName={printableTitle}
                paperName={printableTitle}
            />
        </div>
    );
}