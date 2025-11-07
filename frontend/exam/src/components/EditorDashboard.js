import { useState, useEffect, useRef } from 'react';
import mammoth from 'mammoth';
import * as pdfjsLib from 'pdfjs-dist';
import * as subjectService from '../services/subjectService';
import * as questionService from '../services/questionService';
import * as authService from '../services/authService';

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
            // Fetch ALL questions for statistics cards
            fetchQuestions().then(questions => {
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
                    const response = await fetch('http://localhost:8000/api/questions/search-similar/', {
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
                question_inline_images: questionInlineImages,
                answer_inline_images: answerInlineImages,
                is_active: isQuestionActive
            };

            console.log('Submitting question to database:', questionData);

            // Get auth token from localStorage
            const token = localStorage.getItem('token');
            
            if (!token) {
                alert('You must be logged in to create questions');
                return;
            }

            // Send to database
            const response = await fetch('http://localhost:8000/api/questions', {
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
                setIsQuestionActive(true);
                setSimilarQuestions([]);
                
                alert('✅ Question saved to database successfully!');
                console.log('Question saved:', result);
            } else {
                console.error('Failed to save question:', result);
                alert(`❌ Failed to save question: ${result.message || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Error submitting question:', error);
            alert('❌ Error submitting question. Please check your connection and try again.');
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
        alert('✅ Answer drawing inserted!');
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
            alert('❌ Image not found!');
            return;
        }
        
        // Insert image placeholder at end of content
        const imagePlaceholder = `\n[IMAGE:${image.id}:${image.width}x${image.height}px]\n`;
        setText(prev => prev + imagePlaceholder);
        
        // Update image position
        setImages(prev => prev.map(img => 
            img.id === imageId ? { ...img, position: text.length } : img
        ));
        
        alert('✅ Image inserted!');
    };

    // Insert image directly with image object (for when state hasn't updated yet)
    const insertInlineImageDirect = (image, targetType = 'question') => {
        const setImages = targetType === 'question' ? setQuestionInlineImages : setAnswerInlineImages;
        const setText = targetType === 'question' ? setQuestionText : setAnswerText;
        const text = targetType === 'question' ? questionText : answerText;
        
        if (!image) {
            alert('❌ Image not found!');
            return;
        }
        
        // Insert image placeholder at end of content
        const imagePlaceholder = `\n[IMAGE:${image.id}:${image.width}x${image.height}px]\n`;
        setText(prev => prev + imagePlaceholder);
        
        // Update image position in state
        setImages(prev => prev.map(img => 
            img.id === image.id ? { ...img, position: text.length } : img
        ));
        
        alert('✅ Image inserted!');
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

    // Answer section handlers
    const scrollToSimilar = () => {
        const similarSection = document.getElementById('similar-questions-section');
        if (similarSection) {
            similarSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
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
        const stats = {
            totalQuestions: questionStats.totalQuestions,
            activeQuestions: questionStats.activeQuestions,
            inactiveQuestions: questionStats.inactiveQuestions,
            unknownTopics: questionStats.unknownTopics,
            bySubject: {},
            byPaper: {},
            byTopic: {}
        };

        // Use ALL questions for statistics cards (not filtered)
        const questions = Array.isArray(allQuestions) ? allQuestions : [];
        
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
                stats.byTopic[topicName] = { total: 0, active: 0, inactive: 0 };
            }
            stats.byTopic[topicName].total += 1;
            if (q.is_active !== false) {
                stats.byTopic[topicName].active += 1;
            } else {
                stats.byTopic[topicName].inactive += 1;
            }
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
            alert(`Subject "${newSubjectName}" added successfully!`);
            
            // Reset form
            setNewSubjectName('');
            setNewSubjectPapers([{ name: '', topics: [''], sections: [''] }]);
            
            // Refresh subjects list immediately
            await fetchSubjects();
            // Also refresh dynamic subjects for question entry dropdowns
            await loadDynamicSubjects();
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
    const handleEditSubject = (subject) => {
        setEditingItem({ type: 'subject', data: subject });
        setShowEditModal(true);
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
                    break;
                    
                case 'paper':
                    await subjectService.updatePaper(
                        editingItem.data.subject.id,
                        editingItem.data.paper.id,
                        { name: editingItem.data.paper.name }
                    );
                    break;
                    
                case 'topic':
                    await subjectService.updateTopic(editingItem.data.topic.id, {
                        name: editingItem.data.topic.name
                    });
                    break;
                    
                case 'section':
                    await subjectService.updateSection(editingItem.data.section.id, {
                        name: editingItem.data.section.name
                    });
                    break;
                    
                default:
                    break;
            }

            alert(`${editingItem.type.charAt(0).toUpperCase() + editingItem.type.slice(1)} updated successfully!`);
            setShowEditModal(false);
            setEditingItem(null);
            fetchSubjects();
            // Also refresh dynamic subjects for question entry dropdowns
            loadDynamicSubjects();
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
                    break;
                    
                case 'paper':
                    await subjectService.deletePaper(
                        deletingItem.data.subject.id,
                        deletingItem.data.paper.id
                    );
                    break;
                    
                case 'topic':
                    await subjectService.deleteTopic(deletingItem.data.topic.id);
                    break;
                    
                case 'section':
                    await subjectService.deleteSection(deletingItem.data.section.id);
                    break;
                    
                default:
                    break;
            }

            alert(`${deletingItem.type.charAt(0).toUpperCase() + deletingItem.type.slice(1)} deleted successfully!`);
            setShowDeleteConfirm(false);
            setDeletingItem(null);
            fetchSubjects();
            // Also refresh dynamic subjects for question entry dropdowns
            loadDynamicSubjects();
        } catch (error) {
            console.error('Error deleting:', error);
            alert(error.message || `Failed to delete ${deletingItem.type}. Please try again.`);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100">
            {/* Header */}
            <header className="bg-white shadow-md">
                <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
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
            <div className="max-w-7xl mx-auto px-4 pt-6 sm:px-6 lg:px-8">
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
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
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

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Question Entry Section */}
                    <div className="lg:col-span-2">
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
                                    </div>
                                </div>

                                {/* Unified Content Editor with Inline Images */}
                                <div className="relative border-2 border-gray-300 rounded-lg bg-white overflow-hidden">
                                    {/* Scrollable Display Area showing rendered content with images */}
                                    <div 
                                        className="p-4 overflow-y-auto" 
                                        style={{ 
                                            minHeight: '300px', 
                                            maxHeight: '500px',
                                            whiteSpace: 'pre-wrap',
                                            paddingBottom: '120px' // Space for fixed textarea
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
                                            const sourceIndex = parseInt(e.dataTransfer.getData('sourceIndex'));
                                            
                                            if (imageId) {
                                                // Find the image placeholder in text
                                                const parts = questionText.split(/(\[IMAGE:[\d.]+:(?:\d+x\d+|\d+)px\])/g);
                                                let imageIndex = -1;
                                                parts.forEach((part, idx) => {
                                                    if (part.includes(`[IMAGE:${imageId}:`)) {
                                                        imageIndex = idx;
                                                    }
                                                });
                                                
                                                if (imageIndex !== -1) {
                                                    // Remove from current position
                                                    const imagePlaceholder = parts[imageIndex];
                                                    parts.splice(imageIndex, 1);
                                                    
                                                    // Calculate drop position based on cursor
                                                    const dropTarget = document.elementFromPoint(e.clientX, e.clientY);
                                                    let insertIndex = 0;
                                                    
                                                    // Find nearest text span
                                                    if (dropTarget && dropTarget.closest('[data-text-index]')) {
                                                        insertIndex = parseInt(dropTarget.closest('[data-text-index]').dataset.textIndex) || 0;
                                                    }
                                                    
                                                    // Insert at new position
                                                    parts.splice(insertIndex, 0, imagePlaceholder);
                                                    
                                                    // Update text
                                                    setQuestionText(parts.join(''));
                                                }
                                            }
                                        }}
                                    >
                                        {questionText.split(/(\[IMAGE:[\d.]+:(?:\d+x\d+|\d+)px\])/g).map((part, index) => {
                                            const imageMatchNew = part.match(/\[IMAGE:([\d.]+):(\d+)x(\d+)px\]/);
                                            const imageMatchOld = part.match(/\[IMAGE:([\d.]+):(\d+)px\]/);
                                            
                                            if (imageMatchNew || imageMatchOld) {
                                                const imageId = parseFloat(imageMatchNew ? imageMatchNew[1] : imageMatchOld[1]);
                                                const imageWidth = parseInt(imageMatchNew ? imageMatchNew[2] : imageMatchOld[2]);
                                                const imageHeight = imageMatchNew ? parseInt(imageMatchNew[3]) : null;
                                                const image = questionInlineImages.find(img => Math.abs(img.id - imageId) < 0.001);
                                                
                                                if (image) {
                                                    return (
                                                        <span 
                                                            key={index} 
                                                            className="inline-block align-middle my-2 mx-1 relative"
                                                            draggable={true}
                                                            onDragStart={(e) => {
                                                                e.dataTransfer.setData('imageId', imageId.toString());
                                                                e.dataTransfer.setData('sourceIndex', index.toString());
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
                                    
                                    {/* Fixed Editable textarea at bottom */}
                                    <div className="sticky bottom-0 left-0 right-0 bg-white border-t-2 border-gray-300 shadow-lg">
                                        <textarea
                                            value={questionText}
                                            onChange={(e) => setQuestionText(e.target.value)}
                                            onDragOver={handleTextareaDragOver}
                                            onDrop={handleQuestionDrop}
                                            className="w-full px-4 py-3 focus:ring-2 focus:ring-green-500 focus:outline-none transition text-sm resize-none"
                                            rows="4"
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
                                </div>

                                {/* Question Preview in Answer Section */}
                                {questionText && (
                                    <div className="mb-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
                                        <p className="text-xs font-bold text-blue-800 mb-2">📝 QUESTION PREVIEW:</p>
                                        <div className="text-sm text-gray-700 whitespace-pre-wrap">
                                            {questionText.split(/(\[IMAGE:[\d.]+:(?:\d+x\d+|\d+)px\])/g).map((part, index) => {
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
                                <div className="relative border-2 border-gray-300 rounded-lg bg-white overflow-hidden">
                                    {/* Scrollable Display Area showing rendered content with images */}
                                    <div 
                                        className="p-4 overflow-y-auto" 
                                        style={{ 
                                            minHeight: '300px', 
                                            maxHeight: '500px',
                                            whiteSpace: 'pre-wrap',
                                            paddingBottom: '120px' // Space for fixed textarea
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
                                            const sourceIndex = parseInt(e.dataTransfer.getData('sourceIndex'));
                                            
                                            if (imageId) {
                                                // Find the image placeholder in text
                                                const parts = answerText.split(/(\[IMAGE:[\d.]+:(?:\d+x\d+|\d+)px\])/g);
                                                let imageIndex = -1;
                                                parts.forEach((part, idx) => {
                                                    if (part.includes(`[IMAGE:${imageId}:`)) {
                                                        imageIndex = idx;
                                                    }
                                                });
                                                
                                                if (imageIndex !== -1) {
                                                    // Remove from current position
                                                    const imagePlaceholder = parts[imageIndex];
                                                    parts.splice(imageIndex, 1);
                                                    
                                                    // Calculate drop position based on cursor
                                                    const dropTarget = document.elementFromPoint(e.clientX, e.clientY);
                                                    let insertIndex = 0;
                                                    
                                                    // Find nearest text span
                                                    if (dropTarget && dropTarget.closest('[data-text-index]')) {
                                                        insertIndex = parseInt(dropTarget.closest('[data-text-index]').dataset.textIndex) || 0;
                                                    }
                                                    
                                                    // Insert at new position
                                                    parts.splice(insertIndex, 0, imagePlaceholder);
                                                    
                                                    // Update text
                                                    setAnswerText(parts.join(''));
                                                }
                                            }
                                        }}
                                    >
                                        {answerText.split(/(\[IMAGE:[\d.]+:(?:\d+x\d+|\d+)px\])/g).map((part, index) => {
                                            const imageMatchNew = part.match(/\[IMAGE:([\d.]+):(\d+)x(\d+)px\]/);
                                            const imageMatchOld = part.match(/\[IMAGE:([\d.]+):(\d+)px\]/);
                                            
                                            if (imageMatchNew || imageMatchOld) {
                                                const imageId = parseFloat(imageMatchNew ? imageMatchNew[1] : imageMatchOld[1]);
                                                const imageWidth = parseInt(imageMatchNew ? imageMatchNew[2] : imageMatchOld[2]);
                                                const imageHeight = imageMatchNew ? parseInt(imageMatchNew[3]) : null;
                                                const image = answerInlineImages.find(img => Math.abs(img.id - imageId) < 0.001);
                                                
                                                if (image) {
                                                    return (
                                                        <span 
                                                            key={index} 
                                                            className="inline-block align-middle my-2 mx-1 relative"
                                                            draggable={true}
                                                            onDragStart={(e) => {
                                                                e.dataTransfer.setData('imageId', imageId.toString());
                                                                e.dataTransfer.setData('sourceIndex', index.toString());
                                                                e.dataTransfer.setData('targetType', 'answer');
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
                                    
                                    {/* Fixed Editable textarea at bottom */}
                                    <div className="sticky bottom-0 left-0 right-0 bg-white border-t-2 border-gray-300 shadow-lg">
                                        <textarea
                                            value={answerText}
                                            onChange={(e) => setAnswerText(e.target.value)}
                                            className="w-full px-4 py-3 focus:ring-2 focus:ring-orange-500 focus:outline-none transition text-sm resize-none"
                                            rows="4"
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
                                            <p className="text-sm text-gray-800 mb-3 leading-relaxed border-l-2 border-green-400 pl-3">
                                                {question.question_text || question.text}
                                            </p>
                                            
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
                        <div className="bg-white rounded-xl shadow-lg p-8">
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
                                                        onClick={() => handleEditSubject(subject)}
                                                        className="text-blue-600 hover:text-blue-700 p-2 hover:bg-blue-50 rounded transition"
                                                        title="Edit Subject"
                                                    >
                                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
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

                {/* Statistics Tab Content */}
                {activeTab === 'stats' && (() => {
                    const stats = getStatistics();
                    const filteredQuestions = getFilteredQuestions();
                    
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
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
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
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                                    {Object.entries(stats.byTopic).map(([topic, counts]) => (
                                        <div key={topic} className="border-2 border-gray-200 rounded-lg p-3 hover:border-green-500 transition bg-gradient-to-br from-green-50 to-white">
                                            <h4 className="text-xs font-bold text-gray-700 truncate mb-2">{topic}</h4>
                                            <div className="flex items-center justify-between mb-2">
                                                <span className="text-xs text-gray-600">Total</span>
                                                <span className="text-lg font-bold text-green-600">{counts.total}</span>
                                            </div>
                                            <div className="space-y-1">
                                                <div className="flex justify-between text-xs">
                                                    <span className="text-gray-600">Active:</span>
                                                    <span className="font-semibold text-green-700">{counts.active}</span>
                                                </div>
                                                <div className="flex justify-between text-xs">
                                                    <span className="text-gray-600">Inactive:</span>
                                                    <span className="font-semibold text-red-700">{counts.inactive}</span>
                                                </div>
                                            </div>
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
                                                                    ⚠️ Unknown Topic
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