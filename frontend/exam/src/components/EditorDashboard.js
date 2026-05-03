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
                {activeTab === 'subjects' && <SubjectsTab />}

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