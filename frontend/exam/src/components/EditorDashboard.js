import { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import mammoth from 'mammoth';
import * as pdfjsLib from 'pdfjs-dist';
import * as subjectService from '../services/subjectService';
import * as questionService from '../services/questionService';
import * as authService from '../services/authService';
import { useSearchQuestions } from '../hooks/useQuestions';
import { useDebounce } from '../hooks/useDebounce';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api' ;

// Configure PDF.js worker using a more reliable CDN
if (typeof window !== 'undefined') {
    pdfjsLib.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjsLib.version}/build/pdf.worker.min.js`;
}



export default function EditorDashboard({ onLogout }) {
    const [activeTab, setActiveTab] = useState('questions'); // 'questions', 'subjects', 'stats'
    const [selectedSubject, setSelectedSubject] = useState('');
    const [selectedTopic, setSelectedTopic] = useState('');
    const [selectedPaper, setSelectedPaper] = useState('');
    const [selectedSection, setSelectedSection] = useState('');
    
    // Store UUIDs for API submission
    const [selectedSubjectId, setSelectedSubjectId] = useState('');
    const [selectedPaperId, setSelectedPaperId] = useState('');
    const [selectedTopicId, setSelectedTopicId] = useState('');
    const [selectedSectionId, setSelectedSectionId] = useState('');
    
    const [questionText, setQuestionText] = useState('');
    const [answerText, setAnswerText] = useState('');
    const [marks, setMarks] = useState('');
    const [similarQuestions, setSimilarQuestions] = useState([]);
    const [isSearching, setIsSearching] = useState(false);
    const [showMobileSimilar, setShowMobileSimilar] = useState(false);
    
    // New features states
    const [isQuestionActive, setIsQuestionActive] = useState(true); // Changed from isQuestionComplete
    const [isNested, setIsNested] = useState(false); // Track if question is nested
    const [isEssayQuestion, setIsEssayQuestion] = useState(false); // Track if question is an essay
    const [isGraphQuestion, setIsGraphQuestion] = useState(false); // Track if question requires graphing
    const [uploadedImages, setUploadedImages] = useState([]);
    const [showDrawingTool, setShowDrawingTool] = useState(false);
    const [showGraphPaper, setShowGraphPaper] = useState(false);
    const [drawingTool, setDrawingTool] = useState('pen'); // 'pen', 'eraser', 'line', 'rectangle', 'circle'
    const [drawingColor, setDrawingColor] = useState('#000000');
    const [drawingWidth, setDrawingWidth] = useState(2);
    const canvasRef = useRef(null);
    const [isDrawing, setIsDrawing] = useState(false);
    const [startPos, setStartPos] = useState({ x: 0, y: 0 }); // For shape drawing
    
    // Inline images for question
    const [questionInlineImages, setQuestionInlineImages] = useState([]);
    const [questionImagePositions, setQuestionImagePositions] = useState({}); // { imageId: { x, y } }
    
    // Answer section states
    const [uploadedAnswerImages, setUploadedAnswerImages] = useState([]);
    const [showAnswerDrawingTool, setShowAnswerDrawingTool] = useState(false);
    const [showAnswerGraphPaper, setShowAnswerGraphPaper] = useState(false);
    const [answerDrawingTool, setAnswerDrawingTool] = useState('pen');
    const [answerDrawingColor, setAnswerDrawingColor] = useState('#000000');
    const [answerDrawingWidth, setAnswerDrawingWidth] = useState(2);
    const answerCanvasRef = useRef(null);
    const [isAnswerDrawing, setIsAnswerDrawing] = useState(false);
    
    // Inline images for answer
    const [answerInlineImages, setAnswerInlineImages] = useState([]);
    const [answerImagePositions, setAnswerImagePositions] = useState({}); // { imageId: { x, y } }
    
    // Voice transcription states
    const [isQuestionListening, setIsQuestionListening] = useState(false);
    const [isAnswerListening, setIsAnswerListening] = useState(false);
    const questionRecognitionRef = useRef(null);
    const answerRecognitionRef = useRef(null);
    
    // Text formatting states
    const questionTextareaRef = useRef(null);
    const answerTextareaRef = useRef(null);
    
    // Answer lines states
    const [showAnswerLinesModal, setShowAnswerLinesModal] = useState(false);
    const [answerLinesConfig, setAnswerLinesConfig] = useState({
        numberOfLines: 5,
        lineHeight: 30,
        lineStyle: 'dotted', // 'dotted' or 'solid'
        opacity: 0.5, // 0.1 to 1
        targetSection: 'question' // 'question' or 'answer'
    });
    const [questionAnswerLines, setQuestionAnswerLines] = useState([]); // Array of line configurations
    const [answerAnswerLines, setAnswerAnswerLines] = useState([]); // Array of line configurations
    
    // Edit questions states
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [isSearchingQuestions, setIsSearchingQuestions] = useState(false);
    
    const [editFilterStatus, setEditFilterStatus] = useState('all'); // 'all', 'active', 'inactive'
    const [editFilterType, setEditFilterType] = useState('all'); // 'all', 'nested', 'standalone'
    const [selectedQuestion, setSelectedQuestion] = useState(null);
    const [editQuestionText, setEditQuestionText] = useState('');
    const [editAnswerText, setEditAnswerText] = useState('');
    const [editMarks, setEditMarks] = useState('');
    const [editTopic, setEditTopic] = useState(''); // Topic ID for editing
    const [editQuestionTopics, setEditQuestionTopics] = useState([]); // Topics for the selected paper
    const [editQuestionSections, setEditQuestionSections] = useState([]); // Sections for the selected paper
    const [editSection, setEditSection] = useState(''); // Section ID for editing
    const [editQuestionInlineImages, setEditQuestionInlineImages] = useState([]);
    const [editAnswerInlineImages, setEditAnswerInlineImages] = useState([]);
    const [editQuestionImagePositions, setEditQuestionImagePositions] = useState({});
    const [editAnswerImagePositions, setEditAnswerImagePositions] = useState({});
    const [editQuestionAnswerLines, setEditQuestionAnswerLines] = useState([]);
    const [editAnswerAnswerLines, setEditAnswerAnswerLines] = useState([]);
    const [editIsActive, setEditIsActive] = useState(true); // Question active status
    const [editIsNested, setEditIsNested] = useState(false); // Question nested status
    const [editIsEssayQuestion, setEditIsEssayQuestion] = useState(false); // Track if question is an essay
    const [editIsGraphQuestion, setEditIsGraphQuestion] = useState(false); // Track if question requires graphing
    const editQuestionTextareaRef = useRef(null);
    const editAnswerTextareaRef = useRef(null);

    

    // Memoize rendered search results to avoid re-rendering list items unnecessarily
    const renderedSearchResults = useMemo(() => (
        (Array.isArray(searchResults) ? searchResults : []).map((question) => (
            <div
                key={question.id}
                onClick={() => handleSelectQuestion(question)}
                className={`p-4 border rounded-lg cursor-pointer transition ${
                    selectedQuestion?.id === question.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                }`}
            >
                <div className="flex justify-between items-start mb-2">
                    <div className="flex-1">
                        <p className="text-sm font-semibold text-gray-800 line-clamp-2">
                            {question.question_text?.substring(0, 150)}...
                        </p>
                    </div>
                    <span className="ml-3 text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full whitespace-nowrap">
                        {question.marks} marks
                    </span>
                </div>
                <div className="flex flex-wrap gap-2 text-xs text-gray-600">
                    <span className="bg-gray-100 px-2 py-1 rounded">
                        📚 {question.subject_name}
                    </span>
                    {question.paper_name && (
                        <span className="bg-gray-100 px-2 py-1 rounded">
                            📄 {question.paper_name}
                        </span>
                    )}
                    {question.topic_name && (
                        <span className="bg-gray-100 px-2 py-1 rounded">
                            📖 {question.topic_name}
                        </span>
                    )}
                    <span className={`px-2 py-1 rounded font-semibold ${
                        question.is_active !== false 
                            ? 'bg-green-100 text-green-700' 
                            : 'bg-red-100 text-red-700'
                    }`}>
                        {question.is_active !== false ? '✓ Active' : '✕ Inactive'}
                    </span>
                    <span className={`px-2 py-1 rounded font-semibold ${
                        question.is_nested === true 
                            ? 'bg-purple-100 text-purple-700' 
                            : 'bg-blue-100 text-blue-700'
                    }`}>
                        {question.is_nested === true ? '⊕ Nested' : '◉ Standalone'}
                    </span>
                </div>
            </div>
        ))
    ), [searchResults, selectedQuestion, handleSelectQuestion]);

    // Edit question drawing states
    const [showEditQuestionDrawing, setShowEditQuestionDrawing] = useState(false);
    const [showEditQuestionGraphPaper, setShowEditQuestionGraphPaper] = useState(false);
    const [editQuestionDrawingTool, setEditQuestionDrawingTool] = useState('pen');
    const [editQuestionDrawingColor, setEditQuestionDrawingColor] = useState('#000000');
    const [editQuestionDrawingWidth, setEditQuestionDrawingWidth] = useState(2);
    const editQuestionCanvasRef = useRef(null);
    const [isEditQuestionDrawing, setIsEditQuestionDrawing] = useState(false);
    const [editQuestionStartPos, setEditQuestionStartPos] = useState({ x: 0, y: 0 });

    // Edit answer drawing states
    const [showEditAnswerDrawing, setShowEditAnswerDrawing] = useState(false);
    const [showEditAnswerGraphPaper, setShowEditAnswerGraphPaper] = useState(false);
    const [editAnswerDrawingTool, setEditAnswerDrawingTool] = useState('pen');
    const [editAnswerDrawingColor, setEditAnswerDrawingColor] = useState('#000000');
    const [editAnswerDrawingWidth, setEditAnswerDrawingWidth] = useState(2);
    const editAnswerCanvasRef = useRef(null);
    const [isEditAnswerDrawing, setIsEditAnswerDrawing] = useState(false);
    const [editAnswerStartPos, setEditAnswerStartPos] = useState({ x: 0, y: 0 });

    // Edit voice recording states
    const [isEditQuestionListening, setIsEditQuestionListening] = useState(false);
    const [isEditAnswerListening, setIsEditAnswerListening] = useState(false);
    const editQuestionRecognitionRef = useRef(null);
    const editAnswerRecognitionRef = useRef(null);

    // Edit answer lines modal state
    const [showEditAnswerLinesModal, setShowEditAnswerLinesModal] = useState(false);
    const [editAnswerLinesConfig, setEditAnswerLinesConfig] = useState({
        numberOfLines: 5,
        lineHeight: 30,
        lineStyle: 'dotted',
        opacity: 0.5,
        targetSection: 'question'
    });

    // Edit questions filter states
    const [editFilterSubject, setEditFilterSubject] = useState('');
    const [editFilterPaper, setEditFilterPaper] = useState('');
    const [editFilterTopic, setEditFilterTopic] = useState('');
    const [editAvailablePapers, setEditAvailablePapers] = useState([]);
    const [editAvailableTopics, setEditAvailableTopics] = useState([]);
    // Debounce the search input to avoid frequent queries
    const debouncedSearchQuery = useDebounce(searchQuery, 400);
    // Use React Query hook for cached searching — enabled only when edit tab active
    const { data: rqSearchResults = [], isLoading: rqIsLoading, refetch: refetchQuestions } = useSearchQuestions(
        debouncedSearchQuery,
        { editFilterSubject, editFilterPaper, editFilterTopic, editFilterStatus, editFilterType },
        activeTab === 'edit'
    );
    // Sync react-query results into local state used across the component
    useEffect(() => {
        setSearchResults(Array.isArray(rqSearchResults) ? rqSearchResults : []);
        setIsSearchingQuestions(!!rqIsLoading);
    }, [rqSearchResults, rqIsLoading]);
    
    // Bulk entry states
    const [bulkText, setBulkText] = useState('');
    const [showBulkEntry, setShowBulkEntry] = useState(false);
    const [bulkQuestions, setBulkQuestions] = useState([]);
    const [currentBulkIndex, setCurrentBulkIndex] = useState(0);
    
    // Statistics and filters
    const [savedQuestions, setSavedQuestions] = useState([]); // Filtered questions for list display
    const [allQuestions, setAllQuestions] = useState([]); // All questions for statistics cards
    const [questionStats, setQuestionStats] = useState({
        totalQuestions: 0,
        activeQuestions: 0,
        inactiveQuestions: 0,
        unknownTopics: 0
    });
    const [isLoadingStats, setIsLoadingStats] = useState(false);
    const [statsRefreshTrigger, setStatsRefreshTrigger] = useState(0); // Trigger for stats refresh
    const [filterSubject, setFilterSubject] = useState('');
    const [filterPaper, setFilterPaper] = useState('');
    const [filterTopic, setFilterTopic] = useState('');
    const [filterStatus, setFilterStatus] = useState('all'); // 'all', 'active', 'inactive'
    
    // Filter IDs for API calls
    const [filterSubjectId, setFilterSubjectId] = useState('');
    const [filterPaperId, setFilterPaperId] = useState('');
    const [filterTopicId, setFilterTopicId] = useState('');
    
    const [availablePapers, setAvailablePapers] = useState([]);
    const [availableTopics, setAvailableTopics] = useState([]);

    // New Subject Form States
    const [newSubjectName, setNewSubjectName] = useState('');
    const [newSubjectPapers, setNewSubjectPapers] = useState([{ name: '', topics: [''], sections: [''] }]);

    // CRUD States for Subject Management
    const [existingSubjects, setExistingSubjects] = useState([]);
    const [isLoadingSubjects, setIsLoadingSubjects] = useState(false);
    const [showEditModal, setShowEditModal] = useState(false);
    const [editingItem, setEditingItem] = useState(null); // { type: 'subject'|'paper'|'topic'|'section', data: {...} }
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [deletingItem, setDeletingItem] = useState(null);
    const [expandedSubjects, setExpandedSubjects] = useState({}); // Track which subjects are expanded
    const [expandedPapers, setExpandedPapers] = useState({}); // Track which papers are expanded
    
    // Full subject edit states
    const [editSubjectData, setEditSubjectData] = useState(null);
    const [showFullEditModal, setShowFullEditModal] = useState(false);
    const [selectedPaperIndices, setSelectedPaperIndices] = useState([]); // Papers selected for editing
    const [showTopicsModal, setShowTopicsModal] = useState(false);
    const [viewingPaperTopics, setViewingPaperTopics] = useState(null); // { paperName: '', topics: [], sections: [] }

    // Dynamic subjects loaded from database
    const [subjects, setSubjects] = useState({});
    const [isLoadingDynamicSubjects, setIsLoadingDynamicSubjects] = useState(false);

    // Legacy hardcoded subject configuration (fallback only)
    const fallbackSubjects = {
        'Mathematics': {
            topics: ['Algebra', 'Geometry', 'Calculus', 'Statistics', 'Trigonometry'],
            papers: ['Paper 1', 'Paper 2', 'Paper 3'],
            sections: {
                'Paper 1': ['Section A', 'Section B', 'Section C'],
                'Paper 2': ['Section A', 'Section B'],
                'Paper 3': []
            }
        },
        'English': {
            topics: ['Grammar', 'Composition', 'Literature', 'Comprehension'],
            papers: ['Paper 1', 'Paper 2'],
            sections: {
                'Paper 1': ['Section A', 'Section B', 'Section C'],
                'Paper 2': ['Section A', 'Section B']
            }
        },
        'Physics': {
            topics: ['Mechanics', 'Electricity', 'Waves', 'Thermodynamics', 'Modern Physics'],
            papers: ['Paper 1', 'Paper 2', 'Paper 3'],
            sections: {
                'Paper 1': ['Section A', 'Section B'],
                'Paper 2': [],
                'Paper 3': ['Section A']
            }
        },
        'Chemistry': {
            topics: ['Organic Chemistry', 'Inorganic Chemistry', 'Physical Chemistry', 'Analytical Chemistry'],
            papers: ['Paper 1', 'Paper 2', 'Paper 3'],
            sections: {
                'Paper 1': ['Section A', 'Section B'],
                'Paper 2': [],
                'Paper 3': ['Section A']
            }
        },
        'Biology': {
            topics: ['Cell Biology', 'Genetics', 'Evolution', 'Ecology', 'Human Biology'],
            papers: ['Paper 1', 'Paper 2', 'Paper 3'],
            sections: {
                'Paper 1': ['Section A', 'Section B'],
                'Paper 2': [],
                'Paper 3': ['Section A']
            }
        },
        'History': {
            topics: ['World Wars', 'African History', 'Modern History', 'Ancient Civilizations'],
            papers: ['Paper 1', 'Paper 2'],
            sections: {
                'Paper 1': ['Section A', 'Section B', 'Section C'],
                'Paper 2': ['Section A', 'Section B']
            }
        },
        'Geography': {
            topics: ['Physical Geography', 'Human Geography', 'Map Work', 'Climate'],
            papers: ['Paper 1', 'Paper 2'],
            sections: {
                'Paper 1': ['Section A', 'Section B'],
                'Paper 2': ['Section A', 'Section B']
            }
        }
    };
    // Memoize statistics computation to avoid repeated heavy recalculation
    const memoizedStatistics = useMemo(() => getStatistics(), [allQuestions, filterSubject, filterPaper, filterTopic, filterStatus]);

    // Memoize filtered questions used in stats to avoid recomputing during render
    const memoizedFilteredQuestions = useMemo(() => getFilteredQuestions(), [savedQuestions]);

    // Load subjects from database for question entry dropdowns
    const loadDynamicSubjects = async () => {
        setIsLoadingDynamicSubjects(true);
        try {
            const subjectsData = await subjectService.getAllSubjects();
            
            // Transform database subjects into the format expected by the UI
            const transformedSubjects = {};
            subjectsData.forEach(subject => {
                if (subject.isActive !== false) { // Include active subjects
                    const papers = subject.papers || [];
                    const papersMap = {};
                    const sectionsMap = {};
                    const topicsMap = {}; // Store topics per paper

                    papers.forEach(paper => {
                        if (paper.isActive !== false && paper.name) {
                            papersMap[paper.name] = paper;
                            
                            // Get sections for this paper
                            const sections = (paper.sections || [])
                                .filter(s => s && s.name)
                                .map(s => s.name);
                            sectionsMap[paper.name] = sections;

                            // Store topics for this specific paper
                            const topics = (paper.topics || [])
                                .filter(t => t && t.name)
                                .map(t => t.name);
                            topicsMap[paper.name] = topics;
                        }
                    });

                    transformedSubjects[subject.name] = {
                        papers: Object.keys(papersMap),
                        sections: sectionsMap,
                        topics: topicsMap, // Changed: topics now organized by paper
                        papersData: papersMap, // Store full paper data
                        id: subject.id
                    };
                }
            });

            setSubjects(transformedSubjects);
            console.log('Loaded dynamic subjects:', transformedSubjects);
        } catch (error) {
            console.error('Error loading dynamic subjects:', error);
            // Fallback to hardcoded subjects on error
            setSubjects(fallbackSubjects);
        } finally {
            setIsLoadingDynamicSubjects(false);
        }
    };

    // Fetch questions from database
    const fetchQuestions = async (filters = {}) => {
        try {
            const questions = await questionService.getAllQuestions(filters);
            console.log('Fetched questions:', questions.length, questions);
            // Ensure we always set an array
            setSavedQuestions(Array.isArray(questions) ? questions : []);
            return Array.isArray(questions) ? questions : [];
        } catch (error) {
            console.error('Error fetching questions:', error);
            setSavedQuestions([]);
            return [];
        }
    };

    // Fetch statistics from database
    const fetchStatistics = async () => {
        setIsLoadingStats(true);
        try {
            const stats = await questionService.getQuestionStats();
            setQuestionStats({
                totalQuestions: stats.total || 0,
                activeQuestions: stats.active || 0,
                inactiveQuestions: stats.inactive || 0,
                unknownTopics: stats.unknownTopics || 0
            });
        } catch (error) {
            console.error('Error fetching statistics:', error);
        } finally {
            setIsLoadingStats(false);
        }
    };

    // Fetch topics for a specific paper (for edit question dropdown)
    const fetchTopicsForPaper = async (paperId) => {
        try {
            console.log('[fetchTopicsForPaper] Starting fetch for paper ID:', paperId);
            
            const token = localStorage.getItem('token');
            if (!token) {
                console.error('[fetchTopicsForPaper] No auth token found');
                setEditQuestionTopics([]);
                return;
            }
            
            const response = await fetch(`${API_URL}/subjects`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            
            console.log('[fetchTopicsForPaper] Response status:', response.status, response.ok);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('[fetchTopicsForPaper] Failed to fetch subjects. Status:', response.status);
                console.error('[fetchTopicsForPaper] Error text:', errorText);
                throw new Error(`Failed to fetch subjects: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('[fetchTopicsForPaper] Received data:', data);
            const subjects = data.data || [];
            console.log('[fetchTopicsForPaper] Processing', subjects.length, 'subjects to find paper:', paperId);
            
            // Find the paper in subjects and get its topics
            for (const subject of subjects) {
                console.log('[fetchTopicsForPaper] Checking subject:', subject.name, '| Papers count:', subject.papers?.length);
                if (subject.papers) {
                    subject.papers.forEach(p => {
                        console.log('  Paper ID:', p.id, '| Name:', p.name, '| Topics count:', p.topics?.length);
                    });
                }
                const paper = subject.papers?.find(p => p.id === paperId);
                if (paper) {
                    console.log('[fetchTopicsForPaper] FOUND matching paper!');
                    console.log('[fetchTopicsForPaper] Paper name:', paper.name);
                    console.log('[fetchTopicsForPaper] Topics:', paper.topics);
                    console.log('[fetchTopicsForPaper] Sections:', paper.sections);
                    console.log('[fetchTopicsForPaper] Setting editQuestionTopics with', paper.topics?.length, 'topics');
                    setEditQuestionTopics(paper.topics || []);
                    setEditQuestionSections(paper.sections || []); // Set sections too
                    return;
                }
            }
            
            console.warn('[fetchTopicsForPaper] No paper found with ID:', paperId);
            console.warn('[fetchTopicsForPaper] Setting editQuestionTopics and sections to empty array');
            setEditQuestionTopics([]);
            setEditQuestionSections([]);
        } catch (error) {
            console.error('[fetchTopicsForPaper] Error:', error);
            console.error('[fetchTopicsForPaper] Error stack:', error.stack);
            setEditQuestionTopics([]);
        }
    };

    // Update available papers when subject filter changes
    useEffect(() => {
        if (filterSubject && existingSubjects.length > 0) {
            const subject = existingSubjects.find(s => s.name === filterSubject);
            if (subject) {
                setAvailablePapers(subject.papers || []);
                setFilterSubjectId(subject.id); // Store subject ID
                
                // Reset paper and topic filters
                setFilterPaper('');
                setFilterTopic('');
                setFilterPaperId('');
                setFilterTopicId('');
                setAvailableTopics([]);
            }
        } else {
            setAvailablePapers([]);
            setAvailableTopics([]);
            setFilterSubjectId('');
            setFilterPaperId('');
            setFilterTopicId('');
        }
    }, [filterSubject, existingSubjects]);

    // Update available topics when paper filter changes
    useEffect(() => {
        if (filterSubject && filterPaper && availablePapers.length > 0) {
            const paper = availablePapers.find(p => p.name === filterPaper);
            if (paper) {
                setAvailableTopics(paper.topics || []);
                setFilterPaperId(paper.id); // Store paper ID
                setFilterTopic('');
                setFilterTopicId('');
            }
        } else {
            setAvailableTopics([]);
            setFilterPaperId('');
            setFilterTopicId('');
        }
    }, [filterPaper, availablePapers, filterSubject]);

    // Update topic ID when topic filter changes
    useEffect(() => {
        if (filterTopic && availableTopics.length > 0) {
            const topic = availableTopics.find(t => t.name === filterTopic);
            if (topic) {
                setFilterTopicId(topic.id);
            }
        } else {
            setFilterTopicId('');
        }
    }, [filterTopic, availableTopics]);

    // Fetch statistics and questions when statistics tab is active or when refresh triggered
    useEffect(() => {
        if (activeTab === 'stats') {
            fetchStatistics();
            // Fetch ALL questions for statistics cards (no limit)
            fetchQuestions({ limit: 10000 }).then(questions => {
                setAllQuestions(questions || []);
                setSavedQuestions(questions || []); // Initially show all questions
            });
            fetchSubjects(); // Load subjects for filter dropdowns
        }
    }, [activeTab, statsRefreshTrigger]);

    // Refetch questions when filters change in statistics tab (only affects question list, not cards)
    useEffect(() => {
        if (activeTab === 'stats') {
            const filters = {};
            // Use IDs instead of names for API calls
            if (filterSubjectId) filters.subject = filterSubjectId;
            if (filterPaperId) filters.paper = filterPaperId;
            if (filterTopicId) filters.topic = filterTopicId;
            if (filterStatus === 'active') filters.isActive = 'true';
            if (filterStatus === 'inactive') filters.isActive = 'false';
            
            // Only fetch if filters are applied
            if (Object.keys(filters).length > 0) {
                fetchQuestions(filters).then(questions => {
                    setSavedQuestions(questions || []);
                });
            } else {
                // No filters - show all questions
                setSavedQuestions(allQuestions);
            }
        }
    }, [filterSubjectId, filterPaperId, filterTopicId, filterStatus, activeTab, allQuestions]);

    // Load subjects when component mounts or when subjects tab is active
    useEffect(() => {
        loadDynamicSubjects();
    }, []);

    // Reload subjects when returning to questions tab after editing subjects
    useEffect(() => {
        if (activeTab === 'questions') {
            loadDynamicSubjects();
        }
    }, [activeTab]);

    // Search for similar questions when question text changes
    useEffect(() => {
        const searchSimilarQuestions = async () => {
            // Only search if we have meaningful text and a selected subject
            if (questionText.length > 15 && selectedSubject) {
                setIsSearching(true);
                
                try {
                    // Extract just the text content (remove image placeholders)
                    const cleanText = questionText.replace(/\[IMAGE:[\d.]+:(?:\d+x\d+|\d+)px\]/g, '').trim();
                    
                    if (cleanText.length < 15) {
                        setSimilarQuestions([]);
                        setIsSearching(false);
                        return;
                    }
                    
                    // Get auth token
                    const token = localStorage.getItem('token');
                    
                    if (!token) {
                        console.warn('No auth token found for similar questions search');
                        setSimilarQuestions([]);
                        setIsSearching(false);
                        return;
                    }
                    
                    // Call API to search for similar questions
                    const response = await fetch(`${API_URL}/questions/search-similar/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({
                            question_text: cleanText,
                            subject: selectedSubject,
                            limit: 5  // Get top 5 similar questions
                        })
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        console.log('Similar questions response:', data);
                        const similarQuestions = data.data?.similar_questions || data.similar_questions || [];
                        console.log('Similar questions found:', similarQuestions.length, similarQuestions);
                        setSimilarQuestions(similarQuestions);
                    } else {
                        console.error('Failed to fetch similar questions:', response.status);
                        setSimilarQuestions([]);
                    }
                } catch (error) {
                    console.error('Error searching for similar questions:', error);
                    setSimilarQuestions([]);
                } finally {
                    setIsSearching(false);
                }
            } else {
                setSimilarQuestions([]);
                setIsSearching(false);
            }
        };
        
        // Debounce the search - wait 800ms after user stops typing
        const timer = setTimeout(() => {
            searchSimilarQuestions();
        }, 800);
        
        return () => clearTimeout(timer);
    }, [questionText, selectedSubject]);

    // Update available papers when subject filter changes in edit section
    useEffect(() => {
        if (editFilterSubject && existingSubjects.length > 0) {
            const subject = existingSubjects.find(s => s.name === editFilterSubject);
            if (subject) {
                setEditAvailablePapers(subject.papers || []);
                // Reset dependent filters
                setEditFilterPaper('');
                setEditFilterTopic('');
                setEditAvailableTopics([]);
            }
        } else {
            setEditAvailablePapers([]);
            setEditAvailableTopics([]);
        }
    }, [editFilterSubject, existingSubjects]);

    // Update available topics when paper filter changes in edit section
    useEffect(() => {
        if (editFilterSubject && editFilterPaper && editAvailablePapers.length > 0) {
            const paper = editAvailablePapers.find(p => p.name === editFilterPaper);
            if (paper) {
                setEditAvailableTopics(paper.topics || []);
                setEditFilterTopic('');
            }
        } else {
            setEditAvailableTopics([]);
        }
    }, [editFilterPaper, editAvailablePapers, editFilterSubject]);

    // ====== HELPER FUNCTION: RENDER TEXT WITH IMAGES ======
    /**
     * Renders text content with inline images displayed properly
     * @param {string} text - The text with placeholders like [IMAGE:id:WxH]
     * @param {Array} images - Array of image objects with {id, url, name}
     * @param {Object} imagePositions - Object with image positions {imageId: {x, y}}
     * @param {Array} answerLines - Array of answer line configurations
     * @param {Function} onRemoveImage - Optional callback to remove image
     * @param {Function} onRemoveLines - Optional callback to remove lines
     * @param {string} context - Context identifier (e.g., 'preview', 'edit', 'similar')
     * @returns {Array} - React elements to render
     */
    const renderTextWithImages = (text, images = [], imagePositions = {}, answerLines = [], onRemoveImage = null, onRemoveLines = null, context = 'preview') => {
        if (!text) return [];
        
        return text.split(/(\*\*.*?\*\*|\*.*?\*|__.*?__|_.*?_|\[IMAGE:[\d.]+:(?:\d+x\d+|\d+)px\]|\[LINES:[\d.]+\])/g).map((part, index) => {
            // Bold formatting
            if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
                const content = part.slice(2, -2);
                return <strong key={index}>{content}</strong>;
            }
            
            // Italic formatting
            if (part.startsWith('*') && part.endsWith('*') && !part.startsWith('**') && part.length > 2) {
                const content = part.slice(1, -1);
                return <em key={index} className="italic">{content}</em>;
            }
            
            // Underline formatting
            if (part.startsWith('__') && part.endsWith('__') && part.length > 4) {
                const content = part.slice(2, -2);
                return <u key={index}>{content}</u>;
            }
            
            // Single underscore italic
            if (part.startsWith('_') && part.endsWith('_') && !part.startsWith('__') && part.length > 2) {
                const content = part.slice(1, -1);
                return <em key={index} className="italic">{content}</em>;
            }
            
            // Answer lines
            const linesMatch = part.match(/\[LINES:([\d.]+)\]/);
            if (linesMatch) {
                const lineId = parseFloat(linesMatch[1]);
                const lineConfig = answerLines.find(line => line.id === lineId);
                
                if (lineConfig) {
                    const maxWidth = 700;
                    const fullLines = Math.floor(lineConfig.numberOfLines);
                    const hasHalfLine = lineConfig.numberOfLines % 1 !== 0;
                    
                    return (
                        <div key={index} className="my-2 relative group" style={{ maxWidth: `${maxWidth}px` }}>
                            {[...Array(fullLines)].map((_, idx) => (
                                <div
                                    key={idx}
                                    style={{
                                        height: `${lineConfig.lineHeight}px`,
                                        borderBottom: `2px ${lineConfig.lineStyle} rgba(0, 0, 0, ${lineConfig.opacity})`,
                                        width: '100%'
                                    }}
                                ></div>
                            ))}
                            {hasHalfLine && (
                                <div
                                    style={{
                                        height: `${lineConfig.lineHeight / 2}px`,
                                        borderBottom: `2px ${lineConfig.lineStyle} rgba(0, 0, 0, ${lineConfig.opacity})`,
                                        width: '100%'
                                    }}
                                ></div>
                            )}
                            {onRemoveLines && (
                                <button
                                    type="button"
                                    onClick={() => onRemoveLines(lineId)}
                                    className="absolute -top-2 -right-2 bg-red-500 hover:bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-lg text-xs font-bold z-10"
                                    title="Remove lines"
                                >
                                    ✕
                                </button>
                            )}
                        </div>
                    );
                } else {
                    // Show placeholder when line config not found (e.g., lines from DB without config loaded)
                    // This can happen if the question was created but the line configuration wasn't saved properly
                    return (
                        <div key={index} className="my-2 p-4 bg-yellow-50 border-2 border-dashed border-yellow-400 rounded-lg">
                            <div className="flex items-center gap-2 text-sm text-yellow-800">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                </svg>
                                <span className="font-medium">Answer Lines (Configuration Missing)</span>
                            </div>
                            <div className="mt-2 text-xs text-yellow-700">
                                Line ID: {lineId.toFixed(0)} - The line configuration was not found. This might be an old question. 
                                You can remove this placeholder and add new lines if needed.
                            </div>
                        </div>
                    );
                }
            }
            
            // Images
            const imageMatchNew = part.match(/\[IMAGE:([\d.]+):(\d+)x(\d+)px\]/);
            const imageMatchOld = part.match(/\[IMAGE:([\d.]+):(\d+)px\]/);
            
            if (imageMatchNew || imageMatchOld) {
                const imageId = parseFloat(imageMatchNew ? imageMatchNew[1] : imageMatchOld[1]);
                const imageWidth = parseInt(imageMatchNew ? imageMatchNew[2] : imageMatchOld[2]);
                const imageHeight = imageMatchNew ? parseInt(imageMatchNew[3]) : null;
                const image = images.find(img => Math.abs(img.id - imageId) < 0.001);
                const position = imagePositions[imageId];
                
                if (image) {
                    return (
                        <span 
                            key={index} 
                            className={position ? "absolute z-10" : "inline-block align-middle my-2 mx-1"}
                            style={position ? { left: `${position.x}px`, top: `${position.y}px` } : {}}
                        >
                            <span className="relative inline-block group">
                                <img 
                                    src={image.url} 
                                    alt={image.name || 'Question image'}
                                    style={{ 
                                        width: `${imageWidth}px`, 
                                        height: imageHeight ? `${imageHeight}px` : 'auto',
                                        maxWidth: context === 'similar' ? '200px' : '100%',
                                        display: 'block'
                                    }}
                                    className="border-2 border-blue-400 rounded shadow-sm select-none"
                                />
                                
                                {onRemoveImage && (
                                    <button
                                        type="button"
                                        onClick={() => onRemoveImage(imageId)}
                                        className="absolute -top-2 -right-2 bg-red-500 hover:bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-lg text-xs font-bold z-10"
                                        title="Remove image"
                                    >
                                        ✕
                                    </button>
                                )}
                            </span>
                        </span>
                    );
                }
                
                // If image not found, show informative placeholder
                return (
                    <div key={index} className="my-2 p-4 bg-red-50 border-2 border-dashed border-red-300 rounded-lg inline-block">
                        <div className="flex items-center gap-2 text-sm text-red-800">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            <span className="font-medium">Image Not Found</span>
                        </div>
                        <div className="mt-2 text-xs text-red-700">
                            <div>Image ID: {imageId.toFixed(0)}</div>
                            <div>Expected Size: {imageWidth}px × {imageHeight ? imageHeight + 'px' : 'auto'}</div>
                            <div className="mt-1 italic">The image data is missing from the database. This question may need to be re-edited.</div>
                        </div>
                    </div>
                );
            }
            
            // Regular text
            return <span key={index}>{part}</span>;
        });
    };

    const handleSubjectChange = (subject) => {
        setSelectedSubject(subject);
        setSelectedPaper('');
        setSelectedTopic('');
        setSelectedSection('');
        
        // Store subject ID
        if (subjects[subject] && subjects[subject].id) {
            setSelectedSubjectId(subjects[subject].id);
        }
        setSelectedPaperId('');
        setSelectedTopicId('');
        setSelectedSectionId('');
    };

    const handlePaperChange = (paper) => {
        setSelectedPaper(paper);
        setSelectedTopic('');
        setSelectedSection('');
        
        // Store paper ID
        if (selectedSubject && subjects[selectedSubject]?.papersData?.[paper]) {
            const paperData = subjects[selectedSubject].papersData[paper];
            setSelectedPaperId(paperData.id);
        }
        setSelectedTopicId('');
        setSelectedSectionId('');
    };

    const handleTopicChange = (topic) => {
        setSelectedTopic(topic);
        
        // Find topic ID from current paper's topics
        if (selectedSubject && selectedPaper && subjects[selectedSubject]?.papersData?.[selectedPaper]) {
            const paperData = subjects[selectedSubject].papersData[selectedPaper];
            const topicData = paperData.topics?.find(t => t.name === topic);
            if (topicData) {
                setSelectedTopicId(topicData.id);
            }
        }
    };

    const handleSectionChange = (section) => {
        setSelectedSection(section);
        
        // Find section ID from current paper's sections
        if (selectedSubject && selectedPaper && subjects[selectedSubject]?.papersData?.[selectedPaper]) {
            const paperData = subjects[selectedSubject].papersData[selectedPaper];
            const sectionData = paperData.sections?.find(s => s.name === section);
            if (sectionData) {
                setSelectedSectionId(sectionData.id);
            }
        }
    };

    // ====== EDIT QUESTION DRAWING FUNCTIONS ======

    // Initialize edit question canvas
    useEffect(() => {
        if (showEditQuestionDrawing && editQuestionCanvasRef.current) {
            const canvas = editQuestionCanvasRef.current;
            const ctx = canvas.getContext('2d');
            
            const scale = 2;
            const displayWidth = 794;
            const displayHeight = 1123;
            
            canvas.width = displayWidth * scale;
            canvas.height = displayHeight * scale;
            canvas.style.width = displayWidth + 'px';
            canvas.style.height = displayHeight + 'px';
            
            ctx.scale(scale, scale);
            ctx.imageSmoothingEnabled = true;
            ctx.imageSmoothingQuality = 'high';
            ctx.fillStyle = 'white';
            ctx.fillRect(0, 0, displayWidth, displayHeight);
            
            if (showEditQuestionGraphPaper) {
                drawGraphPaper(ctx, displayWidth, displayHeight);
            }
        }
    }, [showEditQuestionDrawing, showEditQuestionGraphPaper]);

    const startEditQuestionDrawing = (e) => {
        setIsEditQuestionDrawing(true);
        const canvas = editQuestionCanvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        setEditQuestionStartPos({ x, y });
        
        const ctx = canvas.getContext('2d');
        
        if (editQuestionDrawingTool === 'pen' || editQuestionDrawingTool === 'eraser') {
            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.strokeStyle = editQuestionDrawingTool === 'eraser' ? 'white' : editQuestionDrawingColor;
            ctx.lineWidth = editQuestionDrawingTool === 'eraser' ? 20 : editQuestionDrawingWidth;
            ctx.lineCap = 'round';
        }
    };

    const drawEditQuestion = (e) => {
        if (!isEditQuestionDrawing) return;
        const canvas = editQuestionCanvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const ctx = canvas.getContext('2d');
        
        if (editQuestionDrawingTool === 'pen') {
            ctx.strokeStyle = editQuestionDrawingColor;
            ctx.lineWidth = editQuestionDrawingWidth;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';
            ctx.lineTo(x, y);
            ctx.stroke();
        } else if (editQuestionDrawingTool === 'eraser') {
            ctx.strokeStyle = 'white';
            ctx.lineWidth = 20;
            ctx.lineCap = 'round';
            ctx.lineTo(x, y);
            ctx.stroke();
        }
    };

    const stopEditQuestionDrawing = (e) => {
        if (!isEditQuestionDrawing) return;
        setIsEditQuestionDrawing(false);
        
        if (editQuestionDrawingTool === 'line' || editQuestionDrawingTool === 'rectangle' || editQuestionDrawingTool === 'circle') {
            const canvas = editQuestionCanvasRef.current;
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const ctx = canvas.getContext('2d');
            
            ctx.strokeStyle = editQuestionDrawingColor;
            ctx.lineWidth = editQuestionDrawingWidth;
            ctx.lineCap = 'round';
            
            if (editQuestionDrawingTool === 'line') {
                ctx.beginPath();
                ctx.moveTo(editQuestionStartPos.x, editQuestionStartPos.y);
                ctx.lineTo(x, y);
                ctx.stroke();
            } else if (editQuestionDrawingTool === 'rectangle') {
                ctx.beginPath();
                const width = x - editQuestionStartPos.x;
                const height = y - editQuestionStartPos.y;
                ctx.strokeRect(editQuestionStartPos.x, editQuestionStartPos.y, width, height);
            } else if (editQuestionDrawingTool === 'circle') {
                ctx.beginPath();
                const radiusX = Math.abs(x - editQuestionStartPos.x) / 2;
                const radiusY = Math.abs(y - editQuestionStartPos.y) / 2;
                const centerX = editQuestionStartPos.x + (x - editQuestionStartPos.x) / 2;
                const centerY = editQuestionStartPos.y + (y - editQuestionStartPos.y) / 2;
                ctx.ellipse(centerX, centerY, radiusX, radiusY, 0, 0, 2 * Math.PI);
                ctx.stroke();
            }
        }
    };

    const clearEditQuestionCanvas = () => {
        const canvas = editQuestionCanvasRef.current;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        if (showEditQuestionGraphPaper) {
            drawGraphPaper(ctx, canvas.width, canvas.height);
        }
    };

    const saveEditQuestionDrawing = () => {
        const canvas = editQuestionCanvasRef.current;
        const imageUrl = canvas.toDataURL('image/png', 1.0);
        const newImage = {
            id: Date.now() + Math.random(),
            url: imageUrl,
            name: 'Edit_Drawing_' + new Date().getTime() + '.png',
            width: 600,
            height: 400,
            position: editQuestionText.length
        };
        setEditQuestionInlineImages(prev => [...prev, newImage]);
        const imagePlaceholder = `\n[IMAGE:${newImage.id}:${newImage.width}x${newImage.height}px]\n`;
        setEditQuestionText(prev => prev + imagePlaceholder);
        setShowEditQuestionDrawing(false);
        alert('✅ Drawing inserted!');
    };

    // ====== SET QUESTION MODE (ESSAY/GRAPH/REGULAR) ======
    // Call backend to update is_essay and is_graph fields for a question
    const setQuestionMode = async (mode) => {
        if (!selectedQuestion) {
            alert('No question selected.');
            return;
        }
        const token = localStorage.getItem('token');
        if (!token) {
            alert('You must be logged in.');
            return;
        }
        try {
            const response = await fetch(`${API_URL}/questions/set-mode/${selectedQuestion.id}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ mode })
            });
            const result = await response.json();
            if (response.ok && result.success) {
                alert('Question mode updated!');
                // Update local state for UI
                setEditIsEssayQuestion(result.data.is_essay);
                setEditIsGraphQuestion(result.data.is_graph);
            } else {
                alert(result.message || 'Failed to update question mode.');
            }
        } catch (error) {
            alert('Error updating question mode.');
        }
    };

    // ====== EDIT ANSWER DRAWING FUNCTIONS ======

    useEffect(() => {
        if (showEditAnswerDrawing && editAnswerCanvasRef.current) {
            const canvas = editAnswerCanvasRef.current;
            const ctx = canvas.getContext('2d');
            
            const scale = 2;
            const displayWidth = 794;
            const displayHeight = 1123;
            
            canvas.width = displayWidth * scale;
            canvas.height = displayHeight * scale;
            canvas.style.width = displayWidth + 'px';
            canvas.style.height = displayHeight + 'px';
            
            ctx.scale(scale, scale);
            ctx.fillStyle = 'white';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            if (showEditAnswerGraphPaper) {
                drawGraphPaper(ctx, displayWidth, displayHeight);
            }
        }
    }, [showEditAnswerDrawing, showEditAnswerGraphPaper]);

    const startEditAnswerDrawing = (e) => {
        setIsEditAnswerDrawing(true);
        const canvas = editAnswerCanvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        setEditAnswerStartPos({ x, y });
        
        const ctx = canvas.getContext('2d');
        ctx.strokeStyle = editAnswerDrawingColor;
        ctx.lineWidth = editAnswerDrawingWidth;
        ctx.lineCap = 'round';
        
        if (editAnswerDrawingTool === 'pen' || editAnswerDrawingTool === 'eraser') {
            ctx.beginPath();
            ctx.moveTo(x, y);
        }
    };

    const drawEditAnswer = (e) => {
        if (!isEditAnswerDrawing) return;
        
        const canvas = editAnswerCanvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const ctx = canvas.getContext('2d');
        
        if (editAnswerDrawingTool === 'pen') {
            ctx.strokeStyle = editAnswerDrawingColor;
            ctx.lineWidth = editAnswerDrawingWidth;
            ctx.lineTo(x, y);
            ctx.stroke();
        } else if (editAnswerDrawingTool === 'eraser') {
            ctx.globalCompositeOperation = 'destination-out';
            ctx.lineWidth = editAnswerDrawingWidth * 2;
            ctx.lineTo(x, y);
            ctx.stroke();
            ctx.globalCompositeOperation = 'source-over';
        }
    };

    const stopEditAnswerDrawing = (e) => {
        if (!isEditAnswerDrawing) return;
        setIsEditAnswerDrawing(false);
        
        if (editAnswerDrawingTool === 'line' || editAnswerDrawingTool === 'rectangle' || editAnswerDrawingTool === 'circle') {
            const canvas = editAnswerCanvasRef.current;
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const ctx = canvas.getContext('2d');
            
            ctx.strokeStyle = editAnswerDrawingColor;
            ctx.lineWidth = editAnswerDrawingWidth;
            ctx.lineCap = 'round';
            
            if (editAnswerDrawingTool === 'line') {
                ctx.beginPath();
                ctx.moveTo(editAnswerStartPos.x, editAnswerStartPos.y);
                ctx.lineTo(x, y);
                ctx.stroke();
            } else if (editAnswerDrawingTool === 'rectangle') {
                ctx.beginPath();
                const width = x - editAnswerStartPos.x;
                const height = y - editAnswerStartPos.y;
                ctx.strokeRect(editAnswerStartPos.x, editAnswerStartPos.y, width, height);
            } else if (editAnswerDrawingTool === 'circle') {
                ctx.beginPath();
                const radiusX = Math.abs(x - editAnswerStartPos.x) / 2;
                const radiusY = Math.abs(y - editAnswerStartPos.y) / 2;
                const centerX = editAnswerStartPos.x + (x - editAnswerStartPos.x) / 2;
                const centerY = editAnswerStartPos.y + (y - editAnswerStartPos.y) / 2;
                ctx.ellipse(centerX, centerY, radiusX, radiusY, 0, 0, 2 * Math.PI);
                ctx.stroke();
            }
        }
    };

    const clearEditAnswerCanvas = () => {
        const canvas = editAnswerCanvasRef.current;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        if (showEditAnswerGraphPaper) {
            drawGraphPaper(ctx, canvas.width, canvas.height);
        }
    };

    const saveEditAnswerDrawing = () => {
        const canvas = editAnswerCanvasRef.current;
        const imageUrl = canvas.toDataURL('image/png', 1.0);
        const newImage = {
            id: Date.now() + Math.random(),
            url: imageUrl,
            name: 'Edit_Answer_Drawing_' + new Date().getTime() + '.png',
            width: 600,
            height: 400,
            position: editAnswerText.length
        };
        
        setEditAnswerInlineImages(prev => [...prev, newImage]);
        const imagePlaceholder = `\n[IMAGE:${newImage.id}:${newImage.width}x${newImage.height}px]\n`;
        setEditAnswerText(prev => prev + imagePlaceholder);
        
        setShowEditAnswerDrawing(false);
        alert('Answer drawing inserted!');
    };

    // ====== EDIT VOICE RECORDING FUNCTIONS ======

    const toggleEditQuestionVoiceRecording = () => {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert('Voice recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
            return;
        }

        if (isEditQuestionListening) {
            if (editQuestionRecognitionRef.current) {
                editQuestionRecognitionRef.current.stop();
            }
            setIsEditQuestionListening(false);
        } else {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            
            recognition.onstart = () => {
                setIsEditQuestionListening(true);
            };
            
            recognition.onresult = (event) => {
                let finalTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript + ' ';
                    }
                }
                
                if (finalTranscript) {
                    setEditQuestionText(prev => prev + finalTranscript);
                }
            };
            
            recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                setIsEditQuestionListening(false);
                if (event.error !== 'no-speech') {
                    alert('Voice recognition error: ' + event.error);
                }
            };
            
            recognition.onend = () => {
                setIsEditQuestionListening(false);
            };
            
            editQuestionRecognitionRef.current = recognition;
            recognition.start();
        }
    };

    const toggleEditAnswerVoiceRecording = () => {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert('Voice recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
            return;
        }

        if (isEditAnswerListening) {
            if (editAnswerRecognitionRef.current) {
                editAnswerRecognitionRef.current.stop();
            }
            setIsEditAnswerListening(false);
        } else {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            
            recognition.onstart = () => {
                setIsEditAnswerListening(true);
            };
            
            recognition.onresult = (event) => {
                let finalTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript + ' ';
                    }
                }
                
                if (finalTranscript) {
                    setEditAnswerText(prev => prev + finalTranscript);
                }
            };
            
            recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                setIsEditAnswerListening(false);
                if (event.error !== 'no-speech') {
                    alert('Voice recognition error: ' + event.error);
                }
            };
            
            recognition.onend = () => {
                setIsEditAnswerListening(false);
            };
            
            editAnswerRecognitionRef.current = recognition;
            recognition.start();
        }
    };

    // File upload handlers for edit mode
    const handleEditQuestionFileUpload = (e) => {
        const files = Array.from(e.target.files);
        files.forEach(file => {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    const newImage = {
                        id: Date.now() + Math.random(),
                        url: event.target.result,
                        name: file.name,
                        width: 300,
                        height: 200,
                        position: editQuestionText.length
                    };
                    
                    setEditQuestionInlineImages(prev => [...prev, newImage]);
                    
                    setTimeout(() => {
                        const imagePlaceholder = `\n[IMAGE:${newImage.id}:${newImage.width}x${newImage.height}px]\n`;
                        setEditQuestionText(prev => prev + imagePlaceholder);
                    }, 100);
                };
                reader.readAsDataURL(file);
            }
        });
    };

    const handleEditAnswerFileUpload = (e) => {
        const files = Array.from(e.target.files);
        files.forEach(file => {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    const newImage = {
                        id: Date.now() + Math.random(),
                        url: event.target.result,
                        name: file.name,
                        width: 300,
                        height: 200,
                        position: editAnswerText.length
                    };
                    
                    setEditAnswerInlineImages(prev => [...prev, newImage]);
                    
                    setTimeout(() => {
                        const imagePlaceholder = `\n[IMAGE:${newImage.id}:${newImage.width}x${newImage.height}px]\n`;
                        setEditAnswerText(prev => prev + imagePlaceholder);
                    }, 100);
                };
                reader.readAsDataURL(file);
            }
        });
    };

// Cleanup speech recognition on unmount
useEffect(() => {
    return () => {
        if (editQuestionRecognitionRef.current) {
            editQuestionRecognitionRef.current.stop();
        }
        if (editAnswerRecognitionRef.current) {
            editAnswerRecognitionRef.current.stop();
        }
    };
}, []);

    // Handler for contentEditable input
    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!selectedSubject || !selectedPaper) {
            alert('Please select subject and paper');
            return;
        }

        if (!selectedSubjectId || !selectedPaperId) {
            alert('Error: Subject or Paper ID not found. Please reselect your options.');
            return;
        }

        if (!questionText.trim()) {
            alert('Please enter the question text');
            return;
        }

        if (!answerText.trim()) {
            alert('Please enter the answer text');
            return;
        }

        if (!marks || parseInt(marks) <= 0) {
            alert('Please enter valid marks');
            return;
        }

        if (!selectedTopic || !selectedTopicId) {
            alert('Please select a topic');
            return;
        }

        try {
            // Prepare question data for API using UUIDs
            const questionData = {
                subject: selectedSubjectId,
                paper: selectedPaperId,
                topic: selectedTopicId,
                section: selectedSectionId || null,
                question_text: questionText,
                answer_text: answerText,
                marks: parseInt(marks),
                is_nested: isNested, // NEW: Nested question flag
                is_essay: isEssayQuestion, // NEW: Essay question flag
                is_graph: isGraphQuestion, // NEW: Graph question flag
                question_inline_images: questionInlineImages,
                answer_inline_images: answerInlineImages,
                question_image_positions: questionImagePositions, // NEW: Image positions for question
                answer_image_positions: answerImagePositions, // NEW: Image positions for answer
                question_answer_lines: questionAnswerLines, // NEW: Answer lines in question section
                answer_answer_lines: answerAnswerLines, // NEW: Answer lines in answer section
                is_active: isQuestionActive
            };

            console.log('💾 Submitting question to database:', questionData);
            console.log('📋 Question Status Being Saved:', {
                isActive: isQuestionActive,
                isNested: isNested,
                isEssayQuestion: isEssayQuestion,
                isGraphQuestion: isGraphQuestion,
                marks: parseInt(marks),
                questionLength: questionText.length,
                answerLength: answerText.length
            });
            console.log('💾 Question images being saved:', {
                count: questionInlineImages.length,
                images: questionInlineImages,
                firstImageUrl: questionInlineImages[0]?.url?.substring(0, 50) + '...'
            });
            console.log('💾 Answer images being saved:', {
                count: answerInlineImages.length,
                images: answerInlineImages
            });

            // Get auth token from localStorage
            const token = localStorage.getItem('token');
            
            if (!token) {
                alert('You must be logged in to create questions');
                return;
            }

            // Send to database
            const response = await fetch(`${API_URL}/questions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(questionData)
            });

            const result = await response.json();

            if (response.ok && result.success) {
                // Save to local state for immediate UI update
                const savedQuestion = {
                    id: result.data.id,
                    subject: selectedSubject,
                    topic: selectedTopic || 'Unknown',
                    paper: selectedPaper,
                    section: selectedSection || 'No Section',
                    questionText,
                    answerText,
                    marks: parseInt(marks),
                    status: isQuestionActive ? 'Active' : 'Inactive',
                    questionImages: questionInlineImages,
                    answerImages: answerInlineImages,
                    timestamp: new Date().toISOString()
                };
                setSavedQuestions(prev => [...prev, savedQuestion]);
                
                // Refresh statistics immediately
                fetchStatistics();
                
                // Trigger stats refresh for when user switches to stats tab
                setStatsRefreshTrigger(prev => prev + 1);
                
                // Clear form after successful submission
                setQuestionText('');
                setAnswerText('');
                setMarks('');
                setUploadedImages([]);
                setUploadedAnswerImages([]);
                setQuestionInlineImages([]);
                setAnswerInlineImages([]);
                setQuestionImagePositions({}); // NEW: Clear image positions
                setAnswerImagePositions({}); // NEW: Clear image positions
                setQuestionAnswerLines([]); // NEW: Clear answer lines
                setAnswerAnswerLines([]); // NEW: Clear answer lines
                setIsQuestionActive(true);
                setIsNested(false); // NEW: Reset nested checkbox
                setIsEssayQuestion(false); // NEW: Reset essay checkbox
                setIsGraphQuestion(false); // NEW: Reset graph checkbox
                setSimilarQuestions([]);
                
                alert('Question saved to database successfully!');
                console.log('Question saved:', result);
            } else {
                console.error('Failed to save question:', result);
                alert(`Failed to save question: ${result.message || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Error submitting question:', error);
            alert('Error submitting question. Please check your connection and try again.');
        }
    };

    // File upload handler
    const handleFileUpload = (e) => {
        const files = Array.from(e.target.files);
        files.forEach(file => {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    const newImage = {
                        id: Date.now() + Math.random(),
                        url: event.target.result,
                        name: file.name,
                        width: 300, // Default width
                        height: 200, // Default height
                        position: questionText.length
                    };
                    
                    // Add to both inline images and uploaded images
                    setQuestionInlineImages(prev => [...prev, newImage]);
                    setUploadedImages(prev => [...prev, newImage]);
                    
                    // Auto-insert the image directly into content - pass image object directly
                    setTimeout(() => {
                        insertInlineImageDirect(newImage, 'question');
                    }, 100);
                };
                reader.readAsDataURL(file);
            }
        });
    };

    // Remove uploaded image
    const removeImage = (imageId) => {
        setUploadedImages(prev => prev.filter(img => img.id !== imageId));
        removeInlineImage(imageId, 'question');
    };

    // Canvas drawing functions
    useEffect(() => {
        if (showDrawingTool && canvasRef.current) {
            const canvas = canvasRef.current;
            const ctx = canvas.getContext('2d');
            
            // Set canvas size to A4 printable area: 210mm x 297mm
            // At 96 DPI: 210mm = ~794px, 297mm = ~1123px
            // Using 2x scale for better image quality (prevents blur)
            const scale = 2;
            const displayWidth = 794;  // A4 width at 96 DPI
            const displayHeight = 1123; // A4 height at 96 DPI
            
            canvas.width = displayWidth * scale;
            canvas.height = displayHeight * scale;
            canvas.style.width = displayWidth + 'px';
            canvas.style.height = displayHeight + 'px';
            
            // Scale context for high-DPI displays
            ctx.scale(scale, scale);
            
            // Enable image smoothing for better quality
            ctx.imageSmoothingEnabled = true;
            ctx.imageSmoothingQuality = 'high';
            
            // Fill white background
            ctx.fillStyle = 'white';
            ctx.fillRect(0, 0, displayWidth, displayHeight);
            
            if (showGraphPaper) {
                drawGraphPaper(ctx, displayWidth, displayHeight);
            }
        }
    }, [showDrawingTool, showGraphPaper]);

    const drawGraphPaper = (ctx, width, height) => {
        const gridSize = 10; // 10px per unit square
        ctx.strokeStyle = '#e0e0e0';
        ctx.lineWidth = 0.5;

        // Draw vertical lines
        for (let x = 0; x <= width; x += gridSize) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, height);
            ctx.stroke();
        }

        // Draw horizontal lines
        for (let y = 0; y <= height; y += gridSize) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(width, y);
            ctx.stroke();
        }

        // Draw thicker lines every 10 grid units (100px = 10 squares)
        ctx.strokeStyle = '#b0b0b0';
        ctx.lineWidth = 1;
        for (let x = 0; x <= width; x += gridSize * 10) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, height);
            ctx.stroke();
        }
        for (let y = 0; y <= height; y += gridSize * 10) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(width, y);
            ctx.stroke();
        }
    };

    const startDrawing = (e) => {
        setIsDrawing(true);
        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Store starting position for shapes
        setStartPos({ x, y });
        
        const ctx = canvas.getContext('2d');
        
        // For freehand pen and eraser, start path immediately
        if (drawingTool === 'pen' || drawingTool === 'eraser') {
            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.strokeStyle = drawingTool === 'eraser' ? 'white' : drawingColor;
            ctx.lineWidth = drawingTool === 'eraser' ? 20 : drawingWidth;
            ctx.lineCap = 'round';
        }
    };

    const draw = (e) => {
        if (!isDrawing) return;
        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const ctx = canvas.getContext('2d');
        
        if (drawingTool === 'pen') {
            // Freehand drawing with smoothing
            ctx.strokeStyle = drawingColor;
            ctx.lineWidth = drawingWidth;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';
            ctx.lineTo(x, y);
            ctx.stroke();
        } else if (drawingTool === 'eraser') {
            // Eraser (white pen)
            ctx.strokeStyle = 'white';
            ctx.lineWidth = 20;
            ctx.lineCap = 'round';
            ctx.lineTo(x, y);
            ctx.stroke();
        }
        // For shapes (line, rectangle, circle), drawing happens on mouseup
    };

    const stopDrawing = (e) => {
        if (!isDrawing) return;
        setIsDrawing(false);
        
        // For shapes, draw them when mouse is released
        if (drawingTool === 'line' || drawingTool === 'rectangle' || drawingTool === 'circle') {
            const canvas = canvasRef.current;
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const ctx = canvas.getContext('2d');
            
            ctx.strokeStyle = drawingColor;
            ctx.lineWidth = drawingWidth;
            ctx.lineCap = 'round';
            
            if (drawingTool === 'line') {
                // Draw straight line from start to end
                ctx.beginPath();
                ctx.moveTo(startPos.x, startPos.y);
                ctx.lineTo(x, y);
                ctx.stroke();
            } else if (drawingTool === 'rectangle') {
                // Draw rectangle
                ctx.beginPath();
                const width = x - startPos.x;
                const height = y - startPos.y;
                ctx.strokeRect(startPos.x, startPos.y, width, height);
            } else if (drawingTool === 'circle') {
                // Draw circle/ellipse
                ctx.beginPath();
                const radiusX = Math.abs(x - startPos.x) / 2;
                const radiusY = Math.abs(y - startPos.y) / 2;
                const centerX = startPos.x + (x - startPos.x) / 2;
                const centerY = startPos.y + (y - startPos.y) / 2;
                ctx.ellipse(centerX, centerY, radiusX, radiusY, 0, 0, 2 * Math.PI);
                ctx.stroke();
            }
        }
    };

    const clearCanvas = () => {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        if (showGraphPaper) {
            drawGraphPaper(ctx, canvas.width, canvas.height);
        }
    };

    const saveDrawing = () => {
        const canvas = canvasRef.current;
        // Export at high quality - PNG format preserves quality
        const imageUrl = canvas.toDataURL('image/png', 1.0);
        const newImage = {
            id: Date.now(),
            url: imageUrl,
            name: 'Drawing_' + new Date().getTime() + '.png',
            width: 600, // Larger default for better visibility
            height: 400, // Maintain aspect ratio
            position: questionText.length
        };
        
        // Add to inline images and insert placeholder immediately
        setQuestionInlineImages(prev => [...prev, newImage]);
        setUploadedImages(prev => [...prev, newImage]);
        
        // Insert image placeholder immediately
        const imagePlaceholder = `\n[IMAGE:${newImage.id}:${newImage.width}x${newImage.height}px]\n`;
        setQuestionText(prev => prev + imagePlaceholder);
        
        setShowDrawingTool(false);
        alert('✅ Drawing inserted!');
    };

    // ====== ANSWER DRAWING FUNCTIONS ======
    
    // Initialize answer canvas
    useEffect(() => {
        if (showAnswerDrawingTool && answerCanvasRef.current) {
            const canvas = answerCanvasRef.current;
            const ctx = canvas.getContext('2d');
            
            // Set canvas size
            const scale = 2;
            const displayWidth = 794;
            const displayHeight = 1123;
            
            canvas.width = displayWidth * scale;
            canvas.height = displayHeight * scale;
            canvas.style.width = displayWidth + 'px';
            canvas.style.height = displayHeight + 'px';
            
            ctx.scale(scale, scale);
            ctx.fillStyle = 'white';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            if (showAnswerGraphPaper) {
                drawGraphPaper(ctx, displayWidth, displayHeight);
            }
        }
    }, [showAnswerDrawingTool, showAnswerGraphPaper]);
    
    const startAnswerDrawing = (e) => {
        setIsAnswerDrawing(true);
        const canvas = answerCanvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        setStartPos({ x, y });
        
        const ctx = canvas.getContext('2d');
        ctx.strokeStyle = answerDrawingColor;
        ctx.lineWidth = answerDrawingWidth;
        ctx.lineCap = 'round';
        
        if (answerDrawingTool === 'pen' || answerDrawingTool === 'eraser') {
            ctx.beginPath();
            ctx.moveTo(x, y);
        }
    };
    
    const drawAnswer = (e) => {
        if (!isAnswerDrawing) return;
        
        const canvas = answerCanvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const ctx = canvas.getContext('2d');
        
        if (answerDrawingTool === 'pen') {
            ctx.strokeStyle = answerDrawingColor;
            ctx.lineWidth = answerDrawingWidth;
            ctx.lineTo(x, y);
            ctx.stroke();
        } else if (answerDrawingTool === 'eraser') {
            ctx.globalCompositeOperation = 'destination-out';
            ctx.lineWidth = answerDrawingWidth * 2;
            ctx.lineTo(x, y);
            ctx.stroke();
            ctx.globalCompositeOperation = 'source-over';
        }
    };
    
    const stopAnswerDrawing = (e) => {
        if (!isAnswerDrawing) return;
        setIsAnswerDrawing(false);
        
        if (answerDrawingTool === 'line' || answerDrawingTool === 'rectangle' || answerDrawingTool === 'circle') {
            const canvas = answerCanvasRef.current;
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const ctx = canvas.getContext('2d');
            
            ctx.strokeStyle = answerDrawingColor;
            ctx.lineWidth = answerDrawingWidth;
            ctx.lineCap = 'round';
            
            if (answerDrawingTool === 'line') {
                ctx.beginPath();
                ctx.moveTo(startPos.x, startPos.y);
                ctx.lineTo(x, y);
                ctx.stroke();
            } else if (answerDrawingTool === 'rectangle') {
                ctx.beginPath();
                const width = x - startPos.x;
                const height = y - startPos.y;
                ctx.strokeRect(startPos.x, startPos.y, width, height);
            } else if (answerDrawingTool === 'circle') {
                ctx.beginPath();
                const radiusX = Math.abs(x - startPos.x) / 2;
                const radiusY = Math.abs(y - startPos.y) / 2;
                const centerX = startPos.x + (x - startPos.x) / 2;
                const centerY = startPos.y + (y - startPos.y) / 2;
                ctx.ellipse(centerX, centerY, radiusX, radiusY, 0, 0, 2 * Math.PI);
                ctx.stroke();
            }
        }
    };
    
    const clearAnswerCanvas = () => {
        const canvas = answerCanvasRef.current;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        if (showAnswerGraphPaper) {
            drawGraphPaper(ctx, canvas.width, canvas.height);
        }
    };
    
    const saveAnswerDrawing = () => {
        const canvas = answerCanvasRef.current;
        const imageUrl = canvas.toDataURL('image/png', 1.0);
        const newImage = {
            id: Date.now(),
            url: imageUrl,
            name: 'Answer_Drawing_' + new Date().getTime() + '.png',
            width: 600,
            height: 400,
            position: answerText.length
        };
        
        // Add to inline images and insert placeholder immediately
        setAnswerInlineImages(prev => [...prev, newImage]);
        setUploadedAnswerImages(prev => [...prev, newImage]);
        
        // Insert image placeholder immediately
        const imagePlaceholder = `\n[IMAGE:${newImage.id}:${newImage.width}x${newImage.height}px]\n`;
        setAnswerText(prev => prev + imagePlaceholder);
        
        setShowAnswerDrawingTool(false);
        alert('Answer drawing inserted!');
    };
    
    const handleAnswerFileUpload = (e) => {
        const files = Array.from(e.target.files);
        files.forEach(file => {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    const newImage = {
                        id: Date.now() + Math.random(),
                        url: event.target.result,
                        name: file.name,
                        width: 300,
                        height: 200,
                        position: answerText.length
                    };
                    
                    // Add to both inline images and uploaded images
                    setAnswerInlineImages(prev => [...prev, newImage]);
                    setUploadedAnswerImages(prev => [...prev, newImage]);
                    
                    // Auto-insert the image directly into content
                    setTimeout(() => {
                        insertInlineImageDirect(newImage, 'answer');
                    }, 100);
                };
                reader.readAsDataURL(file);
            }
        });
    };

    const removeAnswerImage = (imageId) => {
        setUploadedAnswerImages(prev => prev.filter(img => img.id !== imageId));
        removeInlineImage(imageId, 'answer');
    };

    const insertInlineImage = (imageId, targetType = 'question') => {
        const images = targetType === 'question' ? questionInlineImages : answerInlineImages;
        const setImages = targetType === 'question' ? setQuestionInlineImages : setAnswerInlineImages;
        const setText = targetType === 'question' ? setQuestionText : setAnswerText;
        const text = targetType === 'question' ? questionText : answerText;
        
        const image = images.find(img => img.id === imageId);
        if (!image) {
            alert('Image not found!');
            return;
        }
        
        // Insert image placeholder at end of content
        const imagePlaceholder = `\n[IMAGE:${image.id}:${image.width}x${image.height}px]\n`;
        setText(prev => prev + imagePlaceholder);
        
        // Update image position
        setImages(prev => prev.map(img => 
            img.id === imageId ? { ...img, position: text.length } : img
        ));
        
        alert('Image inserted!');
    };

    // Insert image directly with image object (for when state hasn't updated yet)
    const insertInlineImageDirect = (image, targetType = 'question') => {
        const setImages = targetType === 'question' ? setQuestionInlineImages : setAnswerInlineImages;
        const setText = targetType === 'question' ? setQuestionText : setAnswerText;
        const text = targetType === 'question' ? questionText : answerText;
        
        if (!image) {
            alert('Image not found!');
            return;
        }
        
        // Insert image placeholder at end of content
        const imagePlaceholder = `\n[IMAGE:${image.id}:${image.width}x${image.height}px]\n`;
        setText(prev => prev + imagePlaceholder);
        
        // Update image position in state
        setImages(prev => prev.map(img => 
            img.id === image.id ? { ...img, position: text.length } : img
        ));
        
        alert('Image inserted!');
    };



    const removeInlineImage = (imageId, targetType = 'question') => {
        const setImages = targetType === 'question' ? setQuestionInlineImages : setAnswerInlineImages;
        const setText = targetType === 'question' ? setQuestionText : setAnswerText;
        const text = targetType === 'question' ? questionText : answerText;
        
        setImages(prev => prev.filter(img => img.id !== imageId));
        
        // Remove placeholder from text - support both old and new format
        const regexOld = new RegExp(`\\[IMAGE:${imageId}:\\d+px\\]`, 'g');
        const regexNew = new RegExp(`\\[IMAGE:${imageId}:\\d+x\\d+px\\]`, 'g');
        setText(text.replace(regexOld, '').replace(regexNew, ''));
    };

    const updateImageDimensions = (imageId, newWidth, newHeight, targetType = 'question') => {
        const setImages = targetType === 'question' ? setQuestionInlineImages : setAnswerInlineImages;
        const setText = targetType === 'question' ? setQuestionText : setAnswerText;
        const text = targetType === 'question' ? questionText : answerText;
        const images = targetType === 'question' ? questionInlineImages : answerInlineImages;
        
        const image = images.find(img => img.id === imageId);
        if (!image) return;
        
        // Use new values if provided, otherwise keep existing
        const finalWidth = newWidth !== undefined ? newWidth : image.width;
        const finalHeight = newHeight !== undefined ? newHeight : image.height;
        
        setImages(prev => prev.map(img => 
            img.id === imageId ? { ...img, width: finalWidth, height: finalHeight } : img
        ));
        
        // Update placeholder in text - support both old and new formats
        const oldRegexOld = new RegExp(`\\[IMAGE:${imageId}:\\d+px\\]`, 'g');
        const oldRegexNew = new RegExp(`\\[IMAGE:${imageId}:\\d+x\\d+px\\]`, 'g');
        const newPlaceholder = `[IMAGE:${imageId}:${finalWidth}x${finalHeight}px]`;
        let updatedText = text.replace(oldRegexOld, newPlaceholder);
        updatedText = updatedText.replace(oldRegexNew, newPlaceholder);
        setText(updatedText);
    };

    const updateImageWidth = (imageId, newWidth, targetType = 'question') => {
        updateImageDimensions(imageId, newWidth, undefined, targetType);
    };

    const updateImageHeight = (imageId, newHeight, targetType = 'question') => {
        updateImageDimensions(imageId, undefined, newHeight, targetType);
    };

    // Drag and drop handlers for textareas
    const handleTextareaDragOver = (e) => {
        e.preventDefault();
        e.stopPropagation();
    };

    const handleQuestionDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        // Get dropped files
        const files = Array.from(e.dataTransfer.files);
        
        files.forEach(file => {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    const newImage = {
                        id: Date.now() + Math.random(),
                        url: event.target.result,
                        name: file.name,
                        width: 300,
                        height: 200,
                        position: questionText.length
                    };
                    
                    setQuestionInlineImages(prev => [...prev, newImage]);
                    setUploadedImages(prev => [...prev, newImage]);
                    
                    // Auto-insert the image at cursor position
                    setTimeout(() => {
                        insertInlineImage(newImage.id, 'question');
                    }, 100);
                };
                reader.readAsDataURL(file);
            } else {
                alert('Please drop only image files (.jpg, .png, .gif, etc.)');
            }
        });
    };

    const handleAnswerDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        // Get dropped files
        const files = Array.from(e.dataTransfer.files);
        
        files.forEach(file => {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    const newImage = {
                        id: Date.now() + Math.random(),
                        url: event.target.result,
                        name: file.name,
                        width: 300,
                        height: 200,
                        position: answerText.length
                    };
                    
                    setAnswerInlineImages(prev => [...prev, newImage]);
                    setUploadedAnswerImages(prev => [...prev, newImage]);
                    
                    // Auto-insert the image at cursor position
                    setTimeout(() => {
                        insertInlineImage(newImage.id, 'answer');
                    }, 100);
                };
                reader.readAsDataURL(file);
            } else {
                alert('Please drop only image files (.jpg, .png, .gif, etc.)');
            }
        });
    };

    // Voice transcription handlers
    const toggleQuestionVoiceRecording = () => {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert('Voice recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
            return;
        }

        if (isQuestionListening) {
            // Stop recording
            if (questionRecognitionRef.current) {
                questionRecognitionRef.current.stop();
            }
            setIsQuestionListening(false);
        } else {
            // Start recording
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US'; // Change to your preferred language
            
            recognition.onstart = () => {
                setIsQuestionListening(true);
            };
            
            recognition.onresult = (event) => {
                let interimTranscript = '';
                let finalTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript + ' ';
                    } else {
                        interimTranscript += transcript;
                    }
                }
                
                if (finalTranscript) {
                    setQuestionText(prev => prev + finalTranscript);
                }
            };
            
            recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                setIsQuestionListening(false);
                if (event.error !== 'no-speech') {
                    alert('Voice recognition error: ' + event.error);
                }
            };
            
            recognition.onend = () => {
                setIsQuestionListening(false);
            };
            
            questionRecognitionRef.current = recognition;
            recognition.start();
        }
    };

    const toggleAnswerVoiceRecording = () => {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert('Voice recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
            return;
        }

        if (isAnswerListening) {
            // Stop recording
            if (answerRecognitionRef.current) {
                answerRecognitionRef.current.stop();
            }
            setIsAnswerListening(false);
        } else {
            // Start recording
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US'; // Change to your preferred language
            
            recognition.onstart = () => {
                setIsAnswerListening(true);
            };
            
            recognition.onresult = (event) => {
                let interimTranscript = '';
                let finalTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript + ' ';
                    } else {
                        interimTranscript += transcript;
                    }
                }
                
                if (finalTranscript) {
                    setAnswerText(prev => prev + finalTranscript);
                }
            };
            
            recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                setIsAnswerListening(false);
                if (event.error !== 'no-speech') {
                    alert('Voice recognition error: ' + event.error);
                }
            };
            
            recognition.onend = () => {
                setIsAnswerListening(false);
            };
            
            answerRecognitionRef.current = recognition;
            recognition.start();
        }
    };

    // Cleanup speech recognition on unmount
    useEffect(() => {
        return () => {
            if (questionRecognitionRef.current) {
                questionRecognitionRef.current.stop();
            }
            if (answerRecognitionRef.current) {
                answerRecognitionRef.current.stop();
            }
        };
    }, []);

    // Text formatting functions
    const applyFormatting = (format, textareaRef, setText, section) => {
        const textarea = textareaRef.current;
        if (!textarea) return;

        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const selectedText = textarea.value.substring(start, end);

        if (!selectedText) {
            alert('Please select text to format');
            return;
        }

        let formattedText = '';
        let wrapper = '';

        switch (format) {
            case 'bold':
                wrapper = '**';
                formattedText = `**${selectedText}**`;
                break;
            case 'italic':
                wrapper = '*';
                formattedText = `*${selectedText}*`;
                break;
            case 'underline':
                wrapper = '__';
                formattedText = `__${selectedText}__`;
                break;
            case 'scientific':
                // Scientific names should be in italics
                wrapper = '*';
                formattedText = `*${selectedText}*`;
                break;
            default:
                return;
        }

        // Replace selected text with formatted version
        const newText = textarea.value.substring(0, start) + formattedText + textarea.value.substring(end);
        setText(newText);

        // Restore cursor position after the formatted text
        setTimeout(() => {
            textarea.focus();
            const newCursorPos = start + formattedText.length;
            textarea.setSelectionRange(newCursorPos, newCursorPos);
        }, 0);
    };

    const applyQuestionFormatting = (format) => {
        applyFormatting(format, questionTextareaRef, setQuestionText, 'question');
    };

    const applyAnswerFormatting = (format) => {
        applyFormatting(format, answerTextareaRef, setAnswerText, 'answer');
    };

    // Render formatted text for display
    const renderFormattedText = (text) => {
        if (!text) return null;

        // Split by markdown patterns while preserving image placeholders
        const parts = text.split(/(\*\*.*?\*\*|\*.*?\*|__.*?__|_.*?_|\[IMAGE:[\d.]+:(?:\d+x\d+|\d+)px\])/g);

        return parts.map((part, index) => {
            // Bold: **text**
            if (part.startsWith('**') && part.endsWith('**')) {
                const content = part.slice(2, -2);
                return <strong key={index}>{content}</strong>;
            }
            // Italic (including scientific names): *text*
            if (part.startsWith('*') && part.endsWith('*') && !part.startsWith('**')) {
                const content = part.slice(1, -1);
                return <em key={index}>{content}</em>;
            }
            // Underline: __text__
            if (part.startsWith('__') && part.endsWith('__')) {
                const content = part.slice(2, -2);
                return <u key={index}>{content}</u>;
            }
            // Single underscore italic: _text_
            if (part.startsWith('_') && part.endsWith('_') && !part.startsWith('__')) {
                const content = part.slice(1, -1);
                return <em key={index}>{content}</em>;
            }
            // Image placeholder - will be handled separately
            if (part.match(/\[IMAGE:[\d.]+:(?:\d+x\d+|\d+)px\]/)) {
                return part;
            }
            // Regular text
            return part;
        });
    };

    // Answer section handlers
    const scrollToSimilar = () => {
        const similarSection = document.getElementById('similar-questions-section');
        if (similarSection) {
            similarSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    };

    // Edit Questions functions
    const handleSearchQuestions = async (query = '') => {
        // Legacy wrapper — use react-query refetch which uses the debounced value and filters
        try {
            await refetchQuestions();
        } catch (e) {
            console.error('Error refetching questions via handleSearchQuestions wrapper', e);
        }
    };

    const handleSelectQuestion = useCallback((question) => {
        console.log('RAW question data received:', question);
        console.log('🔍 question_inline_images field:', question.question_inline_images);
        console.log('🔍 answer_inline_images field:', question.answer_inline_images);
        console.log('🔍 SECTION field:', question.section, 'section_name:', question.section_name);
        
        setSelectedQuestion(question);
        setEditQuestionText(question.question_text || '');
        setEditAnswerText(question.answer_text || '');
        setEditMarks(question.marks || '');
        setEditTopic(question.topic || ''); // Set the topic ID for editing
        setEditSection(question.section || ''); // Set the section ID for editing
        console.log('✅ Set editSection to:', question.section || '');
        setEditIsActive(question.is_active !== false); // Load active status
        setEditIsNested(question.is_nested === true); // Load nested status
        setEditIsEssayQuestion(question.is_essay_question === true); // Load essay status
        setEditIsGraphQuestion(question.is_graph_question === true); // Load graph status
        
        console.log('📋 Question Status Loaded for Editing:', {
            questionId: question.id,
            isActive: question.is_active !== false,
            isNested: question.is_nested === true,
            isEssayQuestion: question.is_essay_question === true,
            isGraphQuestion: question.is_graph_question === true,
            marks: question.marks,
            topic: question.topic_name || 'Unknown'
        });
        
        // Fetch topics for the selected paper
        console.log('🔄 About to fetch topics for paper:', question.paper);
        if (question.paper) {
            console.log('✅ Calling fetchTopicsForPaper with paper ID:', question.paper);
            fetchTopicsForPaper(question.paper);
        } else {
            console.warn('⚠️ No paper ID found in question:', question);
        }
        
        // Load inline images (if stored in database)
        const questionImages = question.question_inline_images || [];
        const answerImages = question.answer_inline_images || [];
        
        // Debug: Log image data to check structure
        console.log('📸 Loading question images:', {
            questionId: question.id,
            questionImages,
            answerImages,
            questionImagesCount: questionImages.length,
            answerImagesCount: answerImages.length,
            // Log first image structure if available
            firstQuestionImage: questionImages[0],
            firstAnswerImage: answerImages[0]
        });
        
        // Validate image structure
        if (questionImages.length > 0) {
            questionImages.forEach((img, idx) => {
                if (!img.url) {
                    console.error(`❌ Question image ${idx} is missing URL:`, img);
                } else if (!img.url.startsWith('data:')) {
                    console.warn(`⚠️ Question image ${idx} URL doesn't start with data::`, img.url.substring(0, 50));
                } else {
                    console.log(`✅ Question image ${idx} looks valid (${img.url.length} bytes)`);
                }
            });
        }
        
        // Check for IMAGE placeholders in text
        const questionText = question.question_text || '';
        const answerText = question.answer_text || '';
        const questionImageMatches = questionText.match(/\[IMAGE:([\d.]+):(?:\d+x\d+|\d+)px\]/g) || [];
        const answerImageMatches = answerText.match(/\[IMAGE:([\d.]+):(?:\d+x\d+|\d+)px\]/g) || [];
        
        if (questionImageMatches.length > 0 || answerImageMatches.length > 0) {
            console.log('📷 Image placeholders found:', {
                questionPlaceholders: questionImageMatches,
                answerPlaceholders: answerImageMatches,
                questionImagesInDB: questionImages.length,
                answerImagesInDB: answerImages.length
            });
            
            // Warn if placeholders exist but no images - DATA INTEGRITY ISSUE
            if (questionImageMatches.length > 0 && questionImages.length === 0) {
                console.error('❌ Question has IMAGE placeholders but no image data in database - DATA CORRUPTION!');
                alert('⚠️ Warning: This question has image placeholders but the actual images are missing from the database. The images were not saved properly when the question was created.');
            }
            if (answerImageMatches.length > 0 && answerImages.length === 0) {
                console.error('❌ Answer has IMAGE placeholders but no image data in database - DATA CORRUPTION!');
                alert('⚠️ Warning: This answer has image placeholders but the actual images are missing from the database. The images were not saved properly.');
            }
        }
        
        setEditQuestionInlineImages(questionImages);
        setEditAnswerInlineImages(answerImages);
        
        // NEW: Load image positions
        setEditQuestionImagePositions(question.question_image_positions || {});
        setEditAnswerImagePositions(question.answer_image_positions || {});
        
        // NEW: Load answer lines configurations
        const questionLines = question.question_answer_lines || [];
        const answerLines = question.answer_answer_lines || [];
        
        // Debug: Log if there are LINES placeholders but no configurations
        const questionHasLines = questionText.includes('[LINES:');
        const answerHasLines = answerText.includes('[LINES:');
        
        if ((questionHasLines && questionLines.length === 0) || (answerHasLines && answerLines.length === 0)) {
            console.warn('⚠️ Question has LINES placeholders but no configuration:', {
                questionId: question.id,
                questionHasLines,
                answerHasLines,
                questionLinesCount: questionLines.length,
                answerLinesCount: answerLines.length
            });
            
            // Auto-generate default line configurations for missing lines
            if (questionHasLines && questionLines.length === 0) {
                const matches = questionText.matchAll(/\[LINES:([\d.]+)\]/g);
                const defaultLines = [];
                for (const match of matches) {
                    const lineId = parseFloat(match[1]);
                    defaultLines.push({
                        id: lineId,
                        numberOfLines: 3, // Default to 3 lines
                        lineHeight: 30,   // Default height
                        lineStyle: 'solid',
                        opacity: 0.5
                    });
                }
                setEditQuestionAnswerLines(defaultLines);
                console.log('✅ Auto-generated question line configurations:', defaultLines);
            } else {
                setEditQuestionAnswerLines(questionLines);
            }
            
            if (answerHasLines && answerLines.length === 0) {
                const matches = answerText.matchAll(/\[LINES:([\d.]+)\]/g);
                const defaultLines = [];
                for (const match of matches) {
                    const lineId = parseFloat(match[1]);
                    defaultLines.push({
                        id: lineId,
                        numberOfLines: 3,
                        lineHeight: 30,
                        lineStyle: 'solid',
                        opacity: 0.5
                    });
                }
                setEditAnswerAnswerLines(defaultLines);
                console.log('✅ Auto-generated answer line configurations:', defaultLines);
            } else {
                setEditAnswerAnswerLines(answerLines);
            }
        } else {
            setEditQuestionAnswerLines(questionLines);
            setEditAnswerAnswerLines(answerLines);
        }
        
        // Note: Answer lines are embedded in the text as [LINES:id] placeholders
        // They will be rendered automatically when the text is displayed
    }, [fetchTopicsForPaper]);

    const handleUpdateQuestion = async (e) => {
        e.preventDefault();

        if (!selectedQuestion) {
            alert('No question selected');
            return;
        }

        if (!editQuestionText.trim()) {
            alert('Please enter the question text');
            return;
        }

        if (!editAnswerText.trim()) {
            alert('Please enter the answer text');
            return;
        }

        try {
            // Prepare section value - convert empty string to null
            const sectionValue = editSection && editSection.trim() !== '' ? editSection : (selectedQuestion.section || null);
            
            const updatedData = {
                subject: selectedQuestion.subject, // Include subject for validation
                paper: selectedQuestion.paper, // Include paper for validation
                section: sectionValue, // Use processed section value
                question_text: editQuestionText,
                answer_text: editAnswerText,
                marks: parseFloat(editMarks) || selectedQuestion.marks,
                topic: editTopic || selectedQuestion.topic, // Use editTopic if changed, otherwise keep current
                question_inline_images: editQuestionInlineImages, // Include images
                answer_inline_images: editAnswerInlineImages, // Include images
                question_image_positions: editQuestionImagePositions, // NEW: Image positions
                answer_image_positions: editAnswerImagePositions, // NEW: Image positions
                question_answer_lines: editQuestionAnswerLines, // NEW: Answer lines configurations
                answer_answer_lines: editAnswerAnswerLines, // NEW: Answer lines configurations
                difficulty: selectedQuestion.difficulty, // Include difficulty
                question_type: selectedQuestion.question_type, // Include question type
                is_active: editIsActive, // Use edited status
                is_nested: editIsNested, // Use edited type
                is_essay: editIsEssayQuestion, // Use edited essay status
                is_graph: editIsGraphQuestion // Use edited graph status
            };

            console.log('🔄 Updating question - Full details:');
            console.log('  - Question ID:', selectedQuestion.id);
            console.log('  - editSection state:', editSection);
            console.log('📋 Question Status Being Updated:', {
                isActive: editIsActive,
                isNested: editIsNested,
                isEssayQuestion: editIsEssayQuestion,
                isGraphQuestion: editIsGraphQuestion,
                marks: parseFloat(editMarks),
                topic: editTopic
            });
            console.log('  - selectedQuestion.section:', selectedQuestion.section);
            console.log('  - Computed sectionValue:', sectionValue);
            console.log('  - Full updatedData:', JSON.stringify(updatedData, null, 2));

            console.log('information sent to update')
            console.log(updatedData);
            
            const result = await questionService.updateQuestion(selectedQuestion.id, updatedData);
            console.log('✅ Update result:', result);
            
            alert('Question updated successfully!');
            
            // Refresh search results and get updated question data
            await refetchQuestions();
            
            // Fetch the updated question to refresh the form with latest data
            try {
                const updatedQuestion = await questionService.getQuestionById(selectedQuestion.id);
                console.log('📥 Fetched updated question:', updatedQuestion);
                
                // Update the selected question with fresh data
                if (updatedQuestion) {
                    setSelectedQuestion(updatedQuestion);
                    setEditSection(updatedQuestion.section || '');
                    console.log('✅ Refreshed form with updated section:', updatedQuestion.section);
                }
            } catch (fetchError) {
                console.error('Error fetching updated question:', fetchError);
            }
            
            // Don't clear the form - keep it open with updated data
            // This allows user to verify the changes were saved correctly
            
        } catch (error) {
            console.error('Error updating question:', error);
            alert('Failed to update question: ' + (error.message || 'Unknown error'));
        }
    };

    const handleDeleteQuestion = async () => {
        if (!selectedQuestion) {
            alert('No question selected');
            return;
        }

        if (!window.confirm('Are you sure you want to delete this question? This action cannot be undone.')) {
            return;
        }

        try {
            console.log('🗑️ Deleting question:', selectedQuestion.id);
            await questionService.deleteQuestion(selectedQuestion.id);
            
            alert('Question deleted successfully!');
            
            // Clear selection first
            const deletedQuestionId = selectedQuestion.id;
            setSelectedQuestion(null);
            setEditQuestionText('');
            setEditAnswerText('');
            setEditMarks('');
            setEditTopic('');
            setEditSection('');
            setEditQuestionInlineImages([]);
            setEditAnswerInlineImages([]);
            setEditQuestionImagePositions({}); // NEW: Clear positions
            setEditAnswerImagePositions({}); // NEW: Clear positions
            setEditQuestionAnswerLines([]); // NEW: Clear answer lines
            setEditAnswerAnswerLines([]); // NEW: Clear answer lines
            setEditIsActive(true); // Reset to active
            setEditIsNested(false); // Reset to standalone
            setEditIsEssayQuestion(false); // Reset essay status
            setEditIsGraphQuestion(false); // Reset graph status
            
            // Refresh search results - this will re-fetch questions
            await refetchQuestions();
            
            console.log('✅ Question deleted and search results refreshed');
            
        } catch (error) {
            console.error('Error deleting question:', error);
            alert('Failed to delete question: ' + (error.message || 'Unknown error'));
        }
    };

    const applyEditQuestionFormatting = (format) => {
        applyFormatting(format, editQuestionTextareaRef, setEditQuestionText, 'editQuestion');
    };

    const applyEditAnswerFormatting = (format) => {
        applyFormatting(format, editAnswerTextareaRef, setEditAnswerText, 'editAnswer');
    };

    // Bulk entry functions
    const handleBulkTextPaste = (e) => {
        const pastedText = e.target.value;
        setBulkText(pastedText);
    };

    const handleBulkFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        try {
            let extractedText = '';

            // Handle different file types
            if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
                // Plain text file
                extractedText = await new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = (event) => resolve(event.target.result);
                    reader.onerror = reject;
                    reader.readAsText(file);
                });
            } 
            else if (file.name.endsWith('.docx') || file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
                // Word document (.docx)
                const arrayBuffer = await file.arrayBuffer();
                const result = await mammoth.extractRawText({ arrayBuffer });
                extractedText = result.value;
                
                if (result.messages.length > 0) {
                    console.log('Mammoth warnings:', result.messages);
                }
            }
            else if (file.name.endsWith('.pdf') || file.type === 'application/pdf') {
                // PDF document
                const arrayBuffer = await file.arrayBuffer();
                const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
                
                let fullText = '';
                for (let i = 1; i <= pdf.numPages; i++) {
                    const page = await pdf.getPage(i);
                    const textContent = await page.getTextContent();
                    const pageText = textContent.items.map(item => item.str).join(' ');
                    fullText += pageText + '\n\n';
                }
                extractedText = fullText;
            }
            else {
                alert('⚠️ Unsupported file type!\n\nSupported formats:\n• Text files (.txt)\n• Word documents (.docx)\n• PDF documents (.pdf)');
                e.target.value = '';
                return;
            }

            if (!extractedText.trim()) {
                alert('❌ No text content found in the file. Please check the file and try again.');
                e.target.value = '';
                return;
            }

            setBulkText(extractedText);
            const questionCount = extractedText.split('\n\n').filter(s => s.trim()).length;
            alert(`✅ File "${file.name}" loaded successfully!\n\n📊 ${questionCount} potential questions found.\n\nClick "Process Bulk Questions" to continue.`);
            
        } catch (error) {
            console.error('Error reading file:', error);
            alert('❌ Error reading file: ' + error.message + '\n\nPlease try again or paste the text directly.');
        }
        
        e.target.value = ''; // Reset file input for re-upload
    };

    const processBulkText = () => {
        if (!bulkText.trim()) {
            alert('Please paste some text or upload a file first');
            return;
        }
        // Split by double newlines to separate questions
        const sections = bulkText.split('\n\n').filter(s => s.trim());
        setBulkQuestions(sections);
        setCurrentBulkIndex(0);
        if (sections.length > 0) {
            setQuestionText(sections[0]);
        }
        alert(`Found ${sections.length} potential questions. Review and save each one.`);
    };

    const refreshBulkQueue = () => {
        if (!bulkText.trim()) {
            alert('No text to refresh. Please paste or upload content first.');
            return;
        }
        // Recalculate questions from current text
        const sections = bulkText.split('\n\n').filter(s => s.trim());
        setBulkQuestions(sections);
        setCurrentBulkIndex(0);
        if (sections.length > 0) {
            setQuestionText(sections[0]);
        }
        alert(`✅ Queue refreshed!\n\n📊 Found ${sections.length} questions in the text area.`);
    };

    const clearBulkEntry = () => {
        if (bulkText.trim() || bulkQuestions.length > 0) {
            const confirmed = window.confirm('⚠️ Are you sure you want to clear all bulk entry data?\n\nThis will:\n• Clear the text area\n• Reset the question queue\n• Clear any unsaved content');
            if (confirmed) {
                setBulkText('');
                setBulkQuestions([]);
                setCurrentBulkIndex(0);
                setQuestionText('');
                setAnswerText('');
                alert('✅ Bulk entry cleared successfully!');
            }
        } else {
            alert('Nothing to clear.');
        }
    };

    const loadNextBulkQuestion = () => {
        if (currentBulkIndex < bulkQuestions.length - 1) {
            const nextIndex = currentBulkIndex + 1;
            setCurrentBulkIndex(nextIndex);
            setQuestionText(bulkQuestions[nextIndex]);
            setAnswerText('');
        } else {
            alert('All bulk questions processed!');
            setBulkQuestions([]);
            setCurrentBulkIndex(0);
            setBulkText('');
            setShowBulkEntry(false);
        }
    };

    const handleBulkSubmit = (e) => {
        e.preventDefault();
        handleSubmit(e);
        // Auto-load next question after successful submit
        setTimeout(() => {
            loadNextBulkQuestion();
        }, 500);
    };

    // Statistics calculations
    const getStatistics = () => {
        // Start with all questions
        let questions = Array.isArray(allQuestions) ? allQuestions : [];
        
        // Apply filters to questions
        if (filterSubject) {
            questions = questions.filter(q => q.subject_name === filterSubject);
        }
        if (filterPaper) {
            questions = questions.filter(q => q.paper_name === filterPaper);
        }
        if (filterTopic) {
            questions = questions.filter(q => q.topic_name === filterTopic);
        }
        if (filterStatus === 'active') {
            questions = questions.filter(q => q.is_active !== false);
        } else if (filterStatus === 'inactive') {
            questions = questions.filter(q => q.is_active === false);
        }
        
        const stats = {
            totalQuestions: questions.length,
            activeQuestions: questions.filter(q => q.is_active !== false).length,
            inactiveQuestions: questions.filter(q => q.is_active === false).length,
            unknownTopics: questions.filter(q => !q.topic_name || q.topic_name === 'Unknown').length,
            bySubject: {},
            byPaper: {},
            byTopic: {}
        };
        
        questions.forEach(q => {
            // By subject - use subject_name from API response
            const subjectName = q.subject_name || q.subject?.name || 'Unknown';
            if (!stats.bySubject[subjectName]) {
                stats.bySubject[subjectName] = { total: 0, active: 0, inactive: 0 };
            }
            stats.bySubject[subjectName].total += 1;
            if (q.is_active !== false) {
                stats.bySubject[subjectName].active += 1;
            } else {
                stats.bySubject[subjectName].inactive += 1;
            }
            
            // By paper - use paper_name from API response
            const paperName = q.paper_name || q.paper?.name || 'Unknown';
            const paperKey = `${subjectName} - ${paperName}`;
            if (!stats.byPaper[paperKey]) {
                stats.byPaper[paperKey] = { total: 0, active: 0, inactive: 0, subject: subjectName, paper: paperName };
            }
            stats.byPaper[paperKey].total += 1;
            if (q.is_active !== false) {
                stats.byPaper[paperKey].active += 1;
            } else {
                stats.byPaper[paperKey].inactive += 1;
            }
            
            // By topic - use topic_name from API response
            const topicName = q.topic_name || q.topic?.name || 'Unknown';
            if (!stats.byTopic[topicName]) {
                stats.byTopic[topicName] = { total: 0, active: 0, inactive: 0, byMarks: {} };
            }
            stats.byTopic[topicName].total += 1;
            if (q.is_active !== false) {
                stats.byTopic[topicName].active += 1;
            } else {
                stats.byTopic[topicName].inactive += 1;
            }
            
            // Track questions by marks
            const marks = q.marks || 0;
            if (!stats.byTopic[topicName].byMarks[marks]) {
                stats.byTopic[topicName].byMarks[marks] = 0;
            }
            stats.byTopic[topicName].byMarks[marks] += 1;
        });

        return stats;
    };

    const getFilteredQuestions = () => {
        // Questions are already filtered by the backend based on filters
        // Ensure we always return an array
        return Array.isArray(savedQuestions) ? savedQuestions : [];
    };

    // New Subject Management Functions
    const addPaper = () => {
        setNewSubjectPapers([...newSubjectPapers, { name: '', topics: [''], sections: [''] }]);
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

    // Fetch existing subjects from database
    const fetchSubjects = async () => {
        setIsLoadingSubjects(true);
        try {
            const subjects = await subjectService.getAllSubjects();
            setExistingSubjects(subjects);
        } catch (error) {
            console.error('Error fetching subjects:', error);
            // Display the actual error message from backend
            alert(error.message || 'Failed to load subjects. Please try again.');
        } finally {
            setIsLoadingSubjects(false);
        }
    };

    // Load subjects when component mounts or when activeTab changes to 'subjects'
    useEffect(() => {
        if (activeTab === 'subjects') {
            fetchSubjects();
            
            // Set up periodic refresh every 30 seconds
            const refreshInterval = setInterval(() => {
                fetchSubjects();
            }, 30000); // 30 seconds
            
            // Clean up interval when tab changes or component unmounts
            return () => clearInterval(refreshInterval);
        }
    }, [activeTab]);

    // Trigger search when paper filter changes
    useEffect(() => {
        if (editFilterSubject && editFilterPaper && editAvailablePapers.length > 0) {
            const paper = editAvailablePapers.find(p => p.name === editFilterPaper);
            if (paper) {
                setEditAvailableTopics(paper.topics || []);
                setEditFilterTopic('');
            }
        } else {
            setEditAvailableTopics([]);
        }
        
        // Trigger search when filters change (use react-query refetch)
        refetchQuestions();
    }, [editFilterPaper, editAvailablePapers, editFilterSubject]);

    // Trigger search when other filters change
    useEffect(() => {
        refetchQuestions();
    }, [editFilterSubject, editFilterPaper, editFilterTopic, editFilterStatus, editFilterType]);

    // Load all questions when Edit tab becomes active
    useEffect(() => {
        if (activeTab === 'edit') {
            refetchQuestions();
            fetchSubjects();
        }
    }, [activeTab]);


    

    const handleSubmitNewSubject = async (e) => {
        e.preventDefault();
        
        // Validate inputs
        if (!newSubjectName.trim()) {
            alert('Please enter a subject name');
            return;
        }

        // Validate that at least one paper has a name
        const validPapers = newSubjectPapers.filter(p => p.name.trim() !== '');
        if (validPapers.length === 0) {
            alert('Please add at least one paper');
            return;
        }
        
        const subjectData = {
            name: newSubjectName.trim(),
            papers: validPapers.map(paper => ({
                name: paper.name.trim(),
                topics: paper.topics.filter(t => t.trim() !== ''),
                sections: paper.sections.filter(s => s.trim() !== '').length > 0 
                    ? paper.sections.filter(s => s.trim() !== '')
                    : []
            }))
        };

        try {
            const result = await subjectService.createSubject(subjectData);
            
            // Update existing subjects list directly to avoid flickering
            setExistingSubjects(prevSubjects => [...prevSubjects, result]);
            
            alert(`Subject "${newSubjectName}" added successfully!`);
            
            // Reset form
            setNewSubjectName('');
            setNewSubjectPapers([{ name: '', topics: [''], sections: [''] }]);
            
            // Silent background refresh to ensure consistency (no UI disruption)
            setTimeout(() => {
                fetchSubjects();
                loadDynamicSubjects();
            }, 500);
        } catch (error) {
            console.error('Error creating subject:', error);
            // Display the actual error message from backend
            alert(error.message || 'Failed to add subject. Please try again.');
        }
    };

    // Toggle subject expansion
    const toggleSubjectExpansion = (subjectId) => {
        setExpandedSubjects(prev => ({
            ...prev,
            [subjectId]: !prev[subjectId]
        }));
    };

    // Toggle paper expansion
    const togglePaperExpansion = (paperId) => {
        setExpandedPapers(prev => ({
            ...prev,
            [paperId]: !prev[paperId]
        }));
    };

    // Edit handlers
    const handleEditSubject = (subject, fullEdit = false) => {
        if (fullEdit) {
            // Full edit mode - allows adding/removing papers, topics, sections
            const papers = subject.papers && Array.isArray(subject.papers) && subject.papers.length > 0 
                ? subject.papers.map(paper => ({
                    id: paper.id, // PRESERVE paper ID
                    name: paper.name || '',
                    // Topics can be objects {id, name} or strings - preserve both
                    topics: Array.isArray(paper.topics) && paper.topics.length > 0 
                        ? paper.topics.map(t => {
                            if (typeof t === 'object' && t !== null) {
                                return { id: t.id, name: t.name || '' }; // Preserve object structure
                            }
                            return { name: typeof t === 'string' ? t : '' }; // Convert strings to objects
                        })
                        : [{ name: '' }],
                    // Sections can be objects {id, name} or strings - preserve both
                    sections: Array.isArray(paper.sections) && paper.sections.length > 0 
                        ? paper.sections.map(s => {
                            if (typeof s === 'object' && s !== null) {
                                return { id: s.id, name: s.name || '' }; // Preserve object structure
                            }
                            return { name: typeof s === 'string' ? s : '' }; // Convert strings to objects
                        })
                        : [] // Sections can be empty
                }))
                : [{ name: '', topics: [{ name: '' }], sections: [] }];
                
            setEditSubjectData({
                id: subject.id,
                name: subject.name || '',
                papers: papers,
                originalPaperCount: papers.length // Track how many papers existed originally
            });
            setSelectedPaperIndices([]); // Start with no papers selected for editing
            setShowFullEditModal(true);
        } else {
            // Simple name edit mode
            setEditingItem({ type: 'subject', data: subject });
            setShowEditModal(true);
        }
    };

    const handleEditPaper = (subject, paper) => {
        setEditingItem({ type: 'paper', data: { subject, paper } });
        setShowEditModal(true);
    };

    const handleEditTopic = (subject, paper, topic) => {
        setEditingItem({ type: 'topic', data: { subject, paper, topic } });
        setShowEditModal(true);
    };

    const handleEditSection = (subject, paper, section) => {
        setEditingItem({ type: 'section', data: { subject, paper, section } });
        setShowEditModal(true);
    };

    // Save edit handler
    const handleSaveEdit = async () => {
        if (!editingItem) return;

        try {
            switch (editingItem.type) {
                case 'subject':
                    await subjectService.updateSubject(editingItem.data.id, {
                        name: editingItem.data.name
                    });
                    // Update state directly to avoid flickering
                    setExistingSubjects(prevSubjects =>
                        prevSubjects.map(subject =>
                            subject.id === editingItem.data.id
                                ? { ...subject, name: editingItem.data.name }
                                : subject
                        )
                    );
                    break;
                    
                case 'paper':
                    await subjectService.updatePaper(
                        editingItem.data.subject.id,
                        editingItem.data.paper.id,
                        { name: editingItem.data.paper.name }
                    );
                    // Update state directly
                    setExistingSubjects(prevSubjects =>
                        prevSubjects.map(subject =>
                            subject.id === editingItem.data.subject.id
                                ? {
                                    ...subject,
                                    papers: subject.papers.map(paper =>
                                        paper.id === editingItem.data.paper.id
                                            ? { ...paper, name: editingItem.data.paper.name }
                                            : paper
                                    )
                                }
                                : subject
                        )
                    );
                    break;
                    
                case 'topic':
                    await subjectService.updateTopic(editingItem.data.topic.id, {
                        name: editingItem.data.topic.name
                    });
                    // Update state directly
                    setExistingSubjects(prevSubjects =>
                        prevSubjects.map(subject => ({
                            ...subject,
                            papers: subject.papers.map(paper => ({
                                ...paper,
                                topics: paper.topics.map(topic =>
                                    topic.id === editingItem.data.topic.id
                                        ? { ...topic, name: editingItem.data.topic.name }
                                        : topic
                                )
                            }))
                        }))
                    );
                    break;
                    
                case 'section':
                    await subjectService.updateSection(editingItem.data.section.id, {
                        name: editingItem.data.section.name
                    });
                    // Update state directly
                    setExistingSubjects(prevSubjects =>
                        prevSubjects.map(subject => ({
                            ...subject,
                            papers: subject.papers.map(paper => ({
                                ...paper,
                                sections: paper.sections.map(section =>
                                    section.id === editingItem.data.section.id
                                        ? { ...section, name: editingItem.data.section.name }
                                        : section
                                )
                            }))
                        }))
                    );
                    break;
                    
                default:
                    break;
            }

            alert(`${editingItem.type.charAt(0).toUpperCase() + editingItem.type.slice(1)} updated successfully!`);
            setShowEditModal(false);
            setEditingItem(null);
            
            // Silent background refresh for consistency (no UI disruption)
            setTimeout(() => {
                fetchSubjects();
                loadDynamicSubjects();
            }, 500);
        } catch (error) {
            console.error('Error updating:', error);
            alert(error.message || `Failed to update ${editingItem.type}. Please try again.`);
        }
    };

    // Delete handlers
    const handleDeleteSubject = (subject) => {
        setDeletingItem({ type: 'subject', data: subject });
        setShowDeleteConfirm(true);
    };

    // Full subject edit handlers
    const handleEditSubjectNameChange = (value) => {
        setEditSubjectData(prev => ({ ...prev, name: value }));
    };

    const handleAddEditPaper = () => {
        setEditSubjectData(prev => ({
            ...prev,
            papers: [...prev.papers, { name: '', topics: [{ name: '' }], sections: [] }]
        }));
        // Auto-select the new paper for editing
        setSelectedPaperIndices(prev => [...prev, editSubjectData.papers.length]);
    };

    const handleRemoveEditPaper = (paperIndex) => {
        setEditSubjectData(prev => ({
            ...prev,
            papers: prev.papers.filter((_, index) => index !== paperIndex)
        }));
        // Remove from selected indices and adjust remaining indices
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
            topics: Array.isArray(paper.topics) ? paper.topics.filter(t => t && t.trim()) : [],
            sections: Array.isArray(paper.sections) ? paper.sections.filter(s => s && s.trim()) : []
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

    const handleAddEditTopic = (paperIndex) => {
        setEditSubjectData(prev => ({
            ...prev,
            papers: prev.papers.map((paper, index) => 
                index === paperIndex 
                    ? { ...paper, topics: [...paper.topics, { name: '' }] } // Add as object
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
                                ? { ...topic, name: value } // Update name property in object
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
                    ? { ...paper, sections: [...paper.sections, { name: '' }] } // Add as object
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
                                ? { ...section, name: value } // Update name property in object
                                : section
                        )
                    }
                    : paper
            )
        }));
    };

    const handleSaveFullEdit = async () => {
        if (!editSubjectData) return;

        // Validation
        if (!editSubjectData.name.trim()) {
            alert('Subject name cannot be empty');
            return;
        }

        const originalPaperCount = editSubjectData.originalPaperCount || 0;
        
        try {
            // Build the update payload - preserve existing papers and add new ones
            const allPapers = editSubjectData.papers.map((paper, index) => {
                const isExistingPaper = index < originalPaperCount && paper.id;
                
                // Clean up topics - remove empty ones and deduplicate
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
                
                // Clean up sections - remove empty ones and deduplicate
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
                    sections: Array.from(sectionsMap.values())
                };
                
                // Include ID for existing papers to preserve them
                if (isExistingPaper) {
                    paperData.id = paper.id;
                }

                return paperData;
            });

            // Filter to only valid papers with name and at least one topic
            const validPapers = allPapers.filter(paper => {
                const hasName = paper.name.trim();
                const hasTopics = paper.topics.length > 0;
                return hasName && hasTopics;
            });

            if (validPapers.length === 0) {
                alert('Please add at least one paper with a name and at least one topic');
                return;
            }

            // Send update request with ALL papers (existing + new)
            await subjectService.updateSubject(editSubjectData.id, {
                name: editSubjectData.name.trim(),
                papers: validPapers  // Backend will merge/update based on IDs
            });

            const newPapersCount = validPapers.filter(p => !p.id).length;
            const updatedPapersCount = validPapers.filter(p => p.id).length;
            
            let message = 'Subject updated successfully!\n';
            if (updatedPapersCount > 0) {
                message += `• Preserved ${updatedPapersCount} existing paper${updatedPapersCount > 1 ? 's' : ''}\n`;
            }
            if (newPapersCount > 0) {
                message += `• Added ${newPapersCount} new paper${newPapersCount > 1 ? 's' : ''}`;
            }
            
            alert(message);
            
            setShowFullEditModal(false);
            setEditSubjectData(null);
            setSelectedPaperIndices([]);
            
            // Refresh data to reflect changes
            setTimeout(() => {
                fetchSubjects();
                loadDynamicSubjects();
            }, 300);
        } catch (error) {
            console.error('Error updating subject:', error);
            alert(error.message || 'Failed to update subject. Please try again.');
        }
    };

    const handleCancelFullEdit = () => {
        setShowFullEditModal(false);
        setEditSubjectData(null);
        setSelectedPaperIndices([]);
    };

    const handleDeletePaper = (subject, paper) => {
        setDeletingItem({ type: 'paper', data: { subject, paper } });
        setShowDeleteConfirm(true);
    };

    const handleDeleteTopic = (subject, paper, topic) => {
        setDeletingItem({ type: 'topic', data: { subject, paper, topic } });
        setShowDeleteConfirm(true);
    };

    const handleDeleteSection = (subject, paper, section) => {
        setDeletingItem({ type: 'section', data: { subject, paper, section } });
        setShowDeleteConfirm(true);
    };

    // Confirm delete handler
    const handleConfirmDelete = async () => {
        if (!deletingItem) return;

        try {
            switch (deletingItem.type) {
                case 'subject':
                    await subjectService.deleteSubject(deletingItem.data.id);
                    // Update state directly to avoid flickering
                    setExistingSubjects(prevSubjects => prevSubjects.filter(s => s.id !== deletingItem.data.id));
                    break;
                    
                case 'paper':
                    await subjectService.deletePaper(
                        deletingItem.data.subject.id,
                        deletingItem.data.paper.id
                    );
                    // Update state directly
                    setExistingSubjects(prevSubjects =>
                        prevSubjects.map(subject =>
                            subject.id === deletingItem.data.subject.id
                                ? { ...subject, papers: subject.papers.filter(p => p.id !== deletingItem.data.paper.id) }
                                : subject
                        )
                    );
                    break;
                    
                case 'topic':
                    await subjectService.deleteTopic(deletingItem.data.topic.id);
                    // Update state directly
                    setExistingSubjects(prevSubjects =>
                        prevSubjects.map(subject => ({
                            ...subject,
                            papers: subject.papers.map(paper => ({
                                ...paper,
                                topics: paper.topics.filter(t => t.id !== deletingItem.data.topic.id)
                            }))
                        }))
                    );
                    break;
                    
                case 'section':
                    await subjectService.deleteSection(deletingItem.data.section.id);
                    // Update state directly
                    setExistingSubjects(prevSubjects =>
                        prevSubjects.map(subject => ({
                            ...subject,
                            papers: subject.papers.map(paper => ({
                                ...paper,
                                sections: paper.sections.filter(s => s.id !== deletingItem.data.section.id)
                            }))
                        }))
                    );
                    break;
                    
                default:
                    break;
            }

            alert(`${deletingItem.type.charAt(0).toUpperCase() + deletingItem.type.slice(1)} deleted successfully!`);
            setShowDeleteConfirm(false);
            setDeletingItem(null);
            
            // Silent background refresh for consistency (no UI disruption)
            setTimeout(() => {
                fetchSubjects();
                loadDynamicSubjects();
            }, 500);
        } catch (error) {
            console.error('Error deleting:', error);
            alert(error.message || `Failed to delete ${deletingItem.type}. Please try again.`);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100">
            {/* Header */}
            <header className="bg-white shadow-md">
                <div className="max-w-8xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <img src="/exam.png" alt="Exam Logo" className="w-12 h-12 object-contain" />
                            <h1 className="text-2xl font-bold text-green-600">Editor Dashboard</h1>
                        </div>
                        <button 
                            onClick={() => {
                                authService.logout();
                                onLogout();
                            }}
                            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition"
                        >
                            Logout
                        </button>
                    </div>
                </div>
            </header>

            {/* Navigation Tabs */}
            <div className="max-w-8xl mx-auto px-4 pt-6 sm:px-6 lg:px-8">
                <div className="bg-white rounded-lg shadow-md p-1 flex space-x-1">
                    <button
                        onClick={() => setActiveTab('questions')}
                        className={`flex-1 py-3 px-6 rounded-lg font-semibold transition duration-200 ${
                            activeTab === 'questions'
                                ? 'bg-green-600 text-white shadow-md'
                                : 'bg-white text-gray-600 hover:bg-gray-50'
                        }`}
                    >
                        <div className="flex items-center justify-center space-x-2">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            <span>Add Questions</span>
                        </div>
                    </button>
                    <button
                        onClick={() => setActiveTab('stats')}
                        className={`flex-1 py-3 px-6 rounded-lg font-semibold transition duration-200 ${
                            activeTab === 'stats'
                                ? 'bg-green-600 text-white shadow-md'
                                : 'bg-white text-gray-600 hover:bg-gray-50'
                        }`}
                    >
                        <div className="flex items-center justify-center space-x-2">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                            </svg>
                            <span>Statistics</span>
                        </div>
                    </button>
                    <button
                        onClick={() => setActiveTab('subjects')}
                        className={`flex-1 py-3 px-6 rounded-lg font-semibold transition duration-200 ${
                            activeTab === 'subjects'
                                ? 'bg-green-600 text-white shadow-md'
                                : 'bg-white text-gray-600 hover:bg-gray-50'
                        }`}
                    >
                        <div className="flex items-center justify-center space-x-2">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                            </svg>
                            <span>Add New Subject</span>
                        </div>
                    </button>
                    <button
                        onClick={() => setActiveTab('edit')}
                        className={`flex-1 py-3 px-6 rounded-lg font-semibold transition duration-200 ${
                            activeTab === 'edit'
                                ? 'bg-green-600 text-white shadow-md'
                                : 'bg-white text-gray-600 hover:bg-gray-50'
                        }`}
                    >
                        <div className="flex items-center justify-center space-x-2">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                            <span>Edit Questions</span>
                        </div>
                    </button>
                </div>
            </div>

            <div className="max-w-8xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
                {/* Add Questions Tab Content */}
                {activeTab === 'questions' && (
                    <>
                {/* Bulk Entry Toggle */}
                <div className="bg-blue-50 border-2 border-blue-200 rounded-xl shadow-lg p-4 mb-6">
                    <div className="flex justify-between items-center">
                        <div>
                            <h3 className="font-bold text-blue-800">📋 Bulk Entry Mode</h3>
                            <p className="text-sm text-blue-600">Paste multiple questions from Word/Document</p>
                        </div>
                        <button
                            onClick={() => setShowBulkEntry(!showBulkEntry)}
                            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-semibold transition"
                        >
                            {showBulkEntry ? 'Hide' : 'Show'} Bulk Entry
                        </button>
                    </div>
                    
                    {showBulkEntry && (
                        <div className="mt-4">
                            <div className="mb-4 bg-green-50 border border-green-200 rounded-lg p-3">
                                <p className="text-sm text-green-800 font-semibold mb-1">✅ Supported File Formats:</p>
                                <p className="text-xs text-green-700">📄 Text files (.txt) • 📘 Word documents (.docx) • 📕 PDF files (.pdf)</p>
                            </div>

                            <div className="mb-3">
                                <label className="block text-sm font-bold text-blue-700 mb-2">
                                    Option 1: Upload File (.txt, .docx, .pdf)
                                </label>
                                <div className="flex items-center space-x-3">
                                    <input
                                        type="file"
                                        accept=".txt,.docx,.pdf,text/plain,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/pdf"
                                        onChange={handleBulkFileUpload}
                                        className="hidden"
                                        id="bulkFileInput"
                                    />
                                    <label
                                        htmlFor="bulkFileInput"
                                        className="cursor-pointer bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-semibold transition inline-flex items-center space-x-2"
                                    >
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                        </svg>
                                        <span>Browse & Upload Document</span>
                                    </label>
                                    <span className="text-xs text-gray-600">All formats supported</span>
                                </div>
                            </div>

                            <div className="relative">
                                <div className="absolute inset-0 flex items-center">
                                    <div className="w-full border-t border-blue-300"></div>
                                </div>
                                <div className="relative flex justify-center text-sm">
                                    <span className="px-2 bg-blue-50 text-blue-600 font-semibold">OR</span>
                                </div>
                            </div>

                            <div className="mt-3">
                                <label className="block text-sm font-bold text-blue-700 mb-2">
                                    Option 2: Paste Text Directly
                                </label>
                                <textarea
                                    value={bulkText}
                                    onChange={handleBulkTextPaste}
                                    className="w-full px-4 py-3 border-2 border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                    rows="8"
                                    placeholder="Paste your questions here (separate each question with a blank line)...&#10;&#10;Example:&#10;Question 1 text here&#10;&#10;Question 2 text here&#10;&#10;Question 3 text here"
                                />
                            </div>

                            {/* Action Buttons */}
                            <div className="mt-3 flex flex-wrap gap-2">
                                <button
                                    onClick={processBulkText}
                                    disabled={!bulkText.trim()}
                                    className="flex-1 min-w-[200px] bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-semibold shadow-md transition disabled:bg-gray-400 disabled:cursor-not-allowed inline-flex items-center justify-center space-x-2"
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                                    </svg>
                                    <span>Process Bulk Questions ({bulkQuestions.length})</span>
                                </button>
                                
                                <button
                                    onClick={refreshBulkQueue}
                                    disabled={!bulkText.trim()}
                                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold shadow-md transition disabled:bg-gray-400 disabled:cursor-not-allowed inline-flex items-center space-x-2"
                                    title="Refresh the question queue based on current text"
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                    </svg>
                                    <span>Refresh Queue</span>
                                </button>
                                
                                <button
                                    onClick={clearBulkEntry}
                                    disabled={!bulkText.trim() && bulkQuestions.length === 0}
                                    className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg font-semibold shadow-md transition disabled:bg-gray-400 disabled:cursor-not-allowed inline-flex items-center space-x-2"
                                    title="Clear all bulk entry data"
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                    </svg>
                                    <span>Clear All</span>
                                </button>
                            </div>
                            
                            {bulkQuestions.length > 0 && (
                                <div className="mt-2 text-sm text-blue-700 font-semibold">
                                    📊 Processing question {currentBulkIndex + 1} of {bulkQuestions.length}
                                </div>
                            )}
                        </div>
                    )}
                </div>
                
                {/* Selection Section */}
                <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
                    <h2 className="text-xl font-bold text-gray-800 mb-4">Exam Organization</h2>
                    
                    {isLoadingDynamicSubjects ? (
                        <div className="flex items-center justify-center py-8">
                            <svg className="animate-spin h-8 w-8 text-green-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            <span className="ml-3 text-gray-600">Loading subjects...</span>
                        </div>
                    ) : Object.keys(subjects).length === 0 ? (
                        <div className="text-center py-8">
                            <p className="text-gray-600 mb-4">No subjects found. Please add subjects first.</p>
                            <button
                                onClick={() => setActiveTab('subjects')}
                                className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg font-semibold"
                            >
                                Go to Add Subject
                            </button>
                        </div>
                    ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {/* Subject Selection */}
                        <div>
                            <label className="block text-sm font-bold text-gray-700 mb-2">
                                Select Subject *
                            </label>
                            <select
                                value={selectedSubject}
                                onChange={(e) => handleSubjectChange(e.target.value)}
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                            >
                                <option value="">Choose Subject</option>
                                {Object.keys(subjects).map((subject) => (
                                    <option key={subject} value={subject}>{subject}</option>
                                ))}
                            </select>
                        </div>

                        {/* Paper Selection */}
                        <div>
                            <label className="block text-sm font-bold text-gray-700 mb-2">
                                Select Paper *
                            </label>
                            <select
                                value={selectedPaper}
                                onChange={(e) => handlePaperChange(e.target.value)}
                                disabled={!selectedSubject}
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition disabled:bg-gray-100"
                            >
                                <option value="">Choose Paper</option>
                                {selectedSubject && subjects[selectedSubject]?.papers.map((paper) => (
                                    <option key={paper} value={paper}>{paper}</option>
                                ))}
                            </select>
                        </div>

                        {/* Topic Selection */}
                        <div>
                            <label className="block text-sm font-bold text-gray-700 mb-2">
                                Select Topic (Optional)
                                {selectedPaper && subjects[selectedSubject]?.topics?.[selectedPaper] && (
                                    <span className="ml-1 text-xs font-normal text-gray-500">
                                        ({subjects[selectedSubject].topics[selectedPaper].length} available)
                                    </span>
                                )}
                            </label>
                            <select
                                value={selectedTopic}
                                onChange={(e) => handleTopicChange(e.target.value)}
                                disabled={!selectedPaper}
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition disabled:bg-gray-100"
                            >
                                <option value="">Choose Topic or leave as Unknown</option>
                                <option value="Unknown" className="font-bold text-orange-600">⚠️ Unknown Topic</option>
                                {selectedSubject && selectedPaper && subjects[selectedSubject]?.topics?.[selectedPaper]?.map((topic) => (
                                    <option key={topic} value={topic}>{topic}</option>
                                ))}
                            </select>
                            {selectedTopic === 'Unknown' && (
                                <p className="text-xs text-orange-600 mt-1">
                                    ⚠️ This question will be marked for topic classification later
                                </p>
                            )}
                            {selectedPaper && !selectedTopic && subjects[selectedSubject]?.topics?.[selectedPaper]?.length === 0 && (
                                <p className="text-xs text-gray-500 mt-1">
                                    ℹ️ No topics defined for this paper
                                </p>
                            )}
                        </div>

                        {/* Section Selection */}
                        <div>
                            <label className="block text-sm font-bold text-gray-700 mb-2">
                                Select Section {selectedPaper && subjects[selectedSubject]?.sections[selectedPaper]?.length > 0 && '*'}
                                {selectedPaper && subjects[selectedSubject]?.sections?.[selectedPaper] && (
                                    <span className="ml-1 text-xs font-normal text-gray-500">
                                        ({subjects[selectedSubject].sections[selectedPaper].length} available)
                                    </span>
                                )}
                            </label>
                            <select
                                value={selectedSection}
                                onChange={(e) => handleSectionChange(e.target.value)}
                                disabled={!selectedPaper || subjects[selectedSubject]?.sections[selectedPaper]?.length === 0}
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition disabled:bg-gray-100"
                            >
                                <option value="">
                                    {selectedPaper && subjects[selectedSubject]?.sections[selectedPaper]?.length === 0 
                                        ? 'No Sections' 
                                        : 'Choose Section'}
                                </option>
                                {selectedPaper && subjects[selectedSubject]?.sections[selectedPaper]?.map((section) => (
                                    <option key={section} value={section}>{section}</option>
                                ))}
                            </select>
                        </div>
                    </div>
                    )}

                    {/* Current Selection Display */}
                    {selectedSubject && !isLoadingDynamicSubjects && (
                        <div className="mt-4 p-4 bg-green-50 rounded-lg">
                            <p className="text-sm text-green-800">
                                <span className="font-bold">Current Selection:</span> {selectedSubject}
                                {selectedPaper && ` → ${selectedPaper}`}
                                {selectedTopic && ` → ${selectedTopic}`}
                                {selectedSection && ` → ${selectedSection}`}
                            </p>
                        </div>
                    )}
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
                    {/* Question Entry Section - 80% width on large screens */}
                    <div className="lg:col-span-4">
                        <form onSubmit={bulkQuestions.length > 0 ? handleBulkSubmit : handleSubmit} className="bg-white rounded-xl shadow-lg p-6">
                            <h2 className="text-xl font-bold text-gray-800 mb-4">
                                Question Entry {bulkQuestions.length > 0 && `(${currentBulkIndex + 1} of ${bulkQuestions.length})`}
                            </h2>
                            
                            {/* Question Content - Unified Rich Editor */}
                            <div className="mb-6">
                                <div className="flex items-center justify-between mb-2">
                                    <label className="block text-sm font-bold text-gray-700">
                                        Question Content *
                                    </label>
                                    
                                    {/* Inline Toolbar */}
                                    <div className="flex items-center gap-2">
                                        {/* Image Upload */}
                                        <label className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1.5 rounded-lg cursor-pointer transition text-xs flex items-center gap-1.5">
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                            </svg>
                                            <span>Image</span>
                                            <input type="file" accept="image/*" multiple onChange={handleFileUpload} className="hidden" />
                                        </label>

                                        {/* Drawing Tools */}
                                        <button
                                            type="button"
                                            onClick={() => setShowDrawingTool(!showDrawingTool)}
                                            className={`${showDrawingTool ? 'bg-purple-600' : 'bg-gray-500'} hover:bg-purple-700 text-white px-3 py-1.5 rounded-lg transition text-xs flex items-center gap-1.5`}
                                        >
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                                            </svg>
                                            <span>Draw</span>
                                        </button>

                                        {/* Graph Paper */}
                                        <button
                                            type="button"
                                            onClick={() => {
                                                setShowGraphPaper(!showGraphPaper);
                                                if (!showDrawingTool) setShowDrawingTool(true);
                                            }}
                                            className={`${showGraphPaper ? 'bg-green-600' : 'bg-gray-500'} hover:bg-green-700 text-white px-3 py-1.5 rounded-lg transition text-xs flex items-center gap-1.5`}
                                        >
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                            </svg>
                                            <span>Graph</span>
                                        </button>

                                        {/* Text Formatting Buttons */}
                                        <div className="flex items-center gap-1 border-l border-gray-300 pl-2">
                                            {/* Bold */}
                                            <button
                                                type="button"
                                                onClick={() => applyQuestionFormatting('bold')}
                                                className="bg-gray-600 hover:bg-gray-700 text-white px-2 py-1.5 rounded transition text-xs font-bold"
                                                title="Bold (Select text first)"
                                            >
                                                B
                                            </button>

                                            {/* Italic */}
                                            <button
                                                type="button"
                                                onClick={() => applyQuestionFormatting('italic')}
                                                className="bg-gray-600 hover:bg-gray-700 text-white px-2 py-1.5 rounded transition text-xs italic"
                                                title="Italic / Scientific Name (Select text first)"
                                            >
                                                I
                                            </button>

                                            {/* Underline */}
                                            <button
                                                type="button"
                                                onClick={() => applyQuestionFormatting('underline')}
                                                className="bg-gray-600 hover:bg-gray-700 text-white px-2 py-1.5 rounded transition text-xs underline"
                                                title="Underline (Select text first)"
                                            >
                                                U
                                            </button>
                                        </div>

                                        {/* Answer Lines Button */}
                                        <button
                                            type="button"
                                            onClick={() => {
                                                setAnswerLinesConfig(prev => ({ ...prev, targetSection: 'question' }));
                                                setShowAnswerLinesModal(true);
                                            }}
                                            className="bg-indigo-500 hover:bg-indigo-600 text-white px-3 py-1.5 rounded-lg transition text-xs flex items-center gap-1.5"
                                            title="Add answer lines for students"
                                        >
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                                            </svg>
                                            <span>Lines</span>
                                        </button>

                                        {/* Voice Recording */}
                                        <button
                                            type="button"
                                            onClick={toggleQuestionVoiceRecording}
                                            className={`${isQuestionListening ? 'bg-red-600 animate-pulse' : 'bg-orange-500'} hover:bg-orange-700 text-white px-3 py-1.5 rounded-lg transition text-xs flex items-center gap-1.5`}
                                            title={isQuestionListening ? "Stop voice recording" : "Start voice recording"}
                                        >
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                                            </svg>
                                            <span>{isQuestionListening ? 'Recording...' : 'Mic'}</span>
                                        </button>
                                    </div>
                                </div>

                                {/* Unified Content Editor with Inline Images */}
                                <div className="relative border-2 border-gray-300 rounded-lg bg-white overflow-hidden" style={{ height: '60vh' }}>
                                    {/* Scrollable Display Area showing rendered content with images */}
                                    <div 
                                        className="p-4 overflow-y-auto relative" 
                                        style={{ 
                                            height: '60%', // 60% for display, 40% for textarea
                                            whiteSpace: 'pre-wrap'
                                        }}
                                        onDragOver={(e) => {
                                            e.preventDefault();
                                            e.currentTarget.style.backgroundColor = '#f0f9ff';
                                        }}
                                        onDragLeave={(e) => {
                                            e.currentTarget.style.backgroundColor = 'white';
                                        }}
                                        onDrop={(e) => {
                                            e.preventDefault();
                                            e.currentTarget.style.backgroundColor = 'white';
                                            
                                            const imageId = parseFloat(e.dataTransfer.getData('imageId'));
                                            
                                            if (imageId) {
                                                // Get the container bounds
                                                const rect = e.currentTarget.getBoundingClientRect();
                                                const x = e.clientX - rect.left;
                                                const y = e.clientY - rect.top;
                                                
                                                // Update position for this image
                                                setQuestionImagePositions(prev => ({
                                                    ...prev,
                                                    [imageId]: { x, y }
                                                }));
                                            }
                                        }}
                                    >
                                        {questionText.split(/(\*\*.*?\*\*|\*.*?\*|__.*?__|_.*?_|\[IMAGE:[\d.]+:(?:\d+x\d+|\d+)px\]|\[LINES:[\d.]+\])/g).map((part, index) => {
                                            // Check for formatting first
                                            // Bold: **text**
                                            if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
                                                const content = part.slice(2, -2);
                                                return <strong key={index} data-text-index={index}>{content}</strong>;
                                            }
                                            // Italic (including scientific names): *text*
                                            if (part.startsWith('*') && part.endsWith('*') && !part.startsWith('**') && part.length > 2) {
                                                const content = part.slice(1, -1);
                                                return <em key={index} data-text-index={index} className="italic">{content}</em>;
                                            }
                                            // Underline: __text__
                                            if (part.startsWith('__') && part.endsWith('__') && part.length > 4) {
                                                const content = part.slice(2, -2);
                                                return <u key={index} data-text-index={index}>{content}</u>;
                                            }
                                            // Single underscore italic: _text_
                                            if (part.startsWith('_') && part.endsWith('_') && !part.startsWith('__') && part.length > 2) {
                                                const content = part.slice(1, -1);
                                                return <em key={index} data-text-index={index} className="italic">{content}</em>;
                                            }
                                            
                                            // Check for answer lines
                                            const linesMatch = part.match(/\[LINES:([\d.]+)\]/);
                                            if (linesMatch) {
                                                const lineId = parseFloat(linesMatch[1]);
                                                const lineConfig = questionAnswerLines.find(line => line.id === lineId);
                                                
                                                if (lineConfig) {
                                                    // A4 page width is approximately 210mm = 595px at 72 DPI, content area ~700px
                                                    const maxWidth = 700;
                                                    const fullLines = Math.floor(lineConfig.numberOfLines);
                                                    const hasHalfLine = lineConfig.numberOfLines % 1 !== 0;
                                                    
                                                    return (
                                                        <div key={index} className="my-2 relative group" style={{ maxWidth: `${maxWidth}px` }}>
                                                            {[...Array(fullLines)].map((_, idx) => (
                                                                <div
                                                                    key={idx}
                                                                    style={{
                                                                        height: `${lineConfig.lineHeight}px`,
                                                                        borderBottom: `2px ${lineConfig.lineStyle} rgba(0, 0, 0, ${lineConfig.opacity})`,
                                                                        width: '100%'
                                                                    }}
                                                                ></div>
                                                            ))}
                                                            {hasHalfLine && (
                                                                <div
                                                                    style={{
                                                                        height: `${lineConfig.lineHeight / 2}px`,
                                                                        borderBottom: `2px ${lineConfig.lineStyle} rgba(0, 0, 0, ${lineConfig.opacity})`,
                                                                        width: '100%'
                                                                    }}
                                                                ></div>
                                                            )}
                                                            {/* Remove lines button */}
                                                            <button
                                                                type="button"
                                                                onClick={() => {
                                                                    // Remove from array
                                                                    setQuestionAnswerLines(prev => prev.filter(line => line.id !== lineId));
                                                                    // Remove from text
                                                                    setQuestionText(prev => prev.replace(`[LINES:${lineId}]`, ''));
                                                                }}
                                                                className="absolute -top-2 -right-2 bg-red-500 hover:bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-lg text-xs font-bold z-10"
                                                                title="Remove lines"
                                                            >
                                                                ✕
                                                            </button>
                                                        </div>
                                                    );
                                                }
                                            }
                                            
                                            // Check for images
                                            const imageMatchNew = part.match(/\[IMAGE:([\d.]+):(\d+)x(\d+)px\]/);
                                            const imageMatchOld = part.match(/\[IMAGE:([\d.]+):(\d+)px\]/);
                                            
                                            if (imageMatchNew || imageMatchOld) {
                                                const imageId = parseFloat(imageMatchNew ? imageMatchNew[1] : imageMatchOld[1]);
                                                const imageWidth = parseInt(imageMatchNew ? imageMatchNew[2] : imageMatchOld[2]);
                                                const imageHeight = imageMatchNew ? parseInt(imageMatchNew[3]) : null;
                                                const image = questionInlineImages.find(img => Math.abs(img.id - imageId) < 0.001);
                                                const position = questionImagePositions[imageId];
                                                
                                                if (image) {
                                                    return (
                                                        <span 
                                                            key={index} 
                                                            className={position ? "absolute z-10" : "inline-block align-middle my-2 mx-1"}
                                                            style={position ? { left: `${position.x}px`, top: `${position.y}px` } : {}}
                                                            draggable={true}
                                                            onDragStart={(e) => {
                                                                e.dataTransfer.setData('imageId', imageId.toString());
                                                                e.dataTransfer.effectAllowed = 'move';
                                                            }}
                                                        >
                                                            <span className="relative inline-block group">
                                                                <img 
                                                                    src={image.url} 
                                                                    alt={image.name}
                                                                    style={{ 
                                                                        width: `${imageWidth}px`, 
                                                                        height: imageHeight ? `${imageHeight}px` : 'auto',
                                                                        maxWidth: '100%',
                                                                        display: 'block',
                                                                        cursor: 'move'
                                                                    }}
                                                                    className="border-2 border-blue-400 rounded shadow-sm select-none"
                                                                />
                                                                
                                                                {/* Remove button */}
                                                                <button
                                                                    type="button"
                                                                    onClick={() => removeImage(imageId)}
                                                                    className="absolute -top-2 -right-2 bg-red-500 hover:bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-lg text-xs font-bold z-10"
                                                                    title="Remove image"
                                                                >
                                                                    ✕
                                                                </button>
                                                                
                                                                {/* Position Reset Button - only show if positioned */}
                                                                {position && (
                                                                    <button
                                                                        type="button"
                                                                        onClick={() => {
                                                                            setQuestionImagePositions(prev => {
                                                                                const newPos = { ...prev };
                                                                                delete newPos[imageId];
                                                                                return newPos;
                                                                            });
                                                                        }}
                                                                        className="absolute -top-2 -left-2 bg-blue-500 hover:bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-lg text-xs font-bold z-10"
                                                                        title="Reset to inline position"
                                                                    >
                                                                        ↺
                                                                    </button>
                                                                )}
                                                                
                                                                {/* Resize controls - appear on hover */}
                                                                <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-70 text-white text-xs p-2 opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-2 z-10">
                                                                    <span className="text-[10px]">W:</span>
                                                                    <input
                                                                        type="number"
                                                                        value={imageWidth}
                                                                        onChange={(e) => {
                                                                            const newWidth = parseInt(e.target.value) || imageWidth;
                                                                            updateImageWidth(imageId, newWidth, 'question');
                                                                        }}
                                                                        onClick={(e) => e.stopPropagation()}
                                                                        className="w-14 px-1 py-0 text-black text-[10px] rounded"
                                                                        min="50"
                                                                        max="800"
                                                                    />
                                                                    <span className="text-[10px]">H:</span>
                                                                    <input
                                                                        type="number"
                                                                        value={imageHeight || 'auto'}
                                                                        onChange={(e) => {
                                                                            const newHeight = parseInt(e.target.value) || imageHeight;
                                                                            updateImageHeight(imageId, newHeight, 'question');
                                                                        }}
                                                                        onClick={(e) => e.stopPropagation()}
                                                                        className="w-14 px-1 py-0 text-black text-[10px] rounded"
                                                                        min="50"
                                                                        max="800"
                                                                    />
                                                                    <button
                                                                        type="button"
                                                                        onClick={(e) => {
                                                                            e.stopPropagation();
                                                                            updateImageDimensions(imageId, 300, 200, 'question');
                                                                        }}
                                                                        className="ml-auto bg-blue-500 hover:bg-blue-600 px-2 py-0.5 rounded text-[10px]"
                                                                        title="Reset to default size"
                                                                    >
                                                                        Reset
                                                                    </button>
                                                                </div>
                                                            </span>
                                                        </span>
                                                    );
                                                }
                                                return null;
                                            }
                                            return <span key={index} data-text-index={index}>{part}</span>;
                                        })}
                                        {questionText.length === 0 && (
                                            <span className="text-gray-400 pointer-events-none select-none">
                                                Start typing your question here... You can upload images, draw diagrams, or add graphs directly.
                                            </span>
                                        )}
                                    </div>
                                    
                                    {/* Fixed Editable textarea at bottom - 40% height */}
                                    <div className="absolute bottom-0 left-0 right-0 bg-white border-t-2 border-gray-300 shadow-lg" style={{ height: '40%' }}>
                                        <textarea
                                            ref={questionTextareaRef}
                                            value={questionText}
                                            onChange={(e) => setQuestionText(e.target.value)}
                                            onDragOver={handleTextareaDragOver}
                                            onDrop={handleQuestionDrop}
                                            className="w-full h-full px-4 py-3 focus:ring-2 focus:ring-green-500 focus:outline-none transition text-sm resize-none"
                                            placeholder="Type or edit your question text here..."
                                            style={{ fontFamily: 'monospace' }}
                                        />
                                    </div>
                                </div>
                                
                                {/* Hidden textarea for form validation */}
                                <textarea
                                    value={questionText}
                                    onChange={() => {}}
                                    className="sr-only"
                                    tabIndex={-1}
                                    required
                                    aria-hidden="true"
                                />
                            </div>

                            {/* Drawing Tool Panel - Appears inline when active */}
                            {showDrawingTool && (
                                <div className="mb-6 border-2 border-purple-300 rounded-lg p-4 bg-gradient-to-br from-purple-50 to-indigo-50">
                                    <div className="flex items-center justify-between mb-3">
                                        <h3 className="font-bold text-gray-800 flex items-center gap-2">
                                            <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                                            </svg>
                                            Drawing Tools
                                        </h3>
                                        <button
                                            type="button"
                                            onClick={() => setShowDrawingTool(false)}
                                            className="text-gray-500 hover:text-gray-700"
                                        >
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                            </svg>
                                        </button>
                                    </div>
                                    
                                    {/* Enhanced Drawing Controls */}
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                                        {/* Drawing Tool Selection */}
                                        <div>
                                            <label className="text-xs font-semibold text-gray-700 mb-1 block">Tool</label>
                                            <div className="flex gap-1">
                                                <button 
                                                    type="button" 
                                                    onClick={() => setDrawingTool('pen')} 
                                                    className={`flex-1 px-3 py-2 rounded text-sm font-medium transition ${drawingTool === 'pen' ? 'bg-purple-600 text-white shadow-lg' : 'bg-white text-gray-700 border border-gray-300'}`}
                                                    title="Freehand pen"
                                                >
                                                    ✏️ Pen
                                                </button>
                                                <button 
                                                    type="button" 
                                                    onClick={() => setDrawingTool('line')} 
                                                    className={`flex-1 px-3 py-2 rounded text-sm font-medium transition ${drawingTool === 'line' ? 'bg-purple-600 text-white shadow-lg' : 'bg-white text-gray-700 border border-gray-300'}`}
                                                    title="Straight line"
                                                >
                                                    📏 Line
                                                </button>
                                            </div>
                                        </div>

                                        {/* Shape Tools */}
                                        <div>
                                            <label className="text-xs font-semibold text-gray-700 mb-1 block">Shapes</label>
                                            <div className="flex gap-1">
                                                <button 
                                                    type="button" 
                                                    onClick={() => setDrawingTool('rectangle')} 
                                                    className={`flex-1 px-3 py-2 rounded text-sm font-medium transition ${drawingTool === 'rectangle' ? 'bg-purple-600 text-white shadow-lg' : 'bg-white text-gray-700 border border-gray-300'}`}
                                                    title="Rectangle"
                                                >
                                                    ▭
                                                </button>
                                                <button 
                                                    type="button" 
                                                    onClick={() => setDrawingTool('circle')} 
                                                    className={`flex-1 px-3 py-2 rounded text-sm font-medium transition ${drawingTool === 'circle' ? 'bg-purple-600 text-white shadow-lg' : 'bg-white text-gray-700 border border-gray-300'}`}
                                                    title="Circle"
                                                >
                                                    ⭕
                                                </button>
                                                <button 
                                                    type="button" 
                                                    onClick={() => setDrawingTool('eraser')} 
                                                    className={`flex-1 px-3 py-2 rounded text-sm font-medium transition ${drawingTool === 'eraser' ? 'bg-purple-600 text-white shadow-lg' : 'bg-white text-gray-700 border border-gray-300'}`}
                                                    title="Eraser"
                                                >
                                                    🧹
                                                </button>
                                            </div>
                                        </div>
                                        
                                        {/* Color Picker */}
                                        <div>
                                            <label className="text-xs font-semibold text-gray-700 mb-1 block">Color</label>
                                            <div className="flex gap-2 items-center">
                                                <input 
                                                    type="color" 
                                                    value={drawingColor} 
                                                    onChange={(e) => setDrawingColor(e.target.value)} 
                                                    className="w-12 h-9 rounded cursor-pointer border-2 border-gray-300"
                                                />
                                                <div className="flex-1">
                                                    <select 
                                                        value={drawingColor} 
                                                        onChange={(e) => setDrawingColor(e.target.value)}
                                                        className="w-full px-2 py-2 text-xs border border-gray-300 rounded"
                                                    >
                                                        <option value="#000000">Black</option>
                                                        <option value="#FF0000">Red</option>
                                                        <option value="#0000FF">Blue</option>
                                                        <option value="#008000">Green</option>
                                                        <option value="#FFA500">Orange</option>
                                                        <option value="#800080">Purple</option>
                                                    </select>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        {/* Line Width */}
                                        <div>
                                            <label className="text-xs font-semibold text-gray-700 mb-1 block">
                                                Width: {drawingWidth}px
                                            </label>
                                            <input 
                                                type="range" 
                                                min="1" 
                                                max="20" 
                                                value={drawingWidth} 
                                                onChange={(e) => setDrawingWidth(e.target.value)} 
                                                className="w-full h-9"
                                            />
                                        </div>
                                    </div>
                                    
                                    {/* Action Buttons */}
                                    <div className="flex gap-2 mb-3">
                                        <button 
                                            type="button" 
                                            onClick={clearCanvas} 
                                            className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg font-semibold transition text-sm flex items-center gap-2"
                                        >
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                            </svg>
                                            Clear Canvas
                                        </button>
                                        <button 
                                            type="button" 
                                            onClick={saveDrawing} 
                                            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-semibold transition text-sm flex items-center gap-2"
                                        >
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                            </svg>
                                            Save & Insert Drawing
                                        </button>
                                    </div>
                                    
                                    {/* Drawing Canvas */}
                                    <div className="relative bg-white rounded-lg border-2 border-gray-300 overflow-auto">
                                        <canvas
                                            ref={canvasRef}
                                            onMouseDown={startDrawing}
                                            onMouseMove={draw}
                                            onMouseUp={stopDrawing}
                                            onMouseLeave={stopDrawing}
                                            className="mx-auto cursor-crosshair"
                                            style={{ width: '794px', height: '600px', maxWidth: '100%' }}
                                        />
                                    </div>
                                </div>
                            )}

                            {/* Answer Content - Unified Rich Editor */}
                            <div className="mb-6">
                                <div className="flex items-center justify-between mb-2">
                                    <label className="block text-sm font-bold text-gray-700">
                                        Answer/Solution Content *
                                    </label>
                                    
                                    {/* Button to copy question to answer section */}
                                    <button
                                        type="button"
                                        onClick={() => {
                                            if (questionText && !answerText) {
                                                // Copy question text to answer if answer is empty
                                                setAnswerText(questionText);
                                                // Also copy question images to answer
                                                setAnswerInlineImages([...questionInlineImages]);
                                            } else if (questionText && answerText) {
                                                // If answer already has content, ask for confirmation
                                                if (window.confirm('Answer section already has content. Do you want to replace it with the question text?')) {
                                                    setAnswerText(questionText);
                                                    setAnswerInlineImages([...questionInlineImages]);
                                                }
                                            }
                                        }}
                                        disabled={!questionText}
                                        className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5 ${
                                            questionText 
                                                ? 'bg-blue-600 text-white hover:bg-blue-700' 
                                                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                        }`}
                                        title="Copy question text to answer section for inline editing"
                                    >
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                        </svg>
                                        Copy Question to Answer
                                    </button>
                                </div>

                                {/* Question Preview in Answer Section */}
                                {questionText && (
                                    <div className="mb-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
                                        <p className="text-xs font-bold text-blue-800 mb-2">📝 QUESTION PREVIEW:</p>
                                        <div className="text-sm text-gray-700 whitespace-pre-wrap">
                                            {questionText.split(/(\*\*.*?\*\*|\*.*?\*|__.*?__|_.*?_|\[IMAGE:[\d.]+:(?:\d+x\d+|\d+)px\])/g).map((part, index) => {
                                                // Check for formatting first
                                                // Bold: **text**
                                                if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
                                                    const content = part.slice(2, -2);
                                                    return <strong key={index}>{content}</strong>;
                                                }
                                                // Italic (including scientific names): *text*
                                                if (part.startsWith('*') && part.endsWith('*') && !part.startsWith('**') && part.length > 2) {
                                                    const content = part.slice(1, -1);
                                                    return <em key={index} className="italic">{content}</em>;
                                                }
                                                // Underline: __text__
                                                if (part.startsWith('__') && part.endsWith('__') && part.length > 4) {
                                                    const content = part.slice(2, -2);
                                                    return <u key={index}>{content}</u>;
                                                }
                                                // Single underscore italic: _text_
                                                if (part.startsWith('_') && part.endsWith('_') && !part.startsWith('__') && part.length > 2) {
                                                    const content = part.slice(1, -1);
                                                    return <em key={index} className="italic">{content}</em>;
                                                }
                                                
                                                // Check for images
                                                const imageMatchNew = part.match(/\[IMAGE:([\d.]+):(\d+)x(\d+)px\]/);
                                                const imageMatchOld = part.match(/\[IMAGE:([\d.]+):(\d+)px\]/);
                                                
                                                if (imageMatchNew || imageMatchOld) {
                                                    const imageId = parseFloat(imageMatchNew ? imageMatchNew[1] : imageMatchOld[1]);
                                                    const imageWidth = parseInt(imageMatchNew ? imageMatchNew[2] : imageMatchOld[2]);
                                                    const imageHeight = imageMatchNew ? parseInt(imageMatchNew[3]) : null;
                                                    const image = questionInlineImages.find(img => Math.abs(img.id - imageId) < 0.001);
                                                    
                                                    if (image) {
                                                        return (
                                                            <img 
                                                                key={index}
                                                                src={image.url} 
                                                                alt={image.name}
                                                                style={{ 
                                                                    width: `${imageWidth}px`, 
                                                                    height: imageHeight ? `${imageHeight}px` : 'auto',
                                                                    maxWidth: '100%',
                                                                    display: 'inline-block',
                                                                    verticalAlign: 'middle'
                                                                }}
                                                                className="border border-blue-300 rounded my-1 mx-0.5"
                                                            />
                                                        );
                                                    }
                                                }
                                                return <span key={index}>{part}</span>;
                                            })}
                                        </div>
                                    </div>
                                )}

                                {/* Unified Content Editor with Inline Images */}
                                <div className="relative border-2 border-gray-300 rounded-lg bg-white overflow-hidden" style={{ height: '60vh' }}>
                                    {/* Scrollable Display Area showing rendered content with images */}
                                    <div 
                                        className="p-4 overflow-y-auto relative" 
                                        style={{ 
                                            height: '60%', // 60% for display, 40% for textarea
                                            whiteSpace: 'pre-wrap'
                                        }}
                                        onDragOver={(e) => {
                                            e.preventDefault();
                                            e.currentTarget.style.backgroundColor = '#fff7ed';
                                        }}
                                        onDragLeave={(e) => {
                                            e.currentTarget.style.backgroundColor = 'white';
                                        }}
                                        onDrop={(e) => {
                                            e.preventDefault();
                                            e.currentTarget.style.backgroundColor = 'white';
                                            
                                            const imageId = parseFloat(e.dataTransfer.getData('imageId'));
                                            
                                            if (imageId) {
                                                // Get the container bounds
                                                const rect = e.currentTarget.getBoundingClientRect();
                                                const x = e.clientX - rect.left;
                                                const y = e.clientY - rect.top;
                                                
                                                // Update position for this image
                                                setAnswerImagePositions(prev => ({
                                                    ...prev,
                                                    [imageId]: { x, y }
                                                }));
                                            }
                                        }}
                                    >
                                        {answerText.split(/(\*\*.*?\*\*|\*.*?\*|__.*?__|_.*?_|\[IMAGE:[\d.]+:(?:\d+x\d+|\d+)px\]|\[LINES:[\d.]+\])/g).map((part, index) => {
                                            // Check for formatting first
                                            // Bold: **text**
                                            if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
                                                const content = part.slice(2, -2);
                                                return <strong key={index} data-text-index={index}>{content}</strong>;
                                            }
                                            // Italic (including scientific names): *text*
                                            if (part.startsWith('*') && part.endsWith('*') && !part.startsWith('**') && part.length > 2) {
                                                const content = part.slice(1, -1);
                                                return <em key={index} data-text-index={index} className="italic">{content}</em>;
                                            }
                                            // Underline: __text__
                                            if (part.startsWith('__') && part.endsWith('__') && part.length > 4) {
                                                const content = part.slice(2, -2);
                                                return <u key={index} data-text-index={index}>{content}</u>;
                                            }
                                            // Single underscore italic: _text_
                                            if (part.startsWith('_') && part.endsWith('_') && !part.startsWith('__') && part.length > 2) {
                                                const content = part.slice(1, -1);
                                                return <em key={index} data-text-index={index} className="italic">{content}</em>;
                                            }
                                            
                                            // Check for answer lines
                                            const linesMatch = part.match(/\[LINES:([\d.]+)\]/);
                                            if (linesMatch) {
                                                const lineId = parseFloat(linesMatch[1]);
                                                const lineConfig = answerAnswerLines.find(line => line.id === lineId);
                                                
                                                if (lineConfig) {
                                                    // A4 page width is approximately 210mm = 595px at 72 DPI, content area ~700px
                                                    const maxWidth = 700;
                                                    const fullLines = Math.floor(lineConfig.numberOfLines);
                                                    const hasHalfLine = lineConfig.numberOfLines % 1 !== 0;
                                                    
                                                    return (
                                                        <div key={index} className="my-2 relative group" style={{ maxWidth: `${maxWidth}px` }}>
                                                            {[...Array(fullLines)].map((_, idx) => (
                                                                <div
                                                                    key={idx}
                                                                    className="relative"
                                                                    style={{
                                                                        height: `${lineConfig.lineHeight}px`,
                                                                        borderBottom: `2px ${lineConfig.lineStyle} rgba(0, 0, 0, ${lineConfig.opacity})`,
                                                                        width: '100%'
                                                                    }}
                                                                >
                                                                    <input
                                                                        type="text"
                                                                        placeholder="Type your answer here..."
                                                                        className="absolute inset-0 w-full bg-transparent border-none outline-none px-1"
                                                                        style={{
                                                                            height: `${lineConfig.lineHeight}px`,
                                                                            lineHeight: `${lineConfig.lineHeight - 4}px`,
                                                                            fontSize: `${Math.min(lineConfig.lineHeight * 0.6, 16)}px`,
                                                                            paddingBottom: '2px'
                                                                        }}
                                                                    />
                                                                </div>
                                                            ))}
                                                            {hasHalfLine && (
                                                                <div
                                                                    className="relative"
                                                                    style={{
                                                                        height: `${lineConfig.lineHeight / 2}px`,
                                                                        borderBottom: `2px ${lineConfig.lineStyle} rgba(0, 0, 0, ${lineConfig.opacity})`,
                                                                        width: '100%'
                                                                    }}
                                                                >
                                                                    <input
                                                                        type="text"
                                                                        placeholder="Type here..."
                                                                        className="absolute inset-0 w-full bg-transparent border-none outline-none px-1"
                                                                        style={{
                                                                            height: `${lineConfig.lineHeight / 2}px`,
                                                                            lineHeight: `${(lineConfig.lineHeight / 2) - 4}px`,
                                                                            fontSize: `${Math.min((lineConfig.lineHeight / 2) * 0.6, 14)}px`,
                                                                            paddingBottom: '2px'
                                                                        }}
                                                                    />
                                                                </div>
                                                            )}
                                                            {/* Remove lines button */}
                                                            <button
                                                                type="button"
                                                                onClick={() => {
                                                                    // Remove from array
                                                                    setAnswerAnswerLines(prev => prev.filter(line => line.id !== lineId));
                                                                    // Remove from text
                                                                    setAnswerText(prev => prev.replace(`[LINES:${lineId}]`, ''));
                                                                }}
                                                                className="absolute -top-2 -right-2 bg-red-500 hover:bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-lg text-xs font-bold z-10"
                                                                title="Remove lines"
                                                            >
                                                                ✕
                                                            </button>
                                                        </div>
                                                    );
                                                }
                                            }
                                            
                                            // Check for images
                                            const imageMatchNew = part.match(/\[IMAGE:([\d.]+):(\d+)x(\d+)px\]/);
                                            const imageMatchOld = part.match(/\[IMAGE:([\d.]+):(\d+)px\]/);
                                            
                                            if (imageMatchNew || imageMatchOld) {
                                                const imageId = parseFloat(imageMatchNew ? imageMatchNew[1] : imageMatchOld[1]);
                                                const imageWidth = parseInt(imageMatchNew ? imageMatchNew[2] : imageMatchOld[2]);
                                                const imageHeight = imageMatchNew ? parseInt(imageMatchNew[3]) : null;
                                                const image = answerInlineImages.find(img => Math.abs(img.id - imageId) < 0.001);
                                                const position = answerImagePositions[imageId];
                                                
                                                if (image) {
                                                    return (
                                                        <span 
                                                            key={index} 
                                                            className={position ? "absolute z-10" : "inline-block align-middle my-2 mx-1"}
                                                            style={position ? { left: `${position.x}px`, top: `${position.y}px` } : {}}
                                                            draggable={true}
                                                            onDragStart={(e) => {
                                                                e.dataTransfer.setData('imageId', imageId.toString());
                                                                e.dataTransfer.effectAllowed = 'move';
                                                            }}
                                                        >
                                                            <span className="relative inline-block group">
                                                                <img 
                                                                    src={image.url} 
                                                                    alt={image.name}
                                                                    style={{ 
                                                                        width: `${imageWidth}px`, 
                                                                        height: imageHeight ? `${imageHeight}px` : 'auto',
                                                                        maxWidth: '100%',
                                                                        display: 'block',
                                                                        cursor: 'move'
                                                                    }}
                                                                    className="border-2 border-orange-400 rounded shadow-sm select-none"
                                                                />
                                                                
                                                                {/* Remove button */}
                                                                <button
                                                                    type="button"
                                                                    onClick={() => removeAnswerImage(imageId)}
                                                                    className="absolute -top-2 -right-2 bg-red-500 hover:bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-lg text-xs font-bold z-10"
                                                                    title="Remove image"
                                                                >
                                                                    ✕
                                                                </button>
                                                                
                                                                {/* Position Reset Button - only show if positioned */}
                                                                {position && (
                                                                    <button
                                                                        type="button"
                                                                        onClick={() => {
                                                                            setAnswerImagePositions(prev => {
                                                                                const newPos = { ...prev };
                                                                                delete newPos[imageId];
                                                                                return newPos;
                                                                            });
                                                                        }}
                                                                        className="absolute -top-2 -left-2 bg-blue-500 hover:bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-lg text-xs font-bold z-10"
                                                                        title="Reset to inline position"
                                                                    >
                                                                        ↺
                                                                    </button>
                                                                )}
                                                                
                                                                {/* Resize controls - appear on hover */}
                                                                <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-70 text-white text-xs p-2 opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-2 z-10">
                                                                    <span className="text-[10px]">W:</span>
                                                                    <input
                                                                        type="number"
                                                                        value={imageWidth}
                                                                        onChange={(e) => {
                                                                            const newWidth = parseInt(e.target.value) || imageWidth;
                                                                            updateImageWidth(imageId, newWidth, 'answer');
                                                                        }}
                                                                        onClick={(e) => e.stopPropagation()}
                                                                        className="w-14 px-1 py-0 text-black text-[10px] rounded"
                                                                        min="50"
                                                                        max="800"
                                                                    />
                                                                    <span className="text-[10px]">H:</span>
                                                                    <input
                                                                        type="number"
                                                                        value={imageHeight || 'auto'}
                                                                        onChange={(e) => {
                                                                            const newHeight = parseInt(e.target.value) || imageHeight;
                                                                            updateImageHeight(imageId, newHeight, 'answer');
                                                                        }}
                                                                        onClick={(e) => e.stopPropagation()}
                                                                        className="w-14 px-1 py-0 text-black text-[10px] rounded"
                                                                        min="50"
                                                                        max="800"
                                                                    />
                                                                    <button
                                                                        type="button"
                                                                        onClick={(e) => {
                                                                            e.stopPropagation();
                                                                            updateImageDimensions(imageId, 300, 200, 'answer');
                                                                        }}
                                                                        className="ml-auto bg-blue-500 hover:bg-blue-600 px-2 py-0.5 rounded text-[10px]"
                                                                        title="Reset to default size"
                                                                    >
                                                                        Reset
                                                                    </button>
                                                                </div>
                                                            </span>
                                                        </span>
                                                    );
                                                }
                                                return null;
                                            }
                                            return <span key={index} data-text-index={index}>{part}</span>;
                                        })}
                                        {answerText.length === 0 && (
                                            <span className="text-gray-400 pointer-events-none select-none">
                                                Start with "Solution:" or "Answer:" and type your solution here...
                                            </span>
                                        )}
                                    </div>
                                    
                                    {/* Fixed Editable textarea at bottom - 40% height */}
                                    <div className="absolute bottom-0 left-0 right-0 bg-white border-t-2 border-gray-300 shadow-lg" style={{ height: '40%' }}>
                                        <textarea
                                            ref={answerTextareaRef}
                                            value={answerText}
                                            onChange={(e) => setAnswerText(e.target.value)}
                                            className="w-full h-full px-4 py-3 focus:ring-2 focus:ring-orange-500 focus:outline-none transition text-sm resize-none"
                                            placeholder="Type or edit your answer text here..."
                                            style={{ fontFamily: 'monospace' }}
                                        />
                                    </div>
                                </div>
                                
                                {/* Image and Drawing Tools for Answer Section */}
                                <div className="mt-3 flex flex-wrap gap-2">
                                    {/* Upload Image Button */}
                                    <label className="cursor-pointer inline-flex items-center px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition shadow-md">
                                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                        </svg>
                                        Upload Image
                                        <input 
                                            type="file" 
                                            accept="image/*" 
                                            multiple 
                                            onChange={handleAnswerFileUpload} 
                                            className="hidden" 
                                        />
                                    </label>
                                    
                                    {/* Draw/Graph Button */}
                                    <button
                                        type="button"
                                        onClick={() => setShowAnswerDrawingTool(!showAnswerDrawingTool)}
                                        className={`inline-flex items-center px-4 py-2 rounded-lg transition shadow-md ${
                                            showAnswerDrawingTool 
                                                ? 'bg-orange-600 text-white' 
                                                : 'bg-orange-500 text-white hover:bg-orange-600'
                                        }`}
                                    >
                                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                                        </svg>
                                        {showAnswerDrawingTool ? 'Close Drawing Tool' : 'Draw/Add Graph'}
                                    </button>

                                    {/* Voice Recording Button */}
                                    <button
                                        type="button"
                                        onClick={toggleAnswerVoiceRecording}
                                        className={`inline-flex items-center px-4 py-2 rounded-lg transition shadow-md ${
                                            isAnswerListening 
                                                ? 'bg-red-600 text-white animate-pulse' 
                                                : 'bg-orange-500 text-white hover:bg-orange-600'
                                        }`}
                                        title={isAnswerListening ? "Stop voice recording" : "Start voice recording"}
                                    >
                                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                                        </svg>
                                        {isAnswerListening ? 'Recording...' : 'Voice Input'}
                                    </button>

                                    {/* Text Formatting Buttons */}
                                    <div className="flex items-center gap-1 border-l border-gray-300 pl-2">
                                        {/* Bold */}
                                        <button
                                            type="button"
                                            onClick={() => applyAnswerFormatting('bold')}
                                            className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-2 rounded transition font-bold"
                                            title="Bold (Select text first)"
                                        >
                                            B
                                        </button>

                                        {/* Italic */}
                                        <button
                                            type="button"
                                            onClick={() => applyAnswerFormatting('italic')}
                                            className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-2 rounded transition italic"
                                            title="Italic / Scientific Name (Select text first)"
                                        >
                                            I
                                        </button>

                                        {/* Underline */}
                                        <button
                                            type="button"
                                            onClick={() => applyAnswerFormatting('underline')}
                                            className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-2 rounded transition underline"
                                            title="Underline (Select text first)"
                                        >
                                            U
                                        </button>
                                    </div>

                                    {/* Answer Lines Button */}
                                    <button
                                        type="button"
                                        onClick={() => {
                                            setAnswerLinesConfig(prev => ({ ...prev, targetSection: 'answer' }));
                                            setShowAnswerLinesModal(true);
                                        }}
                                        className="bg-indigo-500 hover:bg-indigo-600 text-white px-3 py-2 rounded-lg transition text-sm flex items-center gap-1.5"
                                        title="Add answer lines for students"
                                    >
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                                        </svg>
                                        <span>Lines</span>
                                    </button>
                                </div>
                                
                                {/* Hidden textarea for form validation */}
                                <textarea
                                    value={answerText}
                                    onChange={() => {}}
                                    className="sr-only"
                                    tabIndex={-1}
                                    required
                                    aria-hidden="true"
                                />
                            </div>

                            {/* Answer Drawing Tool Panel - Appears inline when active */}
                            {showAnswerDrawingTool && (
                                <div className="mb-6 border-2 border-orange-400 rounded-lg p-4 bg-orange-50">
                                    <div className="flex items-center justify-between mb-3">
                                        <h3 className="text-lg font-bold text-orange-800">🎨 Answer Drawing Tool</h3>
                                        <button
                                            type="button"
                                            onClick={() => setShowAnswerDrawingTool(false)}
                                            className="text-orange-600 hover:text-orange-800 font-bold"
                                        >
                                            ✕ Close
                                        </button>
                                    </div>
                                    
                                    {/* Drawing Controls */}
                                    <div className="mb-3 flex flex-wrap gap-3 items-center bg-white p-3 rounded-lg border border-orange-200">
                                        {/* Tool Selection */}
                                        <div className="flex gap-2">
                                            <button
                                                type="button"
                                                onClick={() => setAnswerDrawingTool('pen')}
                                                className={`px-3 py-2 rounded ${answerDrawingTool === 'pen' ? 'bg-orange-500 text-white' : 'bg-gray-200 hover:bg-gray-300'}`}
                                                title="Pen Tool"
                                            >
                                                ✏️ Pen
                                            </button>
                                            <button
                                                type="button"
                                                onClick={() => setAnswerDrawingTool('eraser')}
                                                className={`px-3 py-2 rounded ${answerDrawingTool === 'eraser' ? 'bg-orange-500 text-white' : 'bg-gray-200 hover:bg-gray-300'}`}
                                                title="Eraser"
                                            >
                                                🧹 Eraser
                                            </button>
                                            <button
                                                type="button"
                                                onClick={() => setAnswerDrawingTool('line')}
                                                className={`px-3 py-2 rounded ${answerDrawingTool === 'line' ? 'bg-orange-500 text-white' : 'bg-gray-200 hover:bg-gray-300'}`}
                                                title="Line Tool"
                                            >
                                                📏 Line
                                            </button>
                                            <button
                                                type="button"
                                                onClick={() => setAnswerDrawingTool('rectangle')}
                                                className={`px-3 py-2 rounded ${answerDrawingTool === 'rectangle' ? 'bg-orange-500 text-white' : 'bg-gray-200 hover:bg-gray-300'}`}
                                                title="Rectangle Tool"
                                            >
                                                ▭ Rectangle
                                            </button>
                                            <button
                                                type="button"
                                                onClick={() => setAnswerDrawingTool('circle')}
                                                className={`px-3 py-2 rounded ${answerDrawingTool === 'circle' ? 'bg-orange-500 text-white' : 'bg-gray-200 hover:bg-gray-300'}`}
                                                title="Circle Tool"
                                            >
                                                ⭕ Circle
                                            </button>
                                        </div>
                                        
                                        {/* Color Picker */}
                                        <div className="flex items-center gap-2">
                                            <label className="text-sm font-medium">Color:</label>
                                            <input
                                                type="color"
                                                value={answerDrawingColor}
                                                onChange={(e) => setAnswerDrawingColor(e.target.value)}
                                                className="w-10 h-10 rounded cursor-pointer"
                                            />
                                            <div className="flex gap-1">
                                                {['#000000', '#ff0000', '#0000ff', '#00ff00', '#ff00ff', '#ffff00'].map(color => (
                                                    <button
                                                        key={color}
                                                        type="button"
                                                        onClick={() => setAnswerDrawingColor(color)}
                                                        className="w-6 h-6 rounded border-2 border-gray-300 hover:border-gray-500"
                                                        style={{ backgroundColor: color }}
                                                        title={color}
                                                    />
                                                ))}
                                            </div>
                                        </div>
                                        
                                        {/* Width Slider */}
                                        <div className="flex items-center gap-2">
                                            <label className="text-sm font-medium">Width:</label>
                                            <input
                                                type="range"
                                                min="1"
                                                max="20"
                                                value={answerDrawingWidth}
                                                onChange={(e) => setAnswerDrawingWidth(parseInt(e.target.value))}
                                                className="w-24"
                                            />
                                            <span className="text-sm font-bold w-8">{answerDrawingWidth}px</span>
                                        </div>
                                        
                                        {/* Graph Paper Toggle */}
                                        <label className="flex items-center gap-2 cursor-pointer">
                                            <input
                                                type="checkbox"
                                                checked={showAnswerGraphPaper}
                                                onChange={(e) => setShowAnswerGraphPaper(e.target.checked)}
                                                className="w-4 h-4"
                                            />
                                            <span className="text-sm font-medium">Graph Paper</span>
                                        </label>
                                        
                                        {/* Clear Canvas */}
                                        <button
                                            type="button"
                                            onClick={clearAnswerCanvas}
                                            className="px-3 py-2 bg-red-500 text-white rounded hover:bg-red-600"
                                        >
                                            🗑️ Clear
                                        </button>
                                    </div>
                                    
                                    {/* Canvas */}
                                    <div className="bg-white rounded-lg border-2 border-orange-300 overflow-hidden">
                                        <canvas
                                            ref={answerCanvasRef}
                                            onMouseDown={startAnswerDrawing}
                                            onMouseMove={drawAnswer}
                                            onMouseUp={stopAnswerDrawing}
                                            onMouseLeave={stopAnswerDrawing}
                                            className="cursor-crosshair block"
                                            style={{ width: '100%', maxWidth: '794px' }}
                                        />
                                    </div>
                                    
                                    {/* Save Button */}
                                    <div className="mt-3 flex justify-end">
                                        <button
                                            type="button"
                                            onClick={saveAnswerDrawing}
                                            className="px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 font-bold shadow-md"
                                        >
                                            💾 Save & Insert Drawing
                                        </button>
                                    </div>
                                </div>
                            )}

                            {/* Marks */}
                            <div className="mb-4">
                                <label className="block text-sm font-bold text-gray-700 mb-2">
                                    Marks *
                                </label>
                                <input
                                    type="number"
                                    value={marks}
                                    onChange={(e) => setMarks(e.target.value)}
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                    placeholder="Enter marks for this question"
                                    min="1"
                                    required
                                />
                            </div>

                            {/* Nested Question Checkbox */}
                            <div className="mb-4 border-2 rounded-lg p-4" style={{
                                borderColor: isNested ? '#8b5cf6' : '#d1d5db',
                                backgroundColor: isNested ? '#f3e8ff' : '#f9fafb'
                            }}>
                                <label className="flex items-center cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={isNested}
                                        onChange={(e) => setIsNested(e.target.checked)}
                                        className="w-5 h-5 text-purple-600 rounded focus:ring-2 focus:ring-purple-500"
                                    />
                                    <span className="ml-3 text-sm font-bold text-gray-700">
                                        This is a Nested Question
                                    </span>
                                </label>
                                <p className="text-xs mt-2 ml-8" style={{color: isNested ? '#6b21a8' : '#6b7280'}}>
                                    {isNested 
                                        ? '✓ Nested ' 
                                        : 'Standalone'}
                                </p>
                                {isNested && marks && parseInt(marks) > 0 && (
                                    <div className="mt-2 ml-8 text-xs text-purple-700 flex items-start">
                                        <svg className="w-4 h-4 mr-1 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                                        </svg>
                                        <span>
                                            Recommended marks for nested questions: 4-7 marks
                                            {parseInt(marks) < 4 && ' (Consider increasing marks or marking as standalone)'}
                                            {parseInt(marks) > 7 && ' (Consider reducing marks or splitting into separate questions)'}
                                        </span>
                                    </div>
                                )}
                            </div>

                            {/* Essay Question Checkbox */}
                            <div className="mb-4 border-2 rounded-lg p-4" style={{
                                borderColor: isEssayQuestion ? '#f59e0b' : '#d1d5db',
                                backgroundColor: isEssayQuestion ? '#fef3c7' : '#f9fafb'
                            }}>
                                <label className="flex items-center cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={isEssayQuestion}
                                        onChange={(e) => setIsEssayQuestion(e.target.checked)}
                                        className="w-5 h-5 text-yellow-600 rounded focus:ring-2 focus:ring-yellow-500"
                                    />
                                    <span className="ml-3 text-sm font-bold text-gray-700">
                                        This is an Essay Question
                                    </span>
                                </label>
                                <p className="text-xs mt-2 ml-8" style={{color: isEssayQuestion ? '#b45309' : '#6b7280'}}>
                                    {isEssayQuestion 
                                        ? '✓ Essay question - requires extended written response' 
                                        : 'Not an essay question'}
                                </p>
                            </div>

                            {/* Graph Question Checkbox */}
                            <div className="mb-4 border-2 rounded-lg p-4" style={{
                                borderColor: isGraphQuestion ? '#06b6d4' : '#d1d5db',
                                backgroundColor: isGraphQuestion ? '#cffafe' : '#f9fafb'
                            }}>
                                <label className="flex items-center cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={isGraphQuestion}
                                        onChange={(e) => setIsGraphQuestion(e.target.checked)}
                                        className="w-5 h-5 text-cyan-600 rounded focus:ring-2 focus:ring-cyan-500"
                                    />
                                    <span className="ml-3 text-sm font-bold text-gray-700">
                                        This is a Graph Question
                                    </span>
                                </label>
                                <p className="text-xs mt-2 ml-8" style={{color: isGraphQuestion ? '#0e7490' : '#6b7280'}}>
                                    {isGraphQuestion 
                                        ? '✓ Graph question - requires drawing/plotting graphs' 
                                        : 'Not a graph question'}
                                </p>
                            </div>

                            {/* Question Status */}
                            <div className="mb-6 border-2 rounded-lg p-4" style={{
                                borderColor: isQuestionActive ? '#10b981' : '#ef4444',
                                backgroundColor: isQuestionActive ? '#d1fae5' : '#fee2e2'
                            }}>
                                <label className="flex items-center cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={isQuestionActive}
                                        onChange={(e) => setIsQuestionActive(e.target.checked)}
                                        className="w-5 h-5 text-green-600 rounded focus:ring-2 focus:ring-green-500"
                                    />
                                    <span className="ml-3 text-sm font-bold text-gray-700">
                                        Question is Active
                                    </span>
                                </label>
                                <p className="text-xs mt-2 ml-8" style={{color: isQuestionActive ? '#065f46' : '#991b1b'}}>
                                    {isQuestionActive 
                                        ? '✓ Active - Question can be used in exams' 
                                        : '⚠️ Inactive - Question is disabled and won\'t appear in exams'}
                                </p>
                                {selectedTopic === 'Unknown' && (
                                    <div className="mt-2 ml-8 text-xs text-orange-600 flex items-start">
                                        <svg className="w-4 h-4 mr-1 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                        </svg>
                                        <span>Note: Topic needs to be classified later</span>
                                    </div>
                                )}
                            </div>

                            {/* Submit Button */}
                            <button
                                type="submit"
                                disabled={!selectedSubject || !selectedPaper}
                                className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 shadow-md hover:shadow-lg disabled:bg-gray-400 disabled:cursor-not-allowed"
                            >
                                {bulkQuestions.length > 0 ? `Save & Load Next (${currentBulkIndex + 1}/${bulkQuestions.length})` : isQuestionActive ? 'Submit Active Question' : 'Save Inactive Question'}
                            </button>
                        </form>
                    </div>

                    {/* Similar Questions Section */}
                    <div className="lg:col-span-1">
                        <div id="similar-questions-section" className="bg-white rounded-xl shadow-lg p-6 sticky top-4">
                            <h2 className="text-xl font-bold text-gray-800 mb-4">Similar Questions</h2>
                            
                            {isSearching && (
                                <div className="text-center py-8">
                                    <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-green-600 mx-auto"></div>
                                    <p className="text-sm text-gray-600 mt-2">Searching...</p>
                                </div>
                            )}

                            {!isSearching && questionText.length <= 10 && (
                                <div className="text-center py-8">
                                    <p className="text-sm text-gray-500">
                                        Start typing a question to see similar questions from the database
                                    </p>
                                </div>
                            )}

                            {!isSearching && similarQuestions.length === 0 && questionText.length > 10 && (
                                <div className="text-center py-8">
                                    <div className="text-green-600 mb-2">
                                        <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                        </svg>
                                    </div>
                                    <p className="text-sm text-green-600 font-semibold">
                                        No similar questions found!
                                    </p>
                                    <p className="text-xs text-gray-500 mt-1">
                                        This appears to be a unique question
                                    </p>
                                </div>
                            )}

                            {!isSearching && similarQuestions.length > 0 && (
                                <div className="space-y-3">
                                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
                                        <p className="text-xs font-bold text-yellow-800">
                                            ⚠️ WARNING: Similar questions detected!
                                        </p>
                                        <p className="text-xs text-yellow-700 mt-1">
                                            Found {similarQuestions.length} similar question{similarQuestions.length > 1 ? 's' : ''} in {selectedSubject}
                                        </p>
                                    </div>

                                    {similarQuestions.map((question, index) => (
                                        <div key={question.id || index} className="border border-gray-200 rounded-lg p-4 hover:border-green-500 transition hover:shadow-md bg-white">
                                            {/* Similarity Score */}
                                            <div className="flex justify-between items-center mb-3">
                                                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-bold bg-green-100 text-green-800">
                                                    <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                                    </svg>
                                                    {question.similarity_score ? `${Math.round(question.similarity_score)}% Match` : 'Similar'}
                                                </span>
                                                <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                                                    ID: {question.id}
                                                </span>
                                            </div>
                                            
                                            {/* Question Text */}
                                            <div className="text-sm text-gray-800 mb-3 leading-relaxed border-l-2 border-green-400 pl-3">
                                                {renderTextWithImages(
                                                    question.question_text || question.text,
                                                    question.question_inline_images || [],
                                                    question.question_image_positions || {},
                                                    question.question_answer_lines || [],
                                                    null,
                                                    null,
                                                    'similar'
                                                )}
                                            </div>
                                            
                                            {/* Question Metadata */}
                                            <div className="grid grid-cols-2 gap-2 pt-3 border-t border-gray-100">
                                                {/* Topic */}
                                                <div className="flex items-start">
                                                    <span className="text-xs font-semibold text-gray-500 mr-1">📚 Topic:</span>
                                                    <span className="text-xs text-gray-700">{question.topic || 'N/A'}</span>
                                                </div>
                                                
                                                {/* Paper */}
                                                <div className="flex items-start">
                                                    <span className="text-xs font-semibold text-gray-500 mr-1">📄 Paper:</span>
                                                    <span className="text-xs text-gray-700">{question.paper || 'N/A'}</span>
                                                </div>
                                                
                                                {/* Section */}
                                                <div className="flex items-start">
                                                    <span className="text-xs font-semibold text-gray-500 mr-1">📑 Section:</span>
                                                    <span className="text-xs text-gray-700">{question.section || 'N/A'}</span>
                                                </div>
                                                
                                                {/* Marks */}
                                                <div className="flex items-start">
                                                    <span className="text-xs font-semibold text-gray-500 mr-1">⭐ Marks:</span>
                                                    <span className="text-xs font-bold text-green-600">{question.marks || 0}</span>
                                                </div>
                                            </div>
                                            
                                            {/* Status Badge */}
                                            {question.status && (
                                                <div className="mt-2 pt-2 border-t border-gray-100">
                                                    <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                                                        question.status === 'Active' 
                                                            ? 'bg-green-100 text-green-800' 
                                                            : 'bg-red-100 text-red-800'
                                                    }`}>
                                                        {question.status === 'Active' ? '✓' : '✕'} {question.status}
                                                    </span>
                                                    {question.timestamp && (
                                                        <span className="text-xs text-gray-400 ml-2">
                                                            Added: {new Date(question.timestamp).toLocaleDateString()}
                                                        </span>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Floating Button for Mobile - Similar Questions Counter */}
                {questionText.length > 10 && (
                    <button
                        onClick={scrollToSimilar}
                        className="lg:hidden fixed bottom-6 right-6 bg-green-600 hover:bg-green-700 text-white rounded-full shadow-2xl p-4 flex items-center justify-center z-50 transition-all duration-300 hover:scale-110"
                    >
                        <div className="flex items-center space-x-2">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            <div className="flex flex-col items-start">
                                <span className="text-xs font-bold">Similar</span>
                                <div className="flex items-center">
                                    {isSearching ? (
                                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                    ) : (
                                        <span className="text-lg font-bold">
                                            {similarQuestions.length}
                                        </span>
                                    )}
                                </div>
                            </div>
                        </div>
                        {similarQuestions.length > 0 && (
                            <div className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold animate-pulse">
                                {similarQuestions.length}
                            </div>
                        )}
                    </button>
                )}
                    </>
                )}

                {/* Add New Subject Tab Content */}
                {activeTab === 'subjects' && (
                    <div className="space-y-8">
                        {/* Existing Subjects List */}
                        <div className="bg-white rounded-xl shadow-lg p-8 h-96 overflow-y-auto">
                            <div className="flex justify-between items-center mb-6">
                                <h2 className="text-2xl font-bold text-gray-800">Manage Subjects</h2>
                                <button
                                    onClick={fetchSubjects}
                                    className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition text-sm flex items-center space-x-2"
                                    disabled={isLoadingSubjects}
                                >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                    </svg>
                                    <span>Refresh</span>
                                </button>
                            </div>

                            {isLoadingSubjects ? (
                                <div className="flex justify-center items-center py-12">
                                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
                                </div>
                            ) : existingSubjects.length === 0 ? (
                                <div className="text-center py-12 text-gray-500">
                                    <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                    </svg>
                                    <p className="text-lg font-semibold">No subjects found</p>
                                    <p className="text-sm">Add a new subject below to get started</p>
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    {existingSubjects.map((subject) => (
                                        <div key={subject.id} className="border border-gray-300 rounded-lg overflow-hidden">
                                            {/* Subject Header */}
                                            <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-4 flex items-center justify-between">
                                                <div className="flex items-center space-x-3 flex-1">
                                                    <button
                                                        onClick={() => toggleSubjectExpansion(subject.id)}
                                                        className="text-gray-600 hover:text-gray-800 transition"
                                                    >
                                                        <svg 
                                                            className={`w-5 h-5 transition-transform ${expandedSubjects[subject.id] ? 'rotate-90' : ''}`}
                                                            fill="none" 
                                                            stroke="currentColor" 
                                                            viewBox="0 0 24 24"
                                                        >
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                                        </svg>
                                                    </button>
                                                    <h3 className="text-lg font-bold text-gray-800">{subject.name}</h3>
                                                    <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                                                        {subject.papers?.length || 0} papers
                                                    </span>
                                                </div>
                                                <div className="flex items-center space-x-2">
                                                    <button
                                                        onClick={() => handleEditSubject(subject, false)}
                                                        className="text-blue-600 hover:text-blue-700 p-2 hover:bg-blue-50 rounded transition"
                                                        title="Edit Subject Name"
                                                    >
                                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                                        </svg>
                                                    </button>
                                                    <button
                                                        onClick={() => handleEditSubject(subject, true)}
                                                        className="text-purple-600 hover:text-purple-700 p-2 hover:bg-purple-50 rounded transition"
                                                        title="Manage Papers & Structure"
                                                    >
                                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                                                        </svg>
                                                    </button>
                                                    <button
                                                        onClick={() => handleDeleteSubject(subject)}
                                                        className="text-red-600 hover:text-red-700 p-2 hover:bg-red-50 rounded transition"
                                                        title="Delete Subject"
                                                    >
                                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                                        </svg>
                                                    </button>
                                                </div>
                                            </div>

                                            {/* Subject Content (Papers) */}
                                            {expandedSubjects[subject.id] && (
                                                <div className="p-4 bg-gray-50 space-y-3">
                                                    {subject.papers?.length === 0 ? (
                                                        <p className="text-gray-500 text-sm text-center py-4">No papers added yet</p>
                                                    ) : (
                                                        subject.papers?.map((paper) => (
                                                            <div key={paper.id} className="bg-white rounded-lg border border-gray-200 overflow-hidden">
                                                                {/* Paper Header */}
                                                                <div className="bg-blue-50 p-3 flex items-center justify-between">
                                                                    <div className="flex items-center space-x-2 flex-1">
                                                                        <button
                                                                            onClick={() => togglePaperExpansion(paper.id)}
                                                                            className="text-gray-600 hover:text-gray-800 transition"
                                                                        >
                                                                            <svg 
                                                                                className={`w-4 h-4 transition-transform ${expandedPapers[paper.id] ? 'rotate-90' : ''}`}
                                                                                fill="none" 
                                                                                stroke="currentColor" 
                                                                                viewBox="0 0 24 24"
                                                                            >
                                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                                                            </svg>
                                                                        </button>
                                                                        <h4 className="font-semibold text-gray-700">{paper.name}</h4>
                                                                        <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
                                                                            {paper.topics?.length || 0} topics
                                                                        </span>
                                                                        <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">
                                                                            {paper.sections?.length || 0} sections
                                                                        </span>
                                                                    </div>
                                                                    <div className="flex items-center space-x-2">
                                                                        <button
                                                                            onClick={() => handleEditPaper(subject, paper)}
                                                                            className="text-blue-600 hover:text-blue-700 p-1 hover:bg-blue-100 rounded transition"
                                                                            title="Edit Paper"
                                                                        >
                                                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                                                            </svg>
                                                                        </button>
                                                                        <button
                                                                            onClick={() => handleDeletePaper(subject, paper)}
                                                                            className="text-red-600 hover:text-red-700 p-1 hover:bg-red-100 rounded transition"
                                                                            title="Delete Paper"
                                                                        >
                                                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                                                            </svg>
                                                                        </button>
                                                                    </div>
                                                                </div>

                                                                {/* Paper Content (Topics & Sections) */}
                                                                {expandedPapers[paper.id] && (
                                                                    <div className="p-3 space-y-3">
                                                                        {/* Topics */}
                                                                        <div>
                                                                            <h5 className="text-sm font-semibold text-gray-600 mb-2">Topics:</h5>
                                                                            {paper.topics?.length === 0 ? (
                                                                                <p className="text-gray-400 text-xs">No topics</p>
                                                                            ) : (
                                                                                <div className="space-y-1">
                                                                                    {paper.topics?.map((topic) => (
                                                                                        <div key={topic.id} className="flex items-center justify-between bg-gray-50 p-2 rounded">
                                                                                            <span className="text-sm text-gray-700">{topic.name}</span>
                                                                                            <div className="flex items-center space-x-1">
                                                                                                <button
                                                                                                    onClick={() => handleEditTopic(subject, paper, topic)}
                                                                                                    className="text-blue-600 hover:text-blue-700 p-1 hover:bg-blue-100 rounded transition"
                                                                                                    title="Edit Topic"
                                                                                                >
                                                                                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                                                                                    </svg>
                                                                                                </button>
                                                                                                <button
                                                                                                    onClick={() => handleDeleteTopic(subject, paper, topic)}
                                                                                                    className="text-red-600 hover:text-red-700 p-1 hover:bg-red-100 rounded transition"
                                                                                                    title="Delete Topic"
                                                                                                >
                                                                                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                                                                                    </svg>
                                                                                                </button>
                                                                                            </div>
                                                                                        </div>
                                                                                    ))}
                                                                                </div>
                                                                            )}
                                                                        </div>

                                                                        {/* Sections */}
                                                                        <div>
                                                                            <h5 className="text-sm font-semibold text-gray-600 mb-2">Sections:</h5>
                                                                            {paper.sections?.length === 0 || (paper.sections?.length === 1 && paper.sections[0].name === 'None') ? (
                                                                                <p className="text-gray-400 text-xs">No sections</p>
                                                                            ) : (
                                                                                <div className="space-y-1">
                                                                                    {paper.sections?.map((section) => (
                                                                                        section.name !== 'None' && (
                                                                                            <div key={section.id} className="flex items-center justify-between bg-gray-50 p-2 rounded">
                                                                                                <span className="text-sm text-gray-700">{section.name}</span>
                                                                                                <div className="flex items-center space-x-1">
                                                                                                    <button
                                                                                                        onClick={() => handleEditSection(subject, paper, section)}
                                                                                                        className="text-blue-600 hover:text-blue-700 p-1 hover:bg-blue-100 rounded transition"
                                                                                                        title="Edit Section"
                                                                                                    >
                                                                                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                                                                                        </svg>
                                                                                                    </button>
                                                                                                    <button
                                                                                                        onClick={() => handleDeleteSection(subject, paper, section)}
                                                                                                        className="text-red-600 hover:text-red-700 p-1 hover:bg-red-100 rounded transition"
                                                                                                        title="Delete Section"
                                                                                                    >
                                                                                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                                                                                        </svg>
                                                                                                    </button>
                                                                                                </div>
                                                                                            </div>
                                                                                        )
                                                                                    ))}
                                                                                </div>
                                                                            )}
                                                                        </div>
                                                                    </div>
                                                                )}
                                                            </div>
                                                        ))
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Add New Subject Form */}
                        <div className="bg-white rounded-xl shadow-lg p-8">
                        <h2 className="text-2xl font-bold text-gray-800 mb-6">Add New Subject</h2>
                        
                        <form onSubmit={handleSubmitNewSubject}>
                            {/* Subject Name */}
                            <div className="mb-6">
                                <label className="block text-sm font-bold text-gray-700 mb-2">
                                    Subject Name *
                                </label>
                                <input
                                    type="text"
                                    value={newSubjectName}
                                    onChange={(e) => setNewSubjectName(e.target.value)}
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                    placeholder="e.g., Computer Science"
                                    required
                                />
                            </div>

                            {/* Papers */}
                            <div className="mb-6">
                                <div className="flex justify-between items-center mb-4">
                                    <h3 className="text-lg font-bold text-gray-800">Papers</h3>
                                    <button
                                        type="button"
                                        onClick={addPaper}
                                        className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition text-sm"
                                    >
                                        + Add Paper
                                    </button>
                                </div>

                                {newSubjectPapers.map((paper, paperIndex) => (
                                    <div key={paperIndex} className="border border-gray-300 rounded-lg p-6 mb-4">
                                        <div className="flex justify-between items-center mb-4">
                                            <h4 className="text-md font-bold text-gray-700">Paper {paperIndex + 1}</h4>
                                            {newSubjectPapers.length > 1 && (
                                                <button
                                                    type="button"
                                                    onClick={() => removePaper(paperIndex)}
                                                    className="text-red-600 hover:text-red-700 text-sm font-semibold"
                                                >
                                                    Remove Paper
                                                </button>
                                            )}
                                        </div>

                                        {/* Paper Name */}
                                        <div className="mb-4">
                                            <label className="block text-sm font-bold text-gray-700 mb-2">
                                                Paper Name *
                                            </label>
                                            <input
                                                type="text"
                                                value={paper.name}
                                                onChange={(e) => updatePaperName(paperIndex, e.target.value)}
                                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                                placeholder="e.g., Paper 1"
                                                required
                                            />
                                        </div>

                                        {/* Topics */}
                                        <div className="mb-4">
                                            <div className="flex justify-between items-center mb-2">
                                                <label className="block text-sm font-bold text-gray-700">
                                                    Topics
                                                </label>
                                                <button
                                                    type="button"
                                                    onClick={() => addTopic(paperIndex)}
                                                    className="text-green-600 hover:text-green-700 text-sm font-semibold"
                                                >
                                                    + Add Topic
                                                </button>
                                            </div>
                                            {paper.topics.map((topic, topicIndex) => (
                                                <div key={topicIndex} className="flex items-center space-x-2 mb-2">
                                                    <input
                                                        type="text"
                                                        value={topic}
                                                        onChange={(e) => updateTopic(paperIndex, topicIndex, e.target.value)}
                                                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                                        placeholder="Topic name"
                                                    />
                                                    {paper.topics.length > 1 && (
                                                        <button
                                                            type="button"
                                                            onClick={() => removeTopic(paperIndex, topicIndex)}
                                                            className="text-red-600 hover:text-red-700 px-2"
                                                        >
                                                            ✕
                                                        </button>
                                                    )}
                                                </div>
                                            ))}
                                        </div>

                                        {/* Sections */}
                                        <div className="mb-4">
                                            <div className="flex justify-between items-center mb-2">
                                                <label className="block text-sm font-bold text-gray-700">
                                                    Sections (leave empty if no sections)
                                                </label>
                                                <button
                                                    type="button"
                                                    onClick={() => addSection(paperIndex)}
                                                    className="text-green-600 hover:text-green-700 text-sm font-semibold"
                                                >
                                                    + Add Section
                                                </button>
                                            </div>
                                            {paper.sections.map((section, sectionIndex) => (
                                                <div key={sectionIndex} className="flex items-center space-x-2 mb-2">
                                                    <input
                                                        type="text"
                                                        value={section}
                                                        onChange={(e) => updateSection(paperIndex, sectionIndex, e.target.value)}
                                                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                                        placeholder="Section name (e.g., Section A)"
                                                    />
                                                    {paper.sections.length > 1 && (
                                                        <button
                                                            type="button"
                                                            onClick={() => removeSection(paperIndex, sectionIndex)}
                                                            className="text-red-600 hover:text-red-700 px-2"
                                                        >
                                                            ✕
                                                        </button>
                                                    )}
                                                </div>
                                            ))}
                                            <p className="text-xs text-gray-500 mt-1">
                                                If no sections are provided, it will be recorded as "None"
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {/* Submit Button */}
                            <button
                                type="submit"
                                className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 shadow-md hover:shadow-lg"
                            >
                                Add Subject
                            </button>
                        </form>
                    </div>
                    </div>
                )}

                {/* Edit Modal */}
                {showEditModal && editingItem && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                        <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
                            <h3 className="text-xl font-bold text-gray-800 mb-4">
                                Edit {editingItem.type.charAt(0).toUpperCase() + editingItem.type.slice(1)}
                            </h3>
                            
                            <div className="mb-6">
                                <label className="block text-sm font-bold text-gray-700 mb-2">
                                    {editingItem.type.charAt(0).toUpperCase() + editingItem.type.slice(1)} Name
                                </label>
                                <input
                                    type="text"
                                    value={
                                        editingItem.type === 'subject' 
                                            ? editingItem.data.name 
                                            : editingItem.type === 'paper'
                                            ? editingItem.data.paper.name
                                            : editingItem.type === 'topic'
                                            ? editingItem.data.topic.name
                                            : editingItem.data.section.name
                                    }
                                    onChange={(e) => {
                                        if (editingItem.type === 'subject') {
                                            setEditingItem({
                                                ...editingItem,
                                                data: { ...editingItem.data, name: e.target.value }
                                            });
                                        } else if (editingItem.type === 'paper') {
                                            setEditingItem({
                                                ...editingItem,
                                                data: {
                                                    ...editingItem.data,
                                                    paper: { ...editingItem.data.paper, name: e.target.value }
                                                }
                                            });
                                        } else if (editingItem.type === 'topic') {
                                            setEditingItem({
                                                ...editingItem,
                                                data: {
                                                    ...editingItem.data,
                                                    topic: { ...editingItem.data.topic, name: e.target.value }
                                                }
                                            });
                                        } else {
                                            setEditingItem({
                                                ...editingItem,
                                                data: {
                                                    ...editingItem.data,
                                                    section: { ...editingItem.data.section, name: e.target.value }
                                                }
                                            });
                                        }
                                    }}
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                                    placeholder="Enter name"
                                />
                            </div>

                            <div className="flex space-x-3">
                                <button
                                    onClick={handleSaveEdit}
                                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200"
                                >
                                    Save Changes
                                </button>
                                <button
                                    onClick={() => {
                                        setShowEditModal(false);
                                        setEditingItem(null);
                                    }}
                                    className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold py-3 px-6 rounded-lg transition duration-200"
                                >
                                    Cancel
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Full Subject Edit Modal */}
                {showFullEditModal && editSubjectData && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
                        <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full my-8 max-h-[90vh] overflow-y-auto">
                            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 z-10">
                                <h3 className="text-2xl font-bold text-gray-800">Manage Subject Structure</h3>
                                <p className="text-sm text-gray-600 mt-1">Add or remove papers, topics, and sections</p>
                            </div>

                            <div className="p-6 space-y-6">
                                {/* Current Subject Info Summary */}
                                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                                    <div className="flex items-start space-x-3">
                                        <svg className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                        </svg>
                                        <div className="flex-1">
                                            <h4 className="text-sm font-semibold text-blue-900 mb-2">Current Subject Information</h4>
                                            <div className="text-xs text-blue-800 space-y-2">
                                                <p><span className="font-semibold">Subject:</span> {editSubjectData.name}</p>
                                                <p><span className="font-semibold">Total Papers:</span> {editSubjectData.papers.length}</p>
                                                
                                                {/* Detailed Paper Information */}
                                                <div className="mt-3 space-y-3">
                                                    {editSubjectData.papers.map((paper, idx) => {
                                                        const validTopics = Array.isArray(paper.topics) 
                                                            ? paper.topics.filter(t => t && typeof t === 'string' && t.trim())
                                                            : [];
                                                        const validSections = Array.isArray(paper.sections) 
                                                            ? paper.sections.filter(s => s && typeof s === 'string' && s.trim())
                                                            : [];
                                                        
                                                        return (
                                                            <div key={idx} className="bg-white bg-opacity-60 rounded p-2 border border-blue-100">
                                                                <div className="font-semibold text-blue-900 mb-1">
                                                                    📄 {paper.name || `Paper ${idx + 1}`}
                                                                </div>
                                                                
                                                                {/* Topics List */}
                                                                {validTopics.length > 0 && (
                                                                    <div className="ml-3 mb-1">
                                                                        <span className="font-semibold text-blue-800">Topics ({validTopics.length}):</span>
                                                                        <div className="ml-2 mt-1 flex flex-wrap gap-1">
                                                                            {validTopics.map((topic, tIdx) => (
                                                                                <span key={tIdx} className="inline-block bg-blue-100 text-blue-800 px-2 py-0.5 rounded text-xs">
                                                                                    {topic}
                                                                                </span>
                                                                            ))}
                                                                        </div>
                                                                    </div>
                                                                )}
                                                                
                                                                {/* Sections List */}
                                                                {validSections.length > 0 && (
                                                                    <div className="ml-3">
                                                                        <span className="font-semibold text-blue-800">Sections ({validSections.length}):</span>
                                                                        <div className="ml-2 mt-1 flex flex-wrap gap-1">
                                                                            {validSections.map((section, sIdx) => (
                                                                                <span key={sIdx} className="inline-block bg-green-100 text-green-800 px-2 py-0.5 rounded text-xs">
                                                                                    {section}
                                                                                </span>
                                                                            ))}
                                                                        </div>
                                                                    </div>
                                                                )}
                                                            </div>
                                                        );
                                                    })}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

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
                                        // Determine if this paper is selected for editing
                                        const isSelected = selectedPaperIndices.includes(paperIndex);
                                        // Check if this is an existing paper (from original subject) or a new one
                                        const isExistingPaper = paperIndex < (editSubjectData.originalPaperCount || 0);
                                        
                                        return (
                                            <div key={paperIndex} className={`bg-gray-50 p-4 rounded-lg border-2 space-y-4 transition-all ${
                                                isExistingPaper && !isSelected 
                                                    ? 'border-gray-300 opacity-60' 
                                                    : 'border-purple-300'
                                            }`}>
                                                {/* Paper Header with Selection Checkbox */}
                                                <div className="flex items-start justify-between">
                                                    <div className="flex items-start space-x-3 flex-1">
                                                        {/* Selection Checkbox (only for existing papers) */}
                                                        {isExistingPaper && (
                                                            <div className="pt-6">
                                                                <input
                                                                    type="checkbox"
                                                                    checked={isSelected}
                                                                    onChange={() => handleTogglePaperSelection(paperIndex)}
                                                                    className="w-5 h-5 text-purple-600 border-gray-300 rounded focus:ring-2 focus:ring-purple-500 cursor-pointer"
                                                                    title={isSelected ? "Uncheck to skip editing this paper" : "Check to edit this paper"}
                                                                />
                                                            </div>
                                                        )}
                                                        
                                                        {/* Paper Name Input */}
                                                        <div className="flex-1">
                                                            <div className="flex items-center space-x-2 mb-1">
                                                                <label className="block text-xs font-semibold text-gray-600">
                                                                    Paper {paperIndex + 1} Name *
                                                                </label>
                                                                {/* New Paper Badge */}
                                                                {!isExistingPaper && (
                                                                    <span className="inline-block bg-green-100 text-green-800 px-2 py-0.5 rounded text-xs font-semibold">
                                                                        New
                                                                    </span>
                                                                )}
                                                                {/* Selected Badge */}
                                                                {isExistingPaper && isSelected && (
                                                                    <span className="inline-block bg-purple-100 text-purple-800 px-2 py-0.5 rounded text-xs font-semibold">
                                                                        Selected
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
                                                    
                                                    {/* Action Buttons */}
                                                    <div className="flex items-start space-x-2 pt-6">
                                                        {/* View Topics Button (only for existing papers) */}
                                                        {isExistingPaper && (
                                                            <button
                                                                onClick={() => handleViewPaperTopics(paper)}
                                                                className="flex items-center space-x-1 bg-blue-500 hover:bg-blue-600 text-white px-3 py-2 rounded-lg transition text-xs font-medium"
                                                                title="View existing topics and sections"
                                                            >
                                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                                                </svg>
                                                                <span>View Topics</span>
                                                            </button>
                                                        )}
                                                        
                                                        {/* Remove Paper Button */}
                                                        {editSubjectData.papers.length > 1 && (
                                                            <button
                                                                onClick={() => handleRemoveEditPaper(paperIndex)}
                                                                className="text-red-600 hover:text-red-700 p-2 hover:bg-red-50 rounded transition"
                                                                title="Remove Paper"
                                                            >
                                                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                                                </svg>
                                                            </button>
                                                        )}
                                                    </div>
                                                </div>
                                                
                                                {/* Only show edit fields if paper is selected or is a new paper */}
                                                {(!isExistingPaper || isSelected) && (
                                                    <>

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
                                                    {paper.topics.map((topic, topicIndex) => {
                                                        // Check for duplicates - handle both object and string formats
                                                        const topicName = typeof topic === 'object' ? (topic.name || '') : (topic || '');
                                                        const isDuplicate = topicName.trim() && paper.topics.filter((t, idx) => {
                                                            const tName = typeof t === 'object' ? (t.name || '') : (t || '');
                                                            return idx !== topicIndex && tName.trim().toLowerCase() === topicName.trim().toLowerCase();
                                                        }).length > 0;
                                                        
                                                        return (
                                                            <div key={topicIndex} className="space-y-1">
                                                                <div className="flex items-center space-x-2">
                                                                    <input
                                                                        type="text"
                                                                        value={topicName}
                                                                        onChange={(e) => handleEditTopicChange(paperIndex, topicIndex, e.target.value)}
                                                                        className={`flex-1 px-3 py-2 border rounded-lg focus:ring-2 outline-none text-sm ${
                                                                            isDuplicate 
                                                                                ? 'border-red-300 bg-red-50 focus:ring-red-500 focus:border-red-500' 
                                                                                : 'border-gray-300 focus:ring-blue-500 focus:border-transparent'
                                                                        }`}
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
                                                                {isDuplicate && (
                                                                    <div className="flex items-center space-x-1 text-xs text-red-600 ml-1">
                                                                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                                                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                                                        </svg>
                                                                        <span>Duplicate topic - this topic already exists in this paper</span>
                                                                    </div>
                                                                )}
                                                            </div>
                                                        );
                                                    })}
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
                                                        {paper.sections.map((section, sectionIndex) => {
                                                            // Handle both object and string formats
                                                            const sectionName = typeof section === 'object' ? (section.name || '') : (section || '');
                                                            
                                                            return (
                                                                <div key={sectionIndex} className="flex items-center space-x-2">
                                                                    <input
                                                                        type="text"
                                                                        value={sectionName}
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
                                                            );
                                                        })}
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
                    </div>
                )}

                {/* View Paper Topics Modal */}
                {showTopicsModal && viewingPaperTopics && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                        <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
                            {/* Modal Header */}
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

                            {/* Modal Body */}
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

                                {/* Info Note */}
                                <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
                                    <div className="flex items-start space-x-3">
                                        <svg className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                                        </svg>
                                        <div>
                                            <p className="text-sm font-medium text-yellow-800">Note</p>
                                            <p className="text-sm text-yellow-700 mt-1">
                                                Check the existing topics above to avoid creating duplicates when editing this paper.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Modal Footer */}
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

                {/* Answer Lines Configuration Modal */}
                {showAnswerLinesModal && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-2">
                        <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-2">
                            <div className="flex items-center justify-between mb-2">
                                <h3 className="text-xl font-bold text-gray-800">Add Answer Lines</h3>
                                <button
                                    onClick={() => setShowAnswerLinesModal(false)}
                                    className="text-gray-500 hover:text-gray-700"
                                >
                                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>

                            <div className="space-y-2">
                                <div>
                                    <label className="block text-sm font-bold text-gray-700 mb-2">
                                        Number of Lines *
                                    </label>
                                    <input
                                        type="text"
                                        inputMode="decimal"
                                        value={answerLinesConfig.numberOfLines}
                                        onChange={(e) => {
                                            const value = e.target.value;
                                            // Allow empty input or valid decimal numbers
                                            if (value === '' || /^\d*\.?\d*$/.test(value)) {
                                                const numValue = parseFloat(value);
                                                // Only update if it's a valid number within range or empty
                                                if (value === '' || (!isNaN(numValue) && numValue >= 0.5 && numValue <= 400)) {
                                                    setAnswerLinesConfig(prev => ({ 
                                                        ...prev, 
                                                        numberOfLines: value === '' ? 0.5 : numValue
                                                    }));
                                                }
                                            }
                                        }}
                                        onBlur={(e) => {
                                            // Ensure valid value on blur
                                            const value = parseFloat(e.target.value);
                                            if (isNaN(value) || value < 0.5) {
                                                setAnswerLinesConfig(prev => ({ ...prev, numberOfLines: 0.5 }));
                                            } else if (value > 400) {
                                                setAnswerLinesConfig(prev => ({ ...prev, numberOfLines: 400 }));
                                            }
                                        }}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                        placeholder="e.g., 5 or 2.5 for half line"
                                    />
                                    <p className="text-xs text-gray-500 mt-1">
                                        Enter whole numbers (1, 2, 3,0.5, 2.5...)
                                    </p>
                                </div>

                                {/* Line Height */}
                                <div>
                                    <label className="block text-sm font-bold text-gray-700 mb-2">
                                        Line Height (spacing) *
                                    </label>
                                    <div className="flex items-center gap-2">
                                        <input
                                            type="range"
                                            min="20"
                                            max="80"
                                            value={answerLinesConfig.lineHeight}
                                            onChange={(e) => setAnswerLinesConfig(prev => ({ 
                                                ...prev, 
                                                lineHeight: parseInt(e.target.value) 
                                            }))}
                                            className="flex-1"
                                        />
                                        <span className="text-sm font-semibold text-gray-700 w-12">{answerLinesConfig.lineHeight}px</span>
                                    </div>
                                    <p className="text-xs text-gray-500 mt-1">
                                        Adjust spacing between lines (20px = tight, 80px = wide)
                                    </p>
                                </div>

                                {/* Line Style */}
                                <div>
                                    <label className="block text-sm font-bold text-gray-700 mb-2">
                                        Line Style *
                                    </label>
                                    <div className="grid grid-cols-2 gap-3">
                                        <button
                                            type="button"
                                            onClick={() => setAnswerLinesConfig(prev => ({ ...prev, lineStyle: 'dotted' }))}
                                            className={`px-4 py-3 rounded-lg border-2 transition ${
                                                answerLinesConfig.lineStyle === 'dotted'
                                                    ? 'border-indigo-600 bg-indigo-50 text-indigo-700 font-bold'
                                                    : 'border-gray-300 hover:border-indigo-400'
                                            }`}
                                        >
                                            <div className="border-b-2 border-dotted border-gray-600 mb-1"></div>
                                            Dotted
                                        </button>
                                        <button
                                            type="button"
                                            onClick={() => setAnswerLinesConfig(prev => ({ ...prev, lineStyle: 'solid' }))}
                                            className={`px-4 py-3 rounded-lg border-2 transition ${
                                                answerLinesConfig.lineStyle === 'solid'
                                                    ? 'border-indigo-600 bg-indigo-50 text-indigo-700 font-bold'
                                                    : 'border-gray-300 hover:border-indigo-400'
                                            }`}
                                        >
                                            <div className="border-b-2 border-solid border-gray-600 mb-1"></div>
                                            Solid
                                        </button>
                                    </div>
                                </div>

                                {/* Opacity/Visibility */}
                                <div>
                                    <label className="block text-sm font-bold text-gray-700 mb-2">
                                        Line Visibility (Opacity) *
                                    </label>
                                    <div className="flex items-center gap-2">
                                        <input
                                            type="range"
                                            min="0.1"
                                            max="1"
                                            step="0.1"
                                            value={answerLinesConfig.opacity}
                                            onChange={(e) => setAnswerLinesConfig(prev => ({ 
                                                ...prev, 
                                                opacity: parseFloat(e.target.value) 
                                            }))}
                                            className="flex-1"
                                        />
                                        <span className="text-sm font-semibold text-gray-700 w-12">{Math.round(answerLinesConfig.opacity * 100)}%</span>
                                    </div>
                                    <p className="text-xs text-gray-500 mt-1">
                                        10% = very faint, 100% = fully visible
                                    </p>
                                </div>

                                {/* Preview */}
                                <div className="bg-gray-50 rounded-lg p-4">
                                    <p className="text-xs font-bold text-gray-700 mb-0">Preview:</p>
                                    <div className="bg-white p-3 rounded border border-gray-300 overflow-y-auto h-24">
                                        {[...Array(Math.min(3, Math.ceil(answerLinesConfig.numberOfLines)))].map((_, idx) => (
                                            <div
                                                key={idx}
                                                style={{
                                                    height: `${answerLinesConfig.lineHeight}px`,
                                                    borderBottom: `2px ${answerLinesConfig.lineStyle} rgba(0, 0, 0, ${answerLinesConfig.opacity})`,
                                                    marginBottom: idx === Math.min(3, Math.ceil(answerLinesConfig.numberOfLines)) - 1 ? 0 : 0
                                                }}
                                            ></div>
                                        ))}
                                        {answerLinesConfig.numberOfLines > 3 && (
                                            <p className="text-xs text-gray-500 text-center mt-2">
                                                ... and {answerLinesConfig.numberOfLines - 3} more lines
                                            </p>
                                        )}
                                    </div>
                                </div>
                            </div>

                            <div className="flex space-x-3 mt-4">
                                <button
                                    onClick={() => {
                                        // Add lines to the appropriate section
                                        const lineBlock = {
                                            id: Date.now() + Math.random(),
                                            ...answerLinesConfig
                                        };
                                        
                                        if (answerLinesConfig.targetSection === 'question') {
                                            setQuestionAnswerLines(prev => [...prev, lineBlock]);
                                            // Insert placeholder in question text at cursor position
                                            const textarea = questionTextareaRef.current;
                                            if (textarea) {
                                                const cursorPos = textarea.selectionStart;
                                                const textBefore = questionText.substring(0, cursorPos);
                                                const textAfter = questionText.substring(cursorPos);
                                                setQuestionText(textBefore + `\n[LINES:${lineBlock.id}]\n` + textAfter);
                                            } else {
                                                setQuestionText(prev => prev + `\n[LINES:${lineBlock.id}]\n`);
                                            }
                                        } else {
                                            setAnswerAnswerLines(prev => [...prev, lineBlock]);
                                            // Insert placeholder in answer text at cursor position
                                            const textarea = answerTextareaRef.current;
                                            if (textarea) {
                                                const cursorPos = textarea.selectionStart;
                                                const textBefore = answerText.substring(0, cursorPos);
                                                const textAfter = answerText.substring(cursorPos);
                                                setAnswerText(textBefore + `\n[LINES:${lineBlock.id}]\n` + textAfter);
                                            } else {
                                                setAnswerText(prev => prev + `\n[LINES:${lineBlock.id}]\n`);
                                            }
                                        }
                                        
                                        setShowAnswerLinesModal(false);
                                    }}
                                    className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200"
                                >
                                    Add Lines
                                </button>
                                <button
                                    onClick={() => setShowAnswerLinesModal(false)}
                                    className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold py-3 px-6 rounded-lg transition duration-200"
                                >
                                    Cancel
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Delete Confirmation Modal */}
                {showDeleteConfirm && deletingItem && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                        <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
                            <div className="flex items-center justify-center w-12 h-12 rounded-full bg-red-100 mb-4">
                                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                </svg>
                            </div>
                            
                            <h3 className="text-xl font-bold text-gray-800 mb-2">
                                Delete {deletingItem.type.charAt(0).toUpperCase() + deletingItem.type.slice(1)}?
                            </h3>
                            
                            <p className="text-gray-600 mb-6">
                                Are you sure you want to delete{' '}
                                <span className="font-semibold">
                                    {deletingItem.type === 'subject' 
                                        ? deletingItem.data.name 
                                        : deletingItem.type === 'paper'
                                        ? deletingItem.data.paper.name
                                        : deletingItem.type === 'topic'
                                        ? deletingItem.data.topic.name
                                        : deletingItem.data.section.name}
                                </span>?{' '}
                                {deletingItem.type === 'subject' && 'All papers, topics, sections, and questions under this subject will also be affected.'}
                                {deletingItem.type === 'paper' && 'All topics, sections, and questions under this paper will also be affected.'}
                                This action cannot be undone.
                            </p>

                            <div className="flex space-x-3">
                                <button
                                    onClick={handleConfirmDelete}
                                    className="flex-1 bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200"
                                >
                                    Delete
                                </button>
                                <button
                                    onClick={() => {
                                        setShowDeleteConfirm(false);
                                        setDeletingItem(null);
                                    }}
                                    className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold py-3 px-6 rounded-lg transition duration-200"
                                >
                                    Cancel
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Edit Questions Tab Content */}
                {activeTab === 'edit' && (
                    <div className="space-y-6">
                        {/* Search Section */}
                        <div className="bg-white rounded-xl shadow-lg p-6">
                            <h2 className="text-2xl font-bold text-gray-800 mb-4">Search & Edit Questions</h2>
                            
                            <div className="flex gap-3 mb-4">
                                <div className="flex-1">
                                    <input
                                        type="text"
                                        value={searchQuery}
                                        onChange={(e) => {
                                            // Only update the search query; debounced hook + React Query will fetch
                                            setSearchQuery(e.target.value);
                                        }}
                                        placeholder="Search by question text, answer, subject, or topic... "
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                                    />
                                </div>
                                <button
                                    onClick={() => refetchQuestions()}
                                    disabled={isSearchingQuestions || searchQuery.length < 2}
                                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                    </svg>
                                    Search
                                </button>
                            </div>
                            
                            
                            {/* Enhanced Filter Options */}
                            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-4 mb-6 border-2 border-blue-200">
                                <div className="flex items-center justify-between mb-3">
                                    <h3 className="text-sm font-bold text-gray-800 flex items-center gap-2">
                                        <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                                        </svg>
                                        Advanced Filters
                                    </h3>
                                    <button
                                        onClick={() => {
                                            setEditFilterSubject('');
                                            setEditFilterPaper('');
                                            setEditFilterTopic('');
                                            setEditFilterStatus('all');
                                            setEditFilterType('all');
                                            setEditAvailablePapers([]);
                                            setEditAvailableTopics([]);
                                            setSearchQuery('');
                                            // Re-run search with no filters
                                            refetchQuestions();
                                        }}
                                        className="text-xs text-blue-600 hover:text-blue-800 font-semibold flex items-center gap-1"
                                    >
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                        </svg>
                                        Clear All Filters
                                    </button>
                                </div>
                                
                                {/* First Row: Subject, Paper, Topic */}
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">
                                    {/* Subject Filter */}
                                    <div>
                                        <label className="block text-xs font-semibold text-gray-700 mb-1 flex items-center gap-1">
                                            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                                <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3zM3.31 9.397L5 10.12v4.102a8.969 8.969 0 00-1.05-.174 1 1 0 01-.89-.89 11.115 11.115 0 01.25-3.762zM9.3 16.573A9.026 9.026 0 007 14.935v-3.957l1.818.78a3 3 0 002.364 0l5.508-2.361a11.026 11.026 0 01.25 3.762 1 1 0 01-.89.89 8.968 8.968 0 00-5.35 2.524 1 1 0 01-1.4 0zM6 18a1 1 0 001-1v-2.065a8.935 8.935 0 00-2-.712V17a1 1 0 001 1z" />
                                            </svg>
                                            Subject
                                        </label>
                                        <select
                                            value={editFilterSubject}
                                            onChange={(e) => {
                                                setEditFilterSubject(e.target.value);
                                            }}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-sm bg-white mb-8"
                                        >
                                            <option value="">All Subjects</option>
                                            {existingSubjects.map(s => (
                                                <option key={s.id} value={s.name}>{s.name}</option>
                                            ))}
                                        </select>
                                    </div>

                                    {/* Paper Filter */}
                                    <div>
                                        <label className="block text-xs font-semibold text-gray-700 mb-1 flex items-center gap-1">
                                            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                                <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                                            </svg>
                                            Paper
                                        </label>
                                        <select
                                            value={editFilterPaper}
                                            onChange={(e) => {
                                                setEditFilterPaper(e.target.value);
                                            }}
                                            disabled={!editFilterSubject}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-sm bg-white disabled:bg-gray-100 disabled:cursor-not-allowed"
                                        >
                                            <option value="">All Papers</option>
                                            {editAvailablePapers.map(p => (
                                                <option key={p.id} value={p.name}>{p.name}</option>
                                            ))}
                                        </select>
                                    </div>

                                    {/* Topic Filter */}
                                    <div>
                                        <label className="block text-xs font-semibold text-gray-700 mb-1 flex items-center gap-1">
                                            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                                <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
                                            </svg>
                                            Topic
                                        </label>
                                        <select
                                            value={editFilterTopic}
                                            onChange={(e) => {
                                                setEditFilterTopic(e.target.value);
                                            }}
                                            disabled={!editFilterPaper}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-sm bg-white disabled:bg-gray-100 disabled:cursor-not-allowed"
                                        >
                                            <option value="">All Topics</option>
                                            {editAvailableTopics.map(t => (
                                                <option key={t.id} value={t.name}>{t.name}</option>
                                            ))}
                                        </select>
                                    </div>
                                </div>

                                {/* Second Row: Status and Type */}
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                    {/* Status Filter */}
                                    <div>
                                        <label className="block text-xs font-semibold text-gray-700 mb-1 flex items-center gap-1">
                                            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                            </svg>
                                            Status
                                        </label>
                                        <select
                                            value={editFilterStatus}
                                            onChange={(e) => {
                                                setEditFilterStatus(e.target.value);
                                            }}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-sm bg-white"
                                        >
                                            <option value="all">All Status</option>
                                            <option value="active">✓ Active Only</option>
                                            <option value="inactive">✕ Inactive Only</option>
                                        </select>
                                    </div>

                                    {/* Type Filter */}
                                    <div>
                                        <label className="block text-xs font-semibold text-gray-700 mb-1 flex items-center gap-1">
                                            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                                <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                                            </svg>
                                            Type
                                        </label>
                                        <select
                                            value={editFilterType}
                                            onChange={(e) => {
                                                setEditFilterType(e.target.value);
                                            }}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-sm bg-white"
                                        >
                                            <option value="all">All Types</option>
                                            <option value="nested">⊕ Nested Only</option>
                                            <option value="standalone">◉ Standalone Only</option>
                                        </select>
                                    </div>
                                </div>

                                {/* Active Filters Summary */}
                                {(editFilterSubject || editFilterPaper || editFilterTopic || editFilterStatus !== 'all' || editFilterType !== 'all') && (
                                    <div className="mt-3 pt-3 border-t border-blue-200">
                                        <div className="flex flex-wrap gap-2 items-center">
                                            <span className="text-xs font-semibold text-gray-600">Active Filters:</span>
                                            {editFilterSubject && (
                                                <span className="inline-flex items-center gap-1 bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
                                                    📚 {editFilterSubject}
                                                    <button
                                                        onClick={() => setEditFilterSubject('')}
                                                        className="hover:bg-blue-200 rounded-full p-0.5"
                                                    >
                                                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                                            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                                                        </svg>
                                                    </button>
                                                </span>
                                            )}
                                            {editFilterPaper && (
                                                <span className="inline-flex items-center gap-1 bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-xs">
                                                    📄 {editFilterPaper}
                                                    <button
                                                        onClick={() => setEditFilterPaper('')}
                                                        className="hover:bg-purple-200 rounded-full p-0.5"
                                                    >
                                                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                                            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                                                        </svg>
                                                    </button>
                                                </span>
                                            )}
                                            {editFilterTopic && (
                                                <span className="inline-flex items-center gap-1 bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">
                                                    📖 {editFilterTopic}
                                                    <button
                                                        onClick={() => setEditFilterTopic('')}
                                                        className="hover:bg-green-200 rounded-full p-0.5"
                                                    >
                                                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                                            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                                                        </svg>
                                                    </button>
                                                </span>
                                            )}
                                            {editFilterStatus !== 'all' && (
                                                <span className="inline-flex items-center gap-1 bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs">
                                                    {editFilterStatus === 'active' ? '✓ Active' : '✕ Inactive'}
                                                    <button
                                                        onClick={() => setEditFilterStatus('all')}
                                                        className="hover:bg-yellow-200 rounded-full p-0.5"
                                                    >
                                                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                                            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                                                        </svg>
                                                    </button>
                                                </span>
                                            )}
                                            {editFilterType !== 'all' && (
                                                <span className="inline-flex items-center gap-1 bg-indigo-100 text-indigo-800 px-2 py-1 rounded-full text-xs">
                                                    {editFilterType === 'nested' ? '⊕ Nested' : '◉ Standalone'}
                                                    <button
                                                        onClick={() => setEditFilterType('all')}
                                                        className="hover:bg-indigo-200 rounded-full p-0.5"
                                                    >
                                                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                                            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                                                        </svg>
                                                    </button>
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Search Results */}
                            {isSearchingQuestions ? (
                                <div className="flex justify-center items-center py-12">
                                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                                </div>
                            ) : searchResults.length > 0 ? (
                                <div className="space-y-3">
                                    <p className="text-sm text-gray-600 mb-3">Found {searchResults.length} question(s)</p>
                                    <div className="max-h-96 overflow-y-auto space-y-2">
                                        {renderedSearchResults}
                                    </div>
                                </div>
                            ) : searchQuery.length >= 2 ? (
                                <div className="text-center py-12 text-gray-500">
                                    <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    <p className="text-lg font-semibold">No questions found</p>
                                    <p className="text-sm">Try a different search term</p>
                                </div>
                            ) : null}
                        </div>

                        {/* Edit Form */}
                        {selectedQuestion && (
                            <form onSubmit={handleUpdateQuestion} className="bg-white rounded-xl shadow-lg p-6">
                                <div className="flex justify-between items-center mb-6">
                                    <h2 className="text-2xl font-bold text-gray-800">Edit Question</h2>
                                    <div className="flex gap-2">
                                        <button
                                            type="button"
                                            onClick={() => {
                                                setSelectedQuestion(null);
                                                setEditQuestionText('');
                                                setEditAnswerText('');
                                                setEditMarks('');
                                                setEditTopic('');
                                                setEditQuestionTopics([]);
                                                setEditIsActive(true);
                                                setEditIsNested(false);
                                                setEditIsEssayQuestion(false);
                                                setEditIsGraphQuestion(false);
                                            }}
                                            className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition"
                                        >
                                            Cancel
                                        </button>
                                        <button
                                            type="button"
                                            onClick={handleDeleteQuestion}
                                            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition flex items-center gap-2"
                                        >
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                            </svg>
                                            Delete
                                        </button>
                                        <button
                                            type="submit"
                                            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition flex items-center gap-2"
                                        >
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                            </svg>
                                            Save Changes
                                        </button>
                                    </div>
                                </div>

                                {/* Question Info */}
                                <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                                        <div>
                                            <span className="font-semibold text-gray-700">Subject:</span>
                                            <span className="ml-2 text-gray-600">{selectedQuestion.subject_name}</span>
                                        </div>
                                        {selectedQuestion.paper_name && (
                                            <div>
                                                <span className="font-semibold text-gray-700">Paper:</span>
                                                <span className="ml-2 text-gray-600">{selectedQuestion.paper_name}</span>
                                            </div>
                                        )}
                                        <div>
                                            <label className="font-semibold text-gray-700 block mb-1">Topic:</label>
                                            <select
                                                value={editTopic}
                                                onChange={(e) => setEditTopic(e.target.value)}
                                                className="w-full px-3 py-1.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-sm"
                                            >
                                                <option value="">Select topic...</option>
                                                {editQuestionTopics.map(topic => (
                                                    <option key={topic.id} value={topic.id}>
                                                        {topic.name}
                                                    </option>
                                                ))}
                                            </select>
                                        </div>
                                        {editQuestionSections && editQuestionSections.length > 0 && (
                                            <div>
                                                <label className="font-semibold text-gray-700 block mb-1">Section:</label>
                                                <select
                                                    value={editSection}
                                                    onChange={(e) => setEditSection(e.target.value)}
                                                    className="w-full px-3 py-1.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-sm"
                                                >
                                                    <option value="">Select section...</option>
                                                    {editQuestionSections.map(section => (
                                                        <option key={section.id} value={section.id}>
                                                            {section.name}
                                                        </option>
                                                    ))}
                                                </select>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* Question Content */}
                                {/* <div className="mb-6">
                                    <div className="flex items-center justify-between mb-2">
                                        <label className="block text-sm font-bold text-gray-700">
                                            Question Content *
                                        </label>
                                        
                                        {/* Text Formatting Buttons */}
                                        {/* <div className="flex items-center gap-1">
                                            <button
                                                type="button"
                                                onClick={() => applyEditQuestionFormatting('bold')}
                                                className="bg-gray-600 hover:bg-gray-700 text-white px-2 py-1.5 rounded transition text-xs font-bold"
                                                title="Bold"
                                            >
                                                B
                                            </button>
                                            <button
                                                type="button"
                                                onClick={() => applyEditQuestionFormatting('italic')}
                                                className="bg-gray-600 hover:bg-gray-700 text-white px-2 py-1.5 rounded transition text-xs italic"
                                                title="Italic"
                                            >
                                                I
                                            </button>
                                            <button
                                                type="button"
                                                onClick={() => applyEditQuestionFormatting('underline')}
                                                className="bg-gray-600 hover:bg-gray-700 text-white px-2 py-1.5 rounded transition text-xs underline"
                                                title="Underline"
                                            >
                                                U
                                            </button>
                                        </div>
                                    </div>
                                    
                                    <div className="relative border-2 border-gray-300 rounded-lg bg-white overflow-hidden" style={{ height: '50vh' }}>
                                        {/* Display Area */}
                                        {/* <div className="p-4 overflow-y-auto" style={{ height: '60%', whiteSpace: 'pre-wrap' }}>
                                            {editQuestionText.length > 0 ? (
                                                renderTextWithImages(
                                                    editQuestionText,
                                                    editQuestionInlineImages,
                                                    editQuestionImagePositions,
                                                    editQuestionAnswerLines,
                                                    null,
                                                    null,
                                                    'edit'
                                                )
                                            ) : (
                                                <span className="text-gray-400">Question preview...</span>
                                            )}
                                        </div> */}
                                         
                                        {/* Editable Textarea */}
                                        {/* <div className="absolute bottom-0 left-0 right-0 bg-white border-t-2 border-gray-300" style={{ height: '40%' }}>
                                            <textarea
                                                ref={editQuestionTextareaRef}
                                                value={editQuestionText}
                                                onChange={(e) => setEditQuestionText(e.target.value)}
                                                className="w-full h-full px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:outline-none transition text-sm resize-none"
                                                placeholder="Edit question text..."
                                                style={{ fontFamily: 'monospace' }}
                                                required
                                            />
                                        </div>
                                    </div>
                                </div>  */}

                                {/* Question Content */}
                                <div className="mb-6">
                                    <div className="flex items-center justify-between mb-2">
                                        <label className="block text-sm font-bold text-gray-700">
                                            Question Content *
                                        </label>
                                        
                                        {/* Inline Toolbar */}
                                        <div className="flex items-center gap-2 flex-wrap">
                                            {/* Image Upload */}
                                            <label className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1.5 rounded-lg cursor-pointer transition text-xs flex items-center gap-1.5">
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                                </svg>
                                                <span>Image</span>
                                                <input type="file" accept="image/*" multiple onChange={handleEditQuestionFileUpload} className="hidden" />
                                            </label>

                                            {/* Drawing Tools */}
                                            <button
                                                type="button"
                                                onClick={() => setShowEditQuestionDrawing(!showEditQuestionDrawing)}
                                                className={`${showEditQuestionDrawing ? 'bg-purple-600' : 'bg-gray-500'} hover:bg-purple-700 text-white px-3 py-1.5 rounded-lg transition text-xs flex items-center gap-1.5`}
                                            >
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                                                </svg>
                                                <span>Draw</span>
                                            </button>

                                            {/* Graph Paper */}
                                            <button
                                                type="button"
                                                onClick={() => {
                                                    setShowEditQuestionGraphPaper(!showEditQuestionGraphPaper);
                                                    if (!showEditQuestionDrawing) setShowEditQuestionDrawing(true);
                                                }}
                                                className={`${showEditQuestionGraphPaper ? 'bg-green-600' : 'bg-gray-500'} hover:bg-green-700 text-white px-3 py-1.5 rounded-lg transition text-xs flex items-center gap-1.5`}
                                            >
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                                </svg>
                                                <span>Graph</span>
                                            </button>

                                            {/* Text Formatting Buttons */}
                                            <div className="flex items-center gap-1 border-l border-gray-300 pl-2">
                                                <button
                                                    type="button"
                                                    onClick={() => applyEditQuestionFormatting('bold')}
                                                    className="bg-gray-600 hover:bg-gray-700 text-white px-2 py-1.5 rounded transition text-xs font-bold"
                                                    title="Bold"
                                                >
                                                    B
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={() => applyEditQuestionFormatting('italic')}
                                                    className="bg-gray-600 hover:bg-gray-700 text-white px-2 py-1.5 rounded transition text-xs italic"
                                                    title="Italic"
                                                >
                                                    I
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={() => applyEditQuestionFormatting('underline')}
                                                    className="bg-gray-600 hover:bg-gray-700 text-white px-2 py-1.5 rounded transition text-xs underline"
                                                    title="Underline"
                                                >
                                                    U
                                                </button>
                                            </div>

                                            {/* Answer Lines Button */}
                                            <button
                                                type="button"
                                                onClick={() => {
                                                    setEditAnswerLinesConfig(prev => ({ ...prev, targetSection: 'question' }));
                                                    setShowEditAnswerLinesModal(true);
                                                }}
                                                className="bg-indigo-500 hover:bg-indigo-600 text-white px-3 py-1.5 rounded-lg transition text-xs flex items-center gap-1.5"
                                                title="Add answer lines"
                                            >
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                                                </svg>
                                                <span>Lines</span>
                                            </button>

                                            {/* Voice Recording */}
                                            <button
                                                type="button"
                                                onClick={toggleEditQuestionVoiceRecording}
                                                className={`${isEditQuestionListening ? 'bg-red-600 animate-pulse' : 'bg-orange-500'} hover:bg-orange-700 text-white px-3 py-1.5 rounded-lg transition text-xs flex items-center gap-1.5`}
                                                title={isEditQuestionListening ? "Stop recording" : "Start recording"}
                                            >
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                                                </svg>
                                                <span>{isEditQuestionListening ? 'Recording...' : 'Mic'}</span>
                                            </button>
                                        </div>
                                    </div>
                                    
                                    <div className="relative border-2 border-gray-300 rounded-lg bg-white overflow-hidden" style={{ height: '50vh' }}>
                                        {/* Display Area */}
                                        <div className="p-4 overflow-y-auto" style={{ height: '60%', whiteSpace: 'pre-wrap' }}>
                                            {editQuestionText.length > 0 ? (
                                                renderTextWithImages(
                                                    editQuestionText,
                                                    editQuestionInlineImages,
                                                    editQuestionImagePositions,
                                                    editQuestionAnswerLines,
                                                    (imageId) => {
                                                        setEditQuestionInlineImages(prev => prev.filter(img => img.id !== imageId));
                                                        const regexOld = new RegExp(`\\[IMAGE:${imageId}:\\d+px\\]`, 'g');
                                                        const regexNew = new RegExp(`\\[IMAGE:${imageId}:\\d+x\\d+px\\]`, 'g');
                                                        setEditQuestionText(prev => prev.replace(regexOld, '').replace(regexNew, ''));
                                                    },
                                                    (lineId) => {
                                                        setEditQuestionAnswerLines(prev => prev.filter(line => line.id !== lineId));
                                                        setEditQuestionText(prev => prev.replace(`[LINES:${lineId}]`, ''));
                                                    },
                                                    'edit'
                                                )
                                            ) : (
                                                <span className="text-gray-400">Question preview...</span>
                                            )}
                                        </div>
                                        
                                        {/* Editable Textarea */}
                                        <div className="absolute bottom-0 left-0 right-0 bg-white border-t-2 border-gray-300" style={{ height: '40%' }}>
                                            <textarea
                                                ref={editQuestionTextareaRef}
                                                value={editQuestionText}
                                                onChange={(e) => setEditQuestionText(e.target.value)}
                                                className="w-full h-full px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:outline-none transition text-sm resize-none"
                                                placeholder="Edit question text..."
                                                style={{ fontFamily: 'monospace' }}
                                                required
                                            />
                                        </div>
                                    </div>
                                </div>

                                {/* Drawing Tool Panel for Edit Question */}
                                {showEditQuestionDrawing && (
                                    <div className="mb-6 border-2 border-purple-300 rounded-lg p-4 bg-gradient-to-br from-purple-50 to-indigo-50">
                                        <div className="flex items-center justify-between mb-3">
                                            <h3 className="font-bold text-gray-800 flex items-center gap-2">
                                                <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                                                </svg>
                                                Drawing Tools
                                            </h3>
                                           <button type="button" onClick={() => setShowEditQuestionDrawing(false)} className="text-gray-500 hover:text-gray-700">
                                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                                </svg>
                                            </button>
                                        </div>
                                        {/* Drawing Controls */}
                                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                                            {/* Tool Selection */}
                                            <div>
                                                <label className="text-xs font-semibold text-gray-700 mb-1 block">Tool</label>
                                                <div className="flex gap-1">
                                                    <button 
                                                        type="button" 
                                                        onClick={() => setEditQuestionDrawingTool('pen')} 
                                                        className={`flex-1 px-3 py-2 rounded text-sm font-medium transition ${editQuestionDrawingTool === 'pen' ? 'bg-purple-600 text-white shadow-lg' : 'bg-white text-gray-700 border border-gray-300'}`}
                                                    >
                                                        ✏️ Pen
                                                    </button>
                                                    <button 
                                                        type="button" 
                                                        onClick={() => setEditQuestionDrawingTool('line')} 
                                                        className={`flex-1 px-3 py-2 rounded text-sm font-medium transition ${editQuestionDrawingTool === 'line' ? 'bg-purple-600 text-white shadow-lg' : 'bg-white text-gray-700 border border-gray-300'}`}
                                                    >
                                                        📏 Line
                                                    </button>
                                                </div>
                                            </div>

                                            {/* Shapes */}
                                            <div>
                                                <label className="text-xs font-semibold text-gray-700 mb-1 block">Shapes</label>
                                                <div className="flex gap-1">
                                                    <button 
                                                        type="button" 
                                                        onClick={() => setEditQuestionDrawingTool('rectangle')} 
                                                        className={`flex-1 px-3 py-2 rounded text-sm font-medium transition ${editQuestionDrawingTool === 'rectangle' ? 'bg-purple-600 text-white shadow-lg' : 'bg-white text-gray-700 border border-gray-300'}`}
                                                    >
                                                        ▭
                                                    </button>
                                                    <button 
                                                        type="button" 
                                                        onClick={() => setEditQuestionDrawingTool('circle')} 
                                                        className={`flex-1 px-3 py-2 rounded text-sm font-medium transition ${editQuestionDrawingTool === 'circle' ? 'bg-purple-600 text-white shadow-lg' : 'bg-white text-gray-700 border border-gray-300'}`}
                                                    >
                                                        ⭕
                                                    </button>
                                                    <button 
                                                        type="button" 
                                                        onClick={() => setEditQuestionDrawingTool('eraser')} 
                                                        className={`flex-1 px-3 py-2 rounded text-sm font-medium transition ${editQuestionDrawingTool === 'eraser' ? 'bg-purple-600 text-white shadow-lg' : 'bg-white text-gray-700 border border-gray-300'}`}
                                                    >
                                                        🧹
                                                    </button>
                                                </div>
                                            </div>
                                            
                                            {/* Color Picker */}
                                            <div>
                                                <label className="text-xs font-semibold text-gray-700 mb-1 block">Color</label>
                                                <div className="flex gap-2 items-center">
                                                    <input 
                                                        type="color" 
                                                        value={editQuestionDrawingColor} 
                                                        onChange={(e) => setEditQuestionDrawingColor(e.target.value)} 
                                                        className="w-12 h-9 rounded cursor-pointer border-2 border-gray-300"
                                                    />
                                                    <select 
                                                        value={editQuestionDrawingColor} 
                                                        onChange={(e) => setEditQuestionDrawingColor(e.target.value)}
                                                        className="flex-1 px-2 py-2 text-xs border border-gray-300 rounded"
                                                    >
                                                        <option value="#000000">Black</option>
                                                        <option value="#FF0000">Red</option>
                                                        <option value="#0000FF">Blue</option>
                                                        <option value="#008000">Green</option>
                                                    </select>
                                                </div>
                                            </div>
                                            
                                            {/* Line Width */}
                                            <div>
                                                <label className="text-xs font-semibold text-gray-700 mb-1 block">
                                                    Width: {editQuestionDrawingWidth}px
                                                </label>
                                                <input 
                                                    type="range" 
                                                    min="1" 
                                                    max="20" 
                                                    value={editQuestionDrawingWidth} 
                                                    onChange={(e) => setEditQuestionDrawingWidth(e.target.value)} 
                                                    className="w-full h-9"
                                                />
                                            </div>
                                        </div>
                                        
                                        {/* Action Buttons */}
                                        <div className="flex gap-2 mb-3">
                                            <button 
                                                type="button" 
                                                onClick={clearEditQuestionCanvas} 
                                                className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg font-semibold transition text-sm"
                                            >
                                                Clear Canvas
                                            </button>
                                            <button 
                                                type="button" 
                                                onClick={saveEditQuestionDrawing} 
                                                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-semibold transition text-sm"
                                            >
                                                Save & Insert Drawing
                                            </button>
                                        </div>
                                        
                                        {/* Canvas */}
                                        <div className="relative bg-white rounded-lg border-2 border-gray-300 overflow-auto">
                                            <canvas
                                                ref={editQuestionCanvasRef}
                                                onMouseDown={startEditQuestionDrawing}
                                                onMouseMove={drawEditQuestion}
                                                onMouseUp={stopEditQuestionDrawing}
                                                onMouseLeave={stopEditQuestionDrawing}
                                                className="mx-auto cursor-crosshair"
                                                style={{ width: '794px', height: '600px', maxWidth: '100%' }}
                                            />
                                        </div>
                                    </div>

                                )}

                                {/* Answer Content */}
                                <div className="mb-6">
                                    <div className="flex items-center justify-between mb-2">
                                        <label className="block text-sm font-bold text-gray-700">
                                            Answer Content *
                                        </label>
                                        
                                        {/* Inline Toolbar */}
                                        <div className="flex items-center gap-2 flex-wrap">
                                            {/* Image Upload */}
                                            <label className="bg-orange-500 hover:bg-orange-600 text-white px-3 py-1.5 rounded-lg cursor-pointer transition text-xs flex items-center gap-1.5">
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                                </svg>
                                                <span>Image</span>
                                                <input type="file" accept="image/*" multiple onChange={handleEditAnswerFileUpload} className="hidden" />
                                            </label>

                                            {/* Drawing Tools */}
                                            <button
                                                type="button"
                                                onClick={() => setShowEditAnswerDrawing(!showEditAnswerDrawing)}
                                                className={`${showEditAnswerDrawing ? 'bg-purple-600' : 'bg-gray-500'} hover:bg-purple-700 text-white px-3 py-1.5 rounded-lg transition text-xs flex items-center gap-1.5`}
                                            >
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                                                </svg>
                                                <span>Draw</span>
                                            </button>

                                            {/* Graph Paper */}
                                            <button
                                                type="button"
                                                onClick={() => {
                                                    setShowEditAnswerGraphPaper(!showEditAnswerGraphPaper);
                                                    if (!showEditAnswerDrawing) setShowEditAnswerDrawing(true);
                                                }}
                                                className={`${showEditAnswerGraphPaper ? 'bg-green-600' : 'bg-gray-500'} hover:bg-green-700 text-white px-3 py-1.5 rounded-lg transition text-xs flex items-center gap-1.5`}
                                            >
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                                </svg>
                                                <span>Graph</span>
                                            </button>

                                            {/* Text Formatting */}
                                            <div className="flex items-center gap-1 border-l border-gray-300 pl-2">
                                                <button
                                                    type="button"
                                                    onClick={() => applyEditAnswerFormatting('bold')}
                                                    className="bg-gray-600 hover:bg-gray-700 text-white px-2 py-1.5 rounded transition text-xs font-bold"
                                                >
                                                    B
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={() => applyEditAnswerFormatting('italic')}
                                                    className="bg-gray-600 hover:bg-gray-700 text-white px-2 py-1.5 rounded transition text-xs italic"
                                                >
                                                    I
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={() => applyEditAnswerFormatting('underline')}
                                                    className="bg-gray-600 hover:bg-gray-700 text-white px-2 py-1.5 rounded transition text-xs underline"
                                                >
                                                    U
                                                </button>
                                            </div>

                                            {/* Answer Lines */}
                                            <button
                                                type="button"
                                                onClick={() => {
                                                    setEditAnswerLinesConfig(prev => ({ ...prev, targetSection: 'answer' }));
                                                    setShowEditAnswerLinesModal(true);
                                                }}
                                                className="bg-indigo-500 hover:bg-indigo-600 text-white px-3 py-1.5 rounded-lg transition text-xs flex items-center gap-1.5"
                                            >
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                                                </svg>
                                                <span>Lines</span>
                                            </button>

                                            {/* Voice Recording */}
                                            <button
                                                type="button"
                                                onClick={toggleEditAnswerVoiceRecording}
                                                className={`${isEditAnswerListening ? 'bg-red-600 animate-pulse' : 'bg-orange-500'} hover:bg-orange-700 text-white px-3 py-1.5 rounded-lg transition text-xs flex items-center gap-1.5`}
                                            >
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                                                </svg>
                                                <span>{isEditAnswerListening ? 'Recording...' : 'Mic'}</span>
                                            </button>
                                        </div>
                                    </div>
                                    
                                    <div className="relative border-2 border-gray-300 rounded-lg bg-white overflow-hidden" style={{ height: '50vh' }}>
                                        <div className="p-4 overflow-y-auto" style={{ height: '60%', whiteSpace: 'pre-wrap' }}>
                                            {editAnswerText.length > 0 ? (
                                                renderTextWithImages(
                                                    editAnswerText,
                                                    editAnswerInlineImages,
                                                    editAnswerImagePositions,
                                                    editAnswerAnswerLines,
                                                    (imageId) => {
                                                        setEditAnswerInlineImages(prev => prev.filter(img => img.id !== imageId));
                                                        const regexOld = new RegExp(`\\[IMAGE:${imageId}:\\d+px\\]`, 'g');
                                                        const regexNew = new RegExp(`\\[IMAGE:${imageId}:\\d+x\\d+px\\]`, 'g');
                                                        setEditAnswerText(prev => prev.replace(regexOld, '').replace(regexNew, ''));
                                                    },
                                                    (lineId) => {
                                                        setEditAnswerAnswerLines(prev => prev.filter(line => line.id !== lineId));
                                                        setEditAnswerText(prev => prev.replace(`[LINES:${lineId}]`, ''));
                                                    },
                                                    'edit'
                                                )
                                            ) : (
                                                <span className="text-gray-400">Answer preview...</span>
                                            )}
                                        </div>
                                        
                                        <div className="absolute bottom-0 left-0 right-0 bg-white border-t-2 border-gray-300" style={{ height: '40%' }}>
                                            <textarea
                                                ref={editAnswerTextareaRef}
                                                value={editAnswerText}
                                                onChange={(e) => setEditAnswerText(e.target.value)}
                                                className="w-full h-full px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:outline-none transition text-sm resize-none"
                                                placeholder="Edit answer text..."
                                                style={{ fontFamily: 'monospace' }}
                                                required
                                            />
                                        </div>
                                    </div>
                                </div>

                                {/* Drawing Tool Panel for Edit Answer */}
                                {showEditAnswerDrawing && (
                                    <div className="mb-6 border-2 border-orange-400 rounded-lg p-4 bg-orange-50">
                                        <div className="flex items-center justify-between mb-3">
                                            <h3 className="text-lg font-bold text-orange-800">🎨 Answer Drawing Tool</h3>
                                            <button
                                                type="button"
                                                onClick={() => setShowEditAnswerDrawing(false)}
                                                className="text-orange-600 hover:text-orange-800 font-bold"
                                            >
                                                ✕ Close
                                            </button>
                                        </div>
                                        
                                        <div className="mb-3 flex flex-wrap gap-3 items-center bg-white p-3 rounded-lg border border-orange-200">
                                            <div className="flex gap-2">
                                                <button type="button" onClick={() => setEditAnswerDrawingTool('pen')} className={`px-3 py-2 rounded ${editAnswerDrawingTool === 'pen' ? 'bg-orange-500 text-white' : 'bg-gray-200 hover:bg-gray-300'}`}>✏️ Pen</button>
                                                <button type="button" onClick={() => setEditAnswerDrawingTool('eraser')} className={`px-3 py-2 rounded ${editAnswerDrawingTool === 'eraser' ? 'bg-orange-500 text-white' : 'bg-gray-200 hover:bg-gray-300'}`}>🧹 Eraser</button>
                                                <button type="button" onClick={() => setEditAnswerDrawingTool('line')} className={`px-3 py-2 rounded ${editAnswerDrawingTool === 'line' ? 'bg-orange-500 text-white' : 'bg-gray-200 hover:bg-gray-300'}`}>📏 Line</button>
                                                <button type="button" onClick={() => setEditAnswerDrawingTool('rectangle')} className={`px-3 py-2 rounded ${editAnswerDrawingTool === 'rectangle' ? 'bg-orange-500 text-white' : 'bg-gray-200 hover:bg-gray-300'}`}>▭</button>
                                                <button type="button" onClick={() => setEditAnswerDrawingTool('circle')} className={`px-3 py-2 rounded ${editAnswerDrawingTool === 'circle' ? 'bg-orange-500 text-white' : 'bg-gray-200 hover:bg-gray-300'}`}>⭕</button>
                                            </div>
                                            
                                            <div className="flex items-center gap-2">
                                                <label className="text-sm font-medium">Color:</label>
                                                <input type="color" value={editAnswerDrawingColor} onChange={(e) => setEditAnswerDrawingColor(e.target.value)} className="w-10 h-10 rounded cursor-pointer"/>
                                            </div>
                                            
                                            <div className="flex items-center gap-2">
                                                <label className="text-sm font-medium">Width:</label>
                                                <input type="range" min="1" max="20" value={editAnswerDrawingWidth} onChange={(e) => setEditAnswerDrawingWidth(parseInt(e.target.value))} className="w-24"/>
                                                <span className="text-sm font-bold w-8">{editAnswerDrawingWidth}px</span>
                                            </div>
                                            
                                            <label className="flex items-center gap-2 cursor-pointer">
                                                <input type="checkbox" checked={showEditAnswerGraphPaper} onChange={(e) => setShowEditAnswerGraphPaper(e.target.checked)} className="w-4 h-4"/>
                                                <span className="text-sm font-medium">Graph Paper</span>
                                            </label>
                                            
                                            <button type="button" onClick={clearEditAnswerCanvas} className="px-3 py-2 bg-red-500 text-white rounded hover:bg-red-600">🗑️ Clear</button>
                                        </div>
                                        
                                        <div className="bg-white rounded-lg border-2 border-orange-300 overflow-hidden">
                                            <canvas
                                                ref={editAnswerCanvasRef}
                                                onMouseDown={startEditAnswerDrawing}
                                                onMouseMove={drawEditAnswer}
                                                onMouseUp={stopEditAnswerDrawing}
                                                onMouseLeave={stopEditAnswerDrawing}
                                                className="cursor-crosshair block"
                                                style={{ width: '100%', maxWidth: '794px' }}
                                            />
                                        </div>
                                        
                                        <div className="mt-3 flex justify-end">
                                            <button type="button" onClick={saveEditAnswerDrawing} className="px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 font-bold shadow-md">
                                                💾 Save & Insert Drawing
                                            </button>
                                        </div>
                                    </div>
                                )}

                                {/* Edit Answer Lines Configuration Modal */}
                                {showEditAnswerLinesModal && (
                                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                                        <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
                                            <div className="flex items-center justify-between mb-4">
                                                <h3 className="text-xl font-bold text-gray-800">Add Answer Lines</h3>
                                                <button
                                                    onClick={() => setShowEditAnswerLinesModal(false)}
                                                    className="text-gray-500 hover:text-gray-700"
                                                >
                                                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                                    </svg>
                                                </button>
                                            </div>

                                            <div className="space-y-4">
                                                <div>
                                                    <label className="block text-sm font-bold text-gray-700 mb-2">Number of Lines *</label>
                                                    <input
                                                        type="text"
                                                        inputMode="decimal"
                                                        value={editAnswerLinesConfig.numberOfLines}
                                                        onChange={(e) => {
                                                            const value = e.target.value;
                                                            if (value === '' || /^\d*\.?\d*$/.test(value)) {
                                                                const numValue = parseFloat(value);
                                                                if (value === '' || (!isNaN(numValue) && numValue >= 0.5 && numValue <= 400)) {
                                                                    setEditAnswerLinesConfig(prev => ({ 
                                                                        ...prev, 
                                                                        numberOfLines: value === '' ? 0.5 : numValue
                                                                    }));
                                                                }
                                                            }
                                                        }}
                                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                                                        placeholder="e.g., 5 or 2.5"
                                                    />
                                                </div>

                                                <div>
                                                    <label className="block text-sm font-bold text-gray-700 mb-2">Line Height *</label>
                                                    <div className="flex items-center gap-2">
                                                        <input
                                                            type="range"
                                                            min="20"
                                                            max="80"
                                                            value={editAnswerLinesConfig.lineHeight}
                                                            onChange={(e) => setEditAnswerLinesConfig(prev => ({ 
                                                                ...prev, 
                                                                lineHeight: parseInt(e.target.value) 
                                                            }))}
                                                            className="flex-1"
                                                        />
                                                        <span className="text-sm font-semibold w-12">{editAnswerLinesConfig.lineHeight}px</span>
                                                    </div>
                                                </div>

                                                <div>
                                                    <label className="block text-sm font-bold text-gray-700 mb-2">Line Style *</label>
                                                    <div className="grid grid-cols-2 gap-3">
                                                        <button
                                                            type="button"
                                                            onClick={() => setEditAnswerLinesConfig(prev => ({ ...prev, lineStyle: 'dotted' }))}
                                                            className={`px-4 py-3 rounded-lg border-2 ${editAnswerLinesConfig.lineStyle === 'dotted' ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'}`}
                                                        >
                                                            Dotted
                                                        </button>
                                                        <button
                                                            type="button"
                                                            onClick={() => setEditAnswerLinesConfig(prev => ({ ...prev, lineStyle: 'solid' }))}
                                                            className={`px-4 py-3 rounded-lg border-2 ${editAnswerLinesConfig.lineStyle === 'solid' ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'}`}
                                                        >
                                                            Solid
                                                        </button>
                                                    </div>
                                                </div>

                                                <div>
                                                    <label className="block text-sm font-bold text-gray-700 mb-2">Opacity *</label>
                                                    <div className="flex items-center gap-2">
                                                        <input
                                                            type="range"
                                                            min="0.1"
                                                            max="1"
                                                            step="0.1"
                                                            value={editAnswerLinesConfig.opacity}
                                                            onChange={(e) => setEditAnswerLinesConfig(prev => ({ 
                                                                ...prev, 
                                                                opacity: parseFloat(e.target.value) 
                                                            }))}
                                                            className="flex-1"
                                                        />
                                                        <span className="text-sm font-semibold w-12">{Math.round(editAnswerLinesConfig.opacity * 100)}%</span>
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="flex space-x-3 mt-4">
                                                <button
                                                    onClick={() => {
                                                        const lineBlock = {
                                                            id: Date.now() + Math.random(),
                                                            ...editAnswerLinesConfig
                                                        };
                                                        
                                                        if (editAnswerLinesConfig.targetSection === 'question') {
                                                            setEditQuestionAnswerLines(prev => [...prev, lineBlock]);
                                                            const textarea = editQuestionTextareaRef.current;
                                                            if (textarea) {
                                                                const cursorPos = textarea.selectionStart;
                                                                const textBefore = editQuestionText.substring(0, cursorPos);
                                                                const textAfter = editQuestionText.substring(cursorPos);
                                                                setEditQuestionText(textBefore + `\n[LINES:${lineBlock.id}]\n` + textAfter);
                                                            } else {
                                                                setEditQuestionText(prev => prev + `\n[LINES:${lineBlock.id}]\n`);
                                                            }
                                                        } else {
                                                            setEditAnswerAnswerLines(prev => [...prev, lineBlock]);
                                                            const textarea = editAnswerTextareaRef.current;
                                                            if (textarea) {
                                                                const cursorPos = textarea.selectionStart;
                                                                const textBefore = editAnswerText.substring(0, cursorPos);
                                                                const textAfter = editAnswerText.substring(cursorPos);
                                                                setEditAnswerText(textBefore + `\n[LINES:${lineBlock.id}]\n` + textAfter);
                                                            } else {
                                                                setEditAnswerText(prev => prev + `\n[LINES:${lineBlock.id}]\n`);
                                                            }
                                                        }
                                                        
                                                        setShowEditAnswerLinesModal(false);
                                                    }}
                                                    className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg"
                                                >
                                                    Add Lines
                                                </button>
                                                <button
                                                    onClick={() => setShowEditAnswerLinesModal(false)}
                                                    className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold py-3 px-6 rounded-lg"
                                                >
                                                    Cancel
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {/* Marks */}
                                <div className="mb-6">
                                    <label className="block text-sm font-bold text-gray-700 mb-2">
                                        Marks
                                    </label>
                                    <input
                                        type="number"
                                        value={editMarks}
                                        onChange={(e) => setEditMarks(e.target.value)}
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                                        placeholder="Enter marks"
                                        step="0.5"
                                        min="0"
                                    />
                                </div>

                                {/* Status Controls */}
                                <div className="mb-6 p-6 bg-gradient-to-r from-gray-50 to-blue-50 rounded-xl border-2 border-gray-200">
                                    <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                                        <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                                        </svg>
                                        Question Status
                                    </h3>
                                    
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        {/* Active/Inactive Toggle */}
                                        <div className="bg-white rounded-lg p-4 border-2 border-gray-200 hover:border-blue-300 transition">
                                            <label className="block text-sm font-bold text-gray-700 mb-3">
                                                Activation Status
                                            </label>
                                            <div className="flex gap-2">
                                                <button
                                                    type="button"
                                                    onClick={() => setEditIsActive(true)}
                                                    className={`flex-1 py-3 px-4 rounded-lg font-semibold transition flex items-center justify-center gap-2 ${
                                                        editIsActive
                                                            ? 'bg-green-600 text-white shadow-lg'
                                                            : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                                                    }`}
                                                >
                                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                                    </svg>
                                                    Active
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={() => setEditIsActive(false)}
                                                    className={`flex-1 py-3 px-4 rounded-lg font-semibold transition flex items-center justify-center gap-2 ${
                                                        !editIsActive
                                                            ? 'bg-red-600 text-white shadow-lg'
                                                            : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                                                    }`}
                                                >
                                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                                    </svg>
                                                    Inactive
                                                </button>
                                            </div>
                                            <p className="text-xs text-gray-500 mt-2">
                                                {editIsActive 
                                                    ? '✓ This question will be available for paper generation' 
                                                    : '✕ This question will be hidden from paper generation'}
                                            </p>
                                        </div>

                                        {/* Nested/Standalone Toggle */}
                                        <div className="bg-white rounded-lg p-4 border-2 border-gray-200 hover:border-purple-300 transition">
                                            <label className="block text-sm font-bold text-gray-700 mb-3">
                                                Question Type
                                            </label>
                                            <div className="flex gap-2">
                                                <button
                                                    type="button"
                                                    onClick={() => setEditIsNested(true)}
                                                    className={`flex-1 py-3 px-4 rounded-lg font-semibold transition flex items-center justify-center gap-2 ${
                                                        editIsNested
                                                            ? 'bg-purple-600 text-white shadow-lg'
                                                            : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                                                    }`}
                                                >
                                                    <span className="text-lg">⊕</span>
                                                    Nested
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={() => setEditIsNested(false)}
                                                    className={`flex-1 py-3 px-4 rounded-lg font-semibold transition flex items-center justify-center gap-2 ${
                                                        !editIsNested
                                                            ? 'bg-blue-600 text-white shadow-lg'
                                                            : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                                                    }`}
                                                >
                                                    <span className="text-lg">◉</span>
                                                    Standalone
                                                </button>
                                            </div>
                                            <p className="text-xs text-gray-500 mt-2">
                                                {editIsNested 
                                                    ? '⊕ Question has multiple parts (a, b, c, etc.)' 
                                                    : '◉ Question is a single standalone item'}
                                            </p>
                                        </div>

                                        {/* Essay Question Toggle */}
                                        <div className="bg-white rounded-lg p-4 border-2 border-gray-200 hover:border-yellow-300 transition">
                                            <label className="block text-sm font-bold text-gray-700 mb-3">
                                                Essay Question
                                            </label>
                                            <div className="flex gap-2">
                                                <button
                                                    type="button"
                                                    onClick={() => setQuestionMode('essay')}
                                                    className={`flex-1 py-3 px-4 rounded-lg font-semibold transition flex items-center justify-center gap-2 ${
                                                        editIsEssayQuestion
                                                            ? 'bg-yellow-600 text-white shadow-lg'
                                                            : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                                                    }`}
                                                >
                                                    <span className="text-lg">📝</span>
                                                    Essay
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={() => setQuestionMode('regular1')}
                                                    className={`flex-1 py-3 px-4 rounded-lg font-semibold transition flex items-center justify-center gap-2 ${
                                                        !editIsEssayQuestion
                                                            ? 'bg-gray-600 text-white shadow-lg'
                                                            : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                                                    }`}
                                                >
                                                    <span className="text-lg">📄</span>
                                                    Regular
                                                </button>
                                            </div>
                                            <p className="text-xs text-gray-500 mt-2">
                                                {editIsEssayQuestion 
                                                    ? 'Requires extended written response' 
                                                    : 'Standard question format'}
                                            </p>
                                        </div>

                                        {/* Graph Question Toggle */}
                                        <div className="bg-white rounded-lg p-4 border-2 border-gray-200 hover:border-cyan-300 transition">
                                            <label className="block text-sm font-bold text-gray-700 mb-3">
                                                Graph Question
                                            </label>
                                            <div className="flex gap-2">
                                                <button
                                                    type="button"
                                                    onClick={() => setQuestionMode('graph')}
                                                    className={`flex-1 py-3 px-4 rounded-lg font-semibold transition flex items-center justify-center gap-2 ${
                                                        editIsGraphQuestion
                                                            ? 'bg-cyan-600 text-white shadow-lg'
                                                            : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                                                    }`}
                                                >
                                                    <span className="text-lg">📊</span>
                                                    Graph
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={() => setQuestionMode('regular2')}
                                                    className={`flex-1 py-3 px-4 rounded-lg font-semibold transition flex items-center justify-center gap-2 ${
                                                        !editIsGraphQuestion
                                                            ? 'bg-gray-600 text-white shadow-lg'
                                                            : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                                                    }`}
                                                >
                                                    <span className="text-lg">📄</span>
                                                    Regular
                                                </button>
                                            </div>
                                            <p className="text-xs text-gray-500 mt-2">
                                                {editIsGraphQuestion 
                                                    ? '📊 Requires drawing/plotting graphs' 
                                                    : '📄 No graphing required'}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </form>
                        )}
                    </div>
                )}

                {/* Statistics Tab Content */}
                {activeTab === 'stats' && (() => {
                    const stats = memoizedStatistics;
                    const filteredQuestions = memoizedFilteredQuestions;
                    
                    return (
                        <div>
                            {/* Header with Refresh Button */}
                            <div className="flex justify-between items-center mb-6">
                                <h2 className="text-2xl font-bold text-gray-800">Question Statistics</h2>
                                <button
                                    onClick={() => {
                                        fetchStatistics();
                                        fetchQuestions();
                                    }}
                                    disabled={isLoadingStats}
                                    className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    <svg 
                                        className={`w-5 h-5 ${isLoadingStats ? 'animate-spin' : ''}`} 
                                        fill="none" 
                                        stroke="currentColor" 
                                        viewBox="0 0 24 24"
                                    >
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                    </svg>
                                    {isLoadingStats ? 'Refreshing...' : 'Refresh'}
                                </button>
                            </div>

                            {/* Overall Statistics */}
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                                <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="text-blue-100 text-sm">Total Questions</p>
                                            <p className="text-3xl font-bold">{stats.totalQuestions}</p>
                                        </div>
                                        <svg className="w-12 h-12 opacity-50" fill="currentColor" viewBox="0 0 20 20">
                                            <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/>
                                            <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd"/>
                                        </svg>
                                    </div>
                                </div>

                                <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="text-green-100 text-sm">Active Questions</p>
                                            <p className="text-3xl font-bold">{stats.activeQuestions}</p>
                                        </div>
                                        <svg className="w-12 h-12 opacity-50" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                                        </svg>
                                    </div>
                                </div>

                                <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-xl shadow-lg p-6 text-white">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="text-red-100 text-sm">Inactive Questions</p>
                                            <p className="text-3xl font-bold">{stats.inactiveQuestions}</p>
                                        </div>
                                        <svg className="w-12 h-12 opacity-50" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M13.477 14.89A6 6 0 015.11 6.524l8.367 8.368zm1.414-1.414L6.524 5.11a6 6 0 018.367 8.367zM18 10a8 8 0 11-16 0 8 8 0 0116 0z" clipRule="evenodd"/>
                                        </svg>
                                    </div>
                                </div>

                                <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl shadow-lg p-6 text-white">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="text-orange-100 text-sm">Unknown Topics</p>
                                            <p className="text-3xl font-bold">{stats.unknownTopics}</p>
                                        </div>
                                        <svg className="w-12 h-12 opacity-50" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd"/>
                                        </svg>
                                    </div>
                                </div>
                            </div>

                            {/* Filters */}
                            <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
                                <h3 className="text-lg font-bold mb-4">Filters</h3>
                                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                    <select 
                                        value={filterSubject} 
                                        onChange={(e) => setFilterSubject(e.target.value)} 
                                        className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    >
                                        <option value="">All Subjects</option>
                                        {existingSubjects.map(s => (
                                            <option key={s.id} value={s.name}>{s.name}</option>
                                        ))}
                                    </select>
                                    <select 
                                        value={filterPaper} 
                                        onChange={(e) => setFilterPaper(e.target.value)} 
                                        className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                        disabled={!filterSubject}
                                    >
                                        <option value="">All Papers</option>
                                        {availablePapers.map(p => (
                                            <option key={p.id} value={p.name}>{p.name}</option>
                                        ))}
                                    </select>
                                    <select 
                                        value={filterTopic} 
                                        onChange={(e) => setFilterTopic(e.target.value)} 
                                        className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                        disabled={!filterPaper}
                                    >
                                        <option value="">All Topics</option>
                                        {availableTopics.map(t => (
                                            <option key={t.id} value={t.name}>{t.name}</option>
                                        ))}
                                    </select>
                                    <select 
                                        value={filterStatus} 
                                        onChange={(e) => setFilterStatus(e.target.value)} 
                                        className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    >
                                        <option value="all">All Status</option>
                                        <option value="active">Active Only</option>
                                        <option value="inactive">Inactive Only</option>
                                    </select>
                                </div>
                                <button 
                                    onClick={() => {
                                        setFilterSubject(''); 
                                        setFilterPaper(''); 
                                        setFilterTopic(''); 
                                        setFilterStatus('all');
                                        setFilterSubjectId('');
                                        setFilterPaperId('');
                                        setFilterTopicId('');
                                    }} 
                                    className="mt-4 text-blue-600 hover:text-blue-700 font-semibold transition"
                                >
                                    Clear Filters
                                </button>
                            </div>

                            {/* By Subject */}
                            <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
                                <h3 className="text-lg font-bold mb-4">Questions by Subject</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 h-96 overflow-y-auto">
                                    {Object.entries(stats.bySubject).map(([subject, counts]) => (
                                        <div key={subject} className="border-2 border-gray-200 rounded-lg p-4 hover:border-blue-500 transition bg-gradient-to-br from-blue-50 to-white">
                                            <div className="flex items-center justify-between mb-3">
                                                <h4 className="text-sm font-bold text-gray-700 truncate flex-1">{subject}</h4>
                                                <span className="text-2xl font-bold text-blue-600 ml-2">{counts.total}</span>
                                            </div>
                                            <div className="flex gap-4 text-xs">
                                                <div className="flex items-center">
                                                    <span className="w-2 h-2 bg-green-500 rounded-full mr-1"></span>
                                                    <span className="text-gray-600">Active: <span className="font-semibold">{counts.active}</span></span>
                                                </div>
                                                <div className="flex items-center">
                                                    <span className="w-2 h-2 bg-red-500 rounded-full mr-1"></span>
                                                    <span className="text-gray-600">Inactive: <span className="font-semibold">{counts.inactive}</span></span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                    {Object.keys(stats.bySubject).length === 0 && (
                                        <div className="col-span-full text-center py-8 text-gray-500">
                                            <p>No subjects found</p>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* By Paper */}
                            <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
                                <h3 className="text-lg font-bold mb-4">Questions by Paper</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    {Object.entries(stats.byPaper).map(([paperKey, counts]) => (
                                        <div key={paperKey} className="border-2 border-gray-200 rounded-lg p-4 hover:border-purple-500 transition bg-gradient-to-br from-purple-50 to-white">
                                            <div className="mb-2">
                                                <p className="text-xs text-gray-500 font-medium">{counts.subject}</p>
                                                <h4 className="text-sm font-bold text-gray-700">{counts.paper}</h4>
                                            </div>
                                            <div className="flex items-center justify-between mb-2">
                                                <span className="text-xs text-gray-600">Total Questions</span>
                                                <span className="text-xl font-bold text-purple-600">{counts.total}</span>
                                            </div>
                                            <div className="flex gap-4 text-xs">
                                                <div className="flex items-center">
                                                    <span className="w-2 h-2 bg-green-500 rounded-full mr-1"></span>
                                                    <span className="text-gray-600">Active: <span className="font-semibold">{counts.active}</span></span>
                                                </div>
                                                <div className="flex items-center">
                                                    <span className="w-2 h-2 bg-red-500 rounded-full mr-1"></span>
                                                    <span className="text-gray-600">Inactive: <span className="font-semibold">{counts.inactive}</span></span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                    {Object.keys(stats.byPaper).length === 0 && (
                                        <div className="col-span-full text-center py-8 text-gray-500">
                                            <p>No papers found</p>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* By Topic */}
                            <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
                                <h3 className="text-lg font-bold mb-4">Questions by Topic</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 h-96 overflow-y-auto">
                                    {Object.entries(stats.byTopic).map(([topic, counts]) => (
                                        <div key={topic} className="border-2 border-gray-200 rounded-lg p-4 hover:border-green-500 transition bg-gradient-to-br from-green-50 to-white">
                                            <h4 className="text-sm font-bold text-gray-700 truncate mb-3">{topic}</h4>
                                            <div className="flex items-center justify-between mb-3">
                                                <span className="text-xs text-gray-600">Total Questions</span>
                                                <span className="text-xl font-bold text-green-600">{counts.total}</span>
                                            </div>
                                            <div className="space-y-1 mb-3">
                                                <div className="flex justify-between text-xs">
                                                    <span className="text-gray-600">Active:</span>
                                                    <span className="font-semibold text-green-700">{counts.active}</span>
                                                </div>
                                                <div className="flex justify-between text-xs">
                                                    <span className="text-gray-600">Inactive:</span>
                                                    <span className="font-semibold text-red-700">{counts.inactive}</span>
                                                </div>
                                            </div>
                                            {/* Marks Breakdown */}
                                            {Object.keys(counts.byMarks || {}).length > 0 && (
                                                <div className="pt-3 border-t border-gray-200">
                                                    <p className="text-xs font-semibold text-gray-600 mb-2">By Marks:</p>
                                                    <div className="flex flex-wrap gap-1">
                                                        {Object.entries(counts.byMarks)
                                                            .sort(([a], [b]) => Number(a) - Number(b))
                                                            .map(([marks, count]) => (
                                                                <span key={marks} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-medium">
                                                                    {marks}m: {count}
                                                                </span>
                                                            ))}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                    {Object.keys(stats.byTopic).length === 0 && (
                                        <div className="col-span-full text-center py-8 text-gray-500">
                                            <p>No topics found</p>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Filtered Questions List */}
                            <div className="bg-white rounded-xl shadow-lg p-6">
                                <h3 className="text-lg font-bold mb-4">
                                    Questions List ({filteredQuestions.length})
                                    {isLoadingStats && <span className="ml-2 text-sm text-gray-500">Loading...</span>}
                                </h3>
                                {filteredQuestions.length === 0 ? (
                                    <div className="text-center py-8 text-gray-500">
                                        <p>No questions found</p>
                                        <p className="text-sm mt-2">Try adjusting your filters or add some questions</p>
                                    </div>
                                ) : (
                                    <div className="space-y-3 max-h-96 overflow-y-auto">
                                        {filteredQuestions.map(q => {
                                            // Use API field names (subject_name, paper_name, etc.)
                                            const subjectName = q.subject_name || q.subject?.name || 'Unknown Subject';
                                            const paperName = q.paper_name || q.paper?.name || 'Unknown Paper';
                                            const topicName = q.topic_name || q.topic?.name || 'Unknown';
                                            const sectionName = q.section_name || q.section?.name || 'No Section';
                                            const isActive = q.is_active !== false;
                                            
                                            return (
                                                <div key={q.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
                                                    <div className="flex justify-between items-start mb-2">
                                                        <div className="flex-1">
                                                            <span className={`inline-block px-2 py-1 rounded text-xs font-bold ${isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                                                {isActive ? 'Active' : 'Inactive'}
                                                            </span>
                                                            <span className="ml-2 text-sm font-semibold text-gray-700">
                                                                {subjectName} - {paperName}
                                                            </span>
                                                            {topicName === 'Unknown' && (
                                                                <span className="ml-2 text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded">
                                                                    Unknown Topic
                                                                </span>
                                                            )}
                                                        </div>
                                                        <span className="text-sm font-bold text-blue-600">{q.marks || 0} marks</span>
                                                    </div>
                                                    <p className="text-sm text-gray-600 line-clamp-2">{q.question_text || 'No question text'}</p>
                                                    <p className="text-xs text-gray-500 mt-1">
                                                        Topic: {topicName} | Section: {sectionName}
                                                    </p>
                                                </div>
                                            );
                                        })}
                                    </div>
                                )}
                            </div>
                        </div>
                    );
                })()}
            </div>
        </div>
    );
}