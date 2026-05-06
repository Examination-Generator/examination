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

    // ── Subject edit modal ─────────────────────────────────────────────
    const [showEditModal, setShowEditModal] = useState(false);
    const [editingItem, setEditingItem] = useState(null); // { type: 'subject'|'paper'|'topic'|'section', data: {...} }
    const [editSubjectData, setEditSubjectData] = useState(null);
    const [showFullEditModal, setShowFullEditModal] = useState(false);
    const [selectedPaperIndices, setSelectedPaperIndices] = useState([]); // Papers selected for editing
    const [showTopicsModal, setShowTopicsModal] = useState(false);
    const [viewingPaperTopics, setViewingPaperTopics] = useState(null);

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

    // ── Subject edit handlers ──────────────────────────────────────────
    const handleEditSubject = (subject, fullEdit = false) => {
        if (fullEdit) {
            // Full edit mode - allows adding/removing papers, topics, sections
            const papers = subject.papers && Array.isArray(subject.papers) && subject.papers.length > 0 
                ? subject.papers.map(paper => ({
                    id: paper.id,
                    name: paper.name || '',
                    durationHours: paper.durationHours || 2,
                    durationMinutes: paper.durationMinutes || 0,
                    topics: Array.isArray(paper.topics) && paper.topics.length > 0 
                        ? paper.topics.map(t => {
                            if (typeof t === 'object' && t !== null) {
                                return { id: t.id, name: t.name || '' };
                            }
                            return { name: typeof t === 'string' ? t : '' };
                        })
                        : [{ name: '' }],
                    sections: Array.isArray(paper.sections) && paper.sections.length > 0 
                        ? paper.sections.map(s => {
                            if (typeof s === 'object' && s !== null) {
                                return { id: s.id, name: s.name || '' };
                            }
                            return { name: typeof s === 'string' ? s : '' };
                        })
                        : []
                }))
                : [{ name: '', topics: [{ name: '' }], sections: [], durationHours: 2, durationMinutes: 0 }];
                
            setEditSubjectData({
                id: subject.id,
                name: subject.name || '',
                papers: papers,
                originalPaperCount: papers.length
            });
            setSelectedPaperIndices([]);
            setShowFullEditModal(true);
        } else {
            // Simple name edit mode
            setEditingItem({ type: 'subject', data: subject });
            setShowEditModal(true);
        }
    };

    const handleAddEditPaper = () => {
        setEditSubjectData(prev => ({
            ...prev,
            papers: [...prev.papers, { name: '', topics: [{ name: '' }], sections: [], durationHours: 2, durationMinutes: 0 }]
        }));
        setSelectedPaperIndices(prev => [...prev, editSubjectData.papers.length]);
    };

    const handleRemoveEditPaper = (paperIndex) => {
        setEditSubjectData(prev => ({
            ...prev,
            papers: prev.papers.filter((_, index) => index !== paperIndex)
        }));
        setSelectedPaperIndices(prev => 
            prev.filter(idx => idx !== paperIndex).map(idx => idx > paperIndex ? idx - 1 : idx)
        );
    };

    const handleTogglePaperSelection = (paperIndex) => {
        setSelectedPaperIndices(prev => {
            if (prev.includes(paperIndex)) {
                return prev.filter(idx => idx !== paperIndex);
            } else {
                return [...prev, paperIndex];
            }
        });
    };

    const handleViewPaperTopics = (paper) => {
        setViewingPaperTopics({
            paperName: paper.name,
            topics: Array.isArray(paper.topics) ? paper.topics.filter(t => t && (typeof t === 'object' ? t.name : t)?.trim?.()).map(t => typeof t === 'object' ? t.name : t) : [],
            sections: Array.isArray(paper.sections) ? paper.sections.filter(s => s && (typeof s === 'object' ? s.name : s)?.trim?.()).map(s => typeof s === 'object' ? s.name : s) : []
        });
        setShowTopicsModal(true);
    };

    const handleEditPaperNameChange = (paperIndex, value) => {
        setEditSubjectData(prev => ({
            ...prev,
            papers: prev.papers.map((paper, index) => 
                index === paperIndex ? { ...paper, name: value } : paper
            )
        }));
    };

    const handleEditPaperDurationChange = (paperIndex, field, value) => {
        const numValue = parseInt(value) || 0;
        setEditSubjectData(prev => ({
            ...prev,
            papers: prev.papers.map((paper, index) => {
                if (index === paperIndex) {
                    if (field === 'hours') {
                        return { ...paper, durationHours: Math.max(0, Math.min(24, numValue)) };
                    } else {
                        return { ...paper, durationMinutes: Math.max(0, Math.min(59, numValue)) };
                    }
                }
                return paper;
            })
        }));
    };

    const handleAddEditTopic = (paperIndex) => {
        setEditSubjectData(prev => ({
            ...prev,
            papers: prev.papers.map((paper, index) => 
                index === paperIndex 
                    ? { ...paper, topics: [...paper.topics, { name: '' }] }
                    : paper
            )
        }));
    };

    const handleRemoveEditTopic = (paperIndex, topicIndex) => {
        setEditSubjectData(prev => ({
            ...prev,
            papers: prev.papers.map((paper, index) => 
                index === paperIndex 
                    ? { ...paper, topics: paper.topics.filter((_, tIndex) => tIndex !== topicIndex) }
                    : paper
            )
        }));
    };

    const handleEditTopicChange = (paperIndex, topicIndex, value) => {
        setEditSubjectData(prev => ({
            ...prev,
            papers: prev.papers.map((paper, index) => 
                index === paperIndex 
                    ? { 
                        ...paper, 
                        topics: paper.topics.map((topic, tIndex) => 
                            tIndex === topicIndex 
                                ? { ...topic, name: value }
                                : topic
                        )
                    }
                    : paper
            )
        }));
    };

    const handleAddEditSection = (paperIndex) => {
        setEditSubjectData(prev => ({
            ...prev,
            papers: prev.papers.map((paper, index) => 
                index === paperIndex 
                    ? { ...paper, sections: [...paper.sections, { name: '' }] }
                    : paper
            )
        }));
    };

    const handleRemoveEditSection = (paperIndex, sectionIndex) => {
        setEditSubjectData(prev => ({
            ...prev,
            papers: prev.papers.map((paper, index) => 
                index === paperIndex 
                    ? { ...paper, sections: paper.sections.filter((_, sIndex) => sIndex !== sectionIndex) }
                    : paper
            )
        }));
    };

    const handleEditSectionChange = (paperIndex, sectionIndex, value) => {
        setEditSubjectData(prev => ({
            ...prev,
            papers: prev.papers.map((paper, index) => 
                index === paperIndex 
                    ? { 
                        ...paper, 
                        sections: paper.sections.map((section, sIndex) => 
                            sIndex === sectionIndex 
                                ? { ...section, name: value }
                                : section
                        )
                    }
                    : paper
            )
        }));
    };

    const handleSaveFullEdit = async () => {
        if (!editSubjectData) return;

        if (!editSubjectData.name.trim()) {
            showError('Subject name cannot be empty');
            return;
        }

        const originalPaperCount = editSubjectData.originalPaperCount || 0;
        
        try {
            const allPapers = editSubjectData.papers.map((paper, index) => {
                const isExistingPaper = index < originalPaperCount && paper.id;
                
                const topicsMap = new Map();
                paper.topics
                    .filter(topic => {
                        const name = (typeof topic === 'object' ? topic.name : topic) || '';
                        return name.trim();
                    })
                    .forEach(topic => {
                        const topicObj = typeof topic === 'object' ? topic : { name: topic };
                        const name = topicObj.name.trim();
                        const key = name.toLowerCase();
                        if (!topicsMap.has(key)) {
                            topicsMap.set(key, topicObj);
                        }
                    });
                
                const sectionsMap = new Map();
                paper.sections
                    .filter(section => {
                        const name = (typeof section === 'object' ? section.name : section) || '';
                        return name.trim();
                    })
                    .forEach(section => {
                        const sectionObj = typeof section === 'object' ? section : { name: section };
                        const name = sectionObj.name.trim();
                        const key = name.toLowerCase();
                        if (!sectionsMap.has(key)) {
                            sectionsMap.set(key, sectionObj);
                        }
                    });

                const paperData = {
                    name: paper.name.trim(),
                    topics: Array.from(topicsMap.values()),
                    sections: Array.from(sectionsMap.values()),
                    durationHours: paper.durationHours,
                    durationMinutes: paper.durationMinutes
                };
                
                if (isExistingPaper) {
                    paperData.id = paper.id;
                }

                return paperData;
            });

            const validPapers = allPapers.filter(paper => {
                const hasName = paper.name.trim();
                const hasTopics = paper.topics.length > 0;
                return hasName && hasTopics;
            });

            if (validPapers.length === 0) {
                showError('Please add at least one paper with a name and at least one topic');
                return;
            }

            await subjectService.updateSubject(editSubjectData.id, {
                name: editSubjectData.name.trim(),
                papers: validPapers
            });

            showSuccess('Subject updated successfully!');
            
            setShowFullEditModal(false);
            setEditSubjectData(null);
            setSelectedPaperIndices([]);
            
            setTimeout(() => {
                loadSubjects();
            }, 300);
        } catch (error) {
            showError(error.message || 'Failed to update subject. Please try again.');
        }
    };

    const handleCancelFullEdit = () => {
        setShowFullEditModal(false);
        setEditSubjectData(null);
        setSelectedPaperIndices([]);
    };

    const handleEditSubjectNameChange = (value) => {
        setEditSubjectData(prev => ({ ...prev, name: value }));
    };

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
                    <div className="grid grid-cols-1 gap-6">
                        <div>
                            <SubjectsTab onEditSubject={handleEditSubject} />
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

            {/* Full Subject Edit Modal */}
            {showFullEditModal && editSubjectData && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
                    <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full my-8 max-h-[90vh] overflow-y-auto">
                        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 z-10">
                            <h3 className="text-2xl font-bold text-gray-800">Manage Subject Structure</h3>
                            <p className="text-sm text-gray-600 mt-1">Add or remove papers, topics, and sections</p>
                        </div>

                        <div className="p-6 space-y-6">
                            {/* Subject Name */}
                            <div>
                                <label className="block text-sm font-bold text-gray-700 mb-2">
                                    Subject Name *
                                </label>
                                <input
                                    type="text"
                                    value={editSubjectData.name}
                                    onChange={(e) => handleEditSubjectNameChange(e.target.value)}
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                    placeholder="Enter subject name"
                                />
                            </div>

                            {/* Papers Section */}
                            <div className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <label className="text-sm font-bold text-gray-700">
                                        Papers * (at least one required)
                                    </label>
                                    <button
                                        onClick={handleAddEditPaper}
                                        className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition text-sm"
                                    >
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                                        </svg>
                                        <span>Add Paper</span>
                                    </button>
                                </div>

                                {editSubjectData.papers.map((paper, paperIndex) => {
                                    const isSelected = selectedPaperIndices.includes(paperIndex);
                                    const isExistingPaper = paperIndex < (editSubjectData.originalPaperCount || 0);
                                    
                                    return (
                                        <div key={paperIndex} className={`bg-gray-50 p-4 rounded-lg border-2 space-y-4 transition-all ${
                                            isExistingPaper && !isSelected 
                                                ? 'border-gray-300 opacity-60' 
                                                : 'border-purple-300'
                                        }`}>
                                            {/* Paper Header */}
                                            <div className="flex items-start justify-between">
                                                <div className="flex items-start space-x-3 flex-1">
                                                    {isExistingPaper && (
                                                        <div className="pt-6">
                                                            <input
                                                                type="checkbox"
                                                                checked={isSelected}
                                                                onChange={() => handleTogglePaperSelection(paperIndex)}
                                                                className="w-5 h-5 text-purple-600 border-gray-300 rounded focus:ring-2 focus:ring-purple-500 cursor-pointer"
                                                            />
                                                        </div>
                                                    )}
                                                    
                                                    <div className="flex-1">
                                                        <div className="flex items-center space-x-2 mb-1">
                                                            <label className="block text-xs font-semibold text-gray-600">
                                                                Paper {paperIndex + 1} Name *
                                                            </label>
                                                            {!isExistingPaper && (
                                                                <span className="inline-block bg-green-100 text-green-800 px-2 py-0.5 rounded text-xs font-semibold">
                                                                    New
                                                                </span>
                                                            )}
                                                        </div>
                                                        <input
                                                            type="text"
                                                            value={paper.name}
                                                            onChange={(e) => handleEditPaperNameChange(paperIndex, e.target.value)}
                                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none text-sm"
                                                            placeholder="e.g., Paper 1"
                                                            disabled={isExistingPaper && !isSelected}
                                                        />
                                                    </div>
                                                </div>
                                                
                                                <div className="flex items-start space-x-2 pt-6">
                                                    {isExistingPaper && (
                                                        <button
                                                            onClick={() => handleViewPaperTopics(paper)}
                                                            className="flex items-center space-x-1 bg-blue-500 hover:bg-blue-600 text-white px-3 py-2 rounded-lg transition text-xs font-medium"
                                                        >
                                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                                            </svg>
                                                            <span>View Topics</span>
                                                        </button>
                                                    )}
                                                    
                                                    {editSubjectData.papers.length > 1 && (
                                                        <button
                                                            onClick={() => handleRemoveEditPaper(paperIndex)}
                                                            className="text-red-600 hover:text-red-700 p-2 hover:bg-red-50 rounded transition"
                                                        >
                                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                                            </svg>
                                                        </button>
                                                    )}
                                                </div>
                                            </div>
                                            
                                            {(!isExistingPaper || isSelected) && (
                                                <>
                                                    {/* Paper Duration */}
                                                    <div className="bg-blue-50 p-3 rounded-lg">
                                                        <label className="block text-xs font-semibold text-gray-600 mb-2">
                                                            Paper Duration *
                                                        </label>
                                                        <div className="flex items-center space-x-3">
                                                            <div className="flex items-center space-x-2">
                                                                <label className="text-xs text-gray-600">Hours:</label>
                                                                <input
                                                                    type="number"
                                                                    min="0"
                                                                    max="24"
                                                                    value={paper.durationHours || 2}
                                                                    onChange={(e) => handleEditPaperDurationChange(paperIndex, 'hours', e.target.value)}
                                                                    className="w-20 px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none text-sm"
                                                                    disabled={isExistingPaper && !isSelected}
                                                                />
                                                            </div>
                                                            <div className="flex items-center space-x-2">
                                                                <label className="text-xs text-gray-600">Minutes:</label>
                                                                <input
                                                                    type="number"
                                                                    min="0"
                                                                    max="59"
                                                                    value={paper.durationMinutes || 0}
                                                                    onChange={(e) => handleEditPaperDurationChange(paperIndex, 'minutes', e.target.value)}
                                                                    className="w-20 px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none text-sm"
                                                                    disabled={isExistingPaper && !isSelected}
                                                                />
                                                            </div>
                                                            <div className="text-xs text-gray-600 font-medium">
                                                                = {paper.durationHours || 0}h {paper.durationMinutes || 0}m
                                                            </div>
                                                        </div>
                                                    </div>

                                                    {/* Topics */}
                                                    <div>
                                                        <div className="flex items-center justify-between mb-2">
                                                            <label className="text-xs font-semibold text-gray-600">
                                                                Topics * (at least one required)
                                                            </label>
                                                            <button
                                                                onClick={() => handleAddEditTopic(paperIndex)}
                                                                className="text-blue-600 hover:text-blue-700 text-xs flex items-center space-x-1"
                                                            >
                                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                                                                </svg>
                                                                <span>Add Topic</span>
                                                            </button>
                                                        </div>
                                                        <div className="space-y-2">
                                                            {paper.topics.map((topic, topicIndex) => (
                                                                <div key={topicIndex} className="flex items-center space-x-2">
                                                                    <input
                                                                        type="text"
                                                                        value={typeof topic === 'object' ? (topic.name || '') : (topic || '')}
                                                                        onChange={(e) => handleEditTopicChange(paperIndex, topicIndex, e.target.value)}
                                                                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-sm"
                                                                        placeholder={`Topic ${topicIndex + 1}`}
                                                                    />
                                                                    {paper.topics.length > 1 && (
                                                                        <button
                                                                            onClick={() => handleRemoveEditTopic(paperIndex, topicIndex)}
                                                                            className="text-red-600 hover:text-red-700 p-2 hover:bg-red-50 rounded transition"
                                                                        >
                                                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                                                            </svg>
                                                                        </button>
                                                                    )}
                                                                </div>
                                                            ))}
                                                        </div>
                                                    </div>

                                                    {/* Sections */}
                                                    <div>
                                                        <div className="flex items-center justify-between mb-2">
                                                            <label className="text-xs font-semibold text-gray-600">
                                                                Sections (optional)
                                                            </label>
                                                            <button
                                                                onClick={() => handleAddEditSection(paperIndex)}
                                                                className="text-blue-600 hover:text-blue-700 text-xs flex items-center space-x-1"
                                                            >
                                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                                                                </svg>
                                                                <span>Add Section</span>
                                                            </button>
                                                        </div>
                                                        {paper.sections.length > 0 ? (
                                                            <div className="space-y-2">
                                                                {paper.sections.map((section, sectionIndex) => (
                                                                    <div key={sectionIndex} className="flex items-center space-x-2">
                                                                        <input
                                                                            type="text"
                                                                            value={typeof section === 'object' ? (section.name || '') : (section || '')}
                                                                            onChange={(e) => handleEditSectionChange(paperIndex, sectionIndex, e.target.value)}
                                                                            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-sm"
                                                                            placeholder={`Section ${sectionIndex + 1}`}
                                                                        />
                                                                        <button
                                                                            onClick={() => handleRemoveEditSection(paperIndex, sectionIndex)}
                                                                            className="text-red-600 hover:text-red-700 p-2 hover:bg-red-50 rounded transition"
                                                                        >
                                                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                                                            </svg>
                                                                        </button>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        ) : (
                                                            <p className="text-xs text-gray-500 italic">No sections added. Click "Add Section" to create one.</p>
                                                        )}
                                                    </div>
                                                </>
                                            )}
                                        </div>
                                    );
                                })}

                                {editSubjectData.papers.length === 0 && (
                                    <div className="text-center py-8 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                                        <p className="text-gray-500 mb-3">No papers added yet</p>
                                        <button
                                            onClick={handleAddEditPaper}
                                            className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-lg transition"
                                        >
                                            Add First Paper
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Modal Footer */}
                        <div className="sticky bottom-0 bg-white border-t border-gray-200 px-6 py-4 flex space-x-3">
                            <button
                                onClick={handleSaveFullEdit}
                                className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200"
                            >
                                Save Changes
                            </button>
                            <button
                                onClick={handleCancelFullEdit}
                                className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold py-3 px-6 rounded-lg transition duration-200"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
            

                {/* View Paper Topics Modal */}
                {showTopicsModal && viewingPaperTopics && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                        <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
                            <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-4 rounded-t-xl">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <h2 className="text-2xl font-bold">Paper Topics & Sections</h2>
                                        <p className="text-blue-100 mt-1">{viewingPaperTopics.paperName}</p>
                                    </div>
                                    <button
                                        onClick={() => setShowTopicsModal(false)}
                                        className="text-white hover:bg-blue-800 p-2 rounded-lg transition"
                                    >
                                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </button>
                                </div>
                            </div>

                            <div className="p-6 space-y-6">
                                {/* Topics Section */}
                                <div>
                                    <div className="flex items-center space-x-2 mb-3">
                                        <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                                        </svg>
                                        <h3 className="text-lg font-bold text-gray-800">
                                            Topics ({viewingPaperTopics.topics.length})
                                        </h3>
                                    </div>
                                    
                                    {viewingPaperTopics.topics.length > 0 ? (
                                        <div className="bg-blue-50 rounded-lg p-4">
                                            <div className="flex flex-wrap gap-2">
                                                {viewingPaperTopics.topics.map((topic, idx) => (
                                                    <div key={idx} className="flex items-center space-x-2 bg-blue-100 text-blue-800 px-3 py-2 rounded-lg">
                                                        <span className="font-semibold text-blue-600">{idx + 1}.</span>
                                                        <span className="font-medium">{topic}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="bg-gray-50 rounded-lg p-4 text-center">
                                            <p className="text-gray-500 italic">No topics found for this paper</p>
                                        </div>
                                    )}
                                </div>

                                {/* Sections Section */}
                                <div>
                                    <div className="flex items-center space-x-2 mb-3">
                                        <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                                        </svg>
                                        <h3 className="text-lg font-bold text-gray-800">
                                            Sections ({viewingPaperTopics.sections.length})
                                        </h3>
                                    </div>
                                    
                                    {viewingPaperTopics.sections.length > 0 ? (
                                        <div className="bg-green-50 rounded-lg p-4">
                                            <div className="flex flex-wrap gap-2">
                                                {viewingPaperTopics.sections.map((section, idx) => (
                                                    <div key={idx} className="flex items-center space-x-2 bg-green-100 text-green-800 px-3 py-2 rounded-lg">
                                                        <span className="font-semibold text-green-600">{idx + 1}.</span>
                                                        <span className="font-medium">{section}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="bg-gray-50 rounded-lg p-4 text-center">
                                            <p className="text-gray-500 italic">No sections found for this paper</p>
                                        </div>
                                    )}
                                </div>
                            </div>

                            <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4 rounded-b-xl">
                                <button
                                    onClick={() => setShowTopicsModal(false)}
                                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200"
                                >
                                    Close
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
    )}
    </div>);
   
}