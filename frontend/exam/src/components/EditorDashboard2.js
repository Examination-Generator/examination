
import React, { useState, useEffect, useCallback } from 'react';
import { useQuestionForm } from '../hooks/useQuestionForm';
import SubjectSelector from './SubjectSelector';
import DrawingTool from './DrawingTool';
import SimilarQuestions from './SimilarQuestions';
import StatsCards from './StatsCards';
import QuestionListItem from './QuestionListItem';
import StatsTab from './StatsTab';
import EditTab from './EditTab';
import SubjectsTab from './subjects/SubjectsTab';
import MessagingTab from './MessagingTab';
import QuestionForm from './QuestionForm';
import * as subjectService from '../services/subjectService';
import * as authService from '../services/authService';

export default function EditorDashboard({ onLogout }) {
    const [activeTab, setActiveTab] = useState(() => {
        try { return localStorage.getItem('editorActiveTab') || 'questions'; }
        catch { return 'questions'; }
    });

    // Subject/paper/topic selection
    const [selectedSubject, setSelectedSubject] = useState('');
    const [selectedPaper, setSelectedPaper] = useState('');
    const [selectedTopic, setSelectedTopic] = useState('');
    const [selectedSection, setSelectedSection] = useState('');
    const [selectedSubjectId, setSelectedSubjectId] = useState('');
    const [selectedPaperId, setSelectedPaperId] = useState('');
    const [selectedTopicId, setSelectedTopicId] = useState('');
    const [selectedSectionId, setSelectedSectionId] = useState('');

    const [subjects, setSubjects] = useState({});
    const [isLoadingSubjects, setIsLoadingSubjects] = useState(false);
    const [similarQuestions, setSimilarQuestions] = useState([]);
    const [isSearching, setIsSearching] = useState(false);

    // Use extracted form hook
    const formState = useQuestionForm();

    // Persist tab
    useEffect(() => {
        try { localStorage.setItem('editorActiveTab', activeTab); }
        catch {}
    }, [activeTab]);

    const loadSubjects = useCallback(async () => {
        setIsLoadingSubjects(true);
        try {
            const data = await subjectService.getAllSubjects();
            const transformed = {};
            data.forEach(subject => {
                if (subject.isActive !== false) {
                    const papersMap = {};
                    const sectionsMap = {};
                    const topicsMap = {};
                    (subject.papers || []).forEach(paper => {
                        if (paper.isActive !== false && paper.name) {
                            papersMap[paper.name] = paper;
                            sectionsMap[paper.name] = (paper.sections || []).filter(s => s?.name).map(s => s.name);
                            topicsMap[paper.name] = (paper.topics || []).filter(t => t?.name).map(t => t.name);
                        }
                    });
                    transformed[subject.name] = {
                        papers: Object.keys(papersMap),
                        sections: sectionsMap,
                        topics: topicsMap,
                        papersData: papersMap,
                        id: subject.id,
                    };
                }
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
        if (activeTab === 'questions') loadSubjects();
    }, [activeTab, loadSubjects]);

    const handleSubjectChange = useCallback((subject) => {
        setSelectedSubject(subject);
        setSelectedPaper('');
        setSelectedTopic('');
        setSelectedSection('');
        setSelectedSubjectId(subjects[subject]?.id || '');
        setSelectedPaperId('');
        setSelectedTopicId('');
        setSelectedSectionId('');
    }, [subjects]);

    const handlePaperChange = useCallback((paper) => {
        setSelectedPaper(paper);
        setSelectedTopic('');
        setSelectedSection('');
        const paperId = subjects[selectedSubject]?.papersData?.[paper]?.id || '';
        setSelectedPaperId(paperId);
        setSelectedTopicId('');
        setSelectedSectionId('');
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
                        className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition"
                    >
                        Logout
                    </button>
                </div>
            </header>

            {/* Nav Tabs */}
            <div className="max-w-8xl mx-auto px-4 pt-6">
                <div className="bg-white rounded-lg shadow-md p-1 flex flex-wrap gap-1">
                    {tabs.map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`flex-1 min-w-[140px] py-3 px-4 rounded-lg font-semibold transition ${
                                activeTab === tab.id
                                    ? 'bg-green-600 text-white shadow-md'
                                    : 'text-gray-600 hover:bg-gray-50'
                            }`}
                        >
                            {tab.label}
                        </button>
                    ))}
                </div>
            </div>

            <div className="max-w-8xl mx-auto px-4 py-8">
                {activeTab === 'questions' && (
                    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                        <div className="lg:col-span-3 space-y-6">
                            {/* Subject Selector */}
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
                                onSubmitSuccess={(savedQuestion) => {
                                    console.log('Question saved:', savedQuestion);
                                }}
                            />
                        </div>

                        {/* Similar Questions Sidebar */}
                        <div className="lg:col-span-1">
                            <div className="bg-white rounded-xl shadow-lg p-6 sticky top-4">
                                <h2 className="text-xl font-bold text-gray-800 mb-4">Similar Questions</h2>
                                <SimilarQuestions
                                    questions={similarQuestions}
                                    isSearching={isSearching}
                                    questionText={formState.questionText}
                                />
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'messaging' && <MessagingTab />}

                {/* Other tabs rendered similarly with their own components */}
            </div>
        </div>
    );
}