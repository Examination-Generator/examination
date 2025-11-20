import React from 'react';
import { useState, useEffect, useRef } from 'react';
import { getTopicStatistics, generatePaper, listGeneratedPapers, viewFullPaper, getCoverpageData, updateCoverpageData, getAllSubjects } from '../services/paperService';
import { getCurrentUser, getAuthToken } from '../services/authService';

export default function PaperGenerationDashboard() {
    const [activeTab, setActiveTab] = useState('generate'); // 'generate' or 'history'
    
    // Subject and Paper filter states
    const [subjects, setSubjects] = useState([]);
    const [selectedSubject, setSelectedSubject] = useState('');
    const [papers, setPapers] = useState([]);
    const [selectedPaperId, setSelectedPaperId] = useState('');
    const [subjectsLoading, setSubjectsLoading] = useState(false);
    
    // Generate tab states
    const [topics, setTopics] = useState([]);
    const [selectedTopics, setSelectedTopics] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [generatedResult, setGeneratedResult] = useState(null);
    
    // History tab states
    const [generatedPapers, setGeneratedPapers] = useState([]);
    const [historyLoading, setHistoryLoading] = useState(false);
    const [selectedPaper, setSelectedPaper] = useState(null);
    const [viewingPaper, setViewingPaper] = useState(false);
    const [viewingCoverpage, setViewingCoverpage] = useState(false);
    const [coverpageData, setCoverpageData] = useState(null);
    const [coverpageLoading, setCoverpageLoading] = useState(false);
    
    // Coverpage editor states
    const [editableData, setEditableData] = useState({
        school_name: 'EXAMINATION CENTRE',
        school_logo: '/exam.png',
        logo_position: 'center',
        class_name: '',
        exam_title: 'END TERM 3 EXAMINATION 2025',
        paper_title: 'BIOLOGY PAPER 1',
        time_allocation: '2 hours',
        total_marks: 80,
        total_questions: 0,
        instructions: [
            'Write your name and index number in the spaces provided above.',
            'Sign and write the date of examination in the spaces provided above.',
            'Answer all the questions in this question paper.',
            'All answers must be written in the spaces provided.',
            'This paper consists of 9 printed pages.',
            'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
            'Candidates should answer the questions in English.'
        ]
    });
    const [previewMode, setPreviewMode] = useState(false);
    const [saving, setSaving] = useState(false);
    const [logoPreview, setLogoPreview] = useState(false);
    const [showFullExamModal, setShowFullExamModal] = useState(false);
    const [examModalView, setExamModalView] = useState('questions'); // 'questions' or 'marking_scheme'

    // Load subjects and topics on component mount
    useEffect(() => {
        loadSubjects();
        loadTopics();
    }, []);

    // Reload topics when selected paper changes
    useEffect(() => {
        if (selectedPaperId) {
            loadTopics();
            setSelectedTopics([]); // Reset selected topics when paper changes
        }
    }, [selectedPaperId]);

    // Load generated papers when switching to history tab
    useEffect(() => {
        if (activeTab === 'history') {
            loadGeneratedPapers();
        }
    }, [activeTab]);
    
    // Update editable data when coverpage data changes
    useEffect(() => {
        if (coverpageData) {
            const coverpage = coverpageData?.coverpage || coverpageData;
            setEditableData({
                school_name: coverpage?.school_name || 'EXAMINATION CENTRE',
                school_logo: coverpage?.school_logo || '/exam.png',
                logo_position: coverpage?.logo_position || 'center',
                class_name: coverpage?.class_name || '',
                exam_title: coverpage?.exam_title || 'END TERM 3 EXAMINATION 2025',
                paper_title: coverpage?.paper_title || 'BIOLOGY PAPER 1',
                time_allocation: coverpage?.time_allocation || '2 hours',
                total_marks: coverpage?.total_marks || 80,
                total_questions: coverpage?.total_questions || selectedPaper?.total_questions || 0,
                instructions: coverpage?.instructions || [
                    'Write your name and index number in the spaces provided above.',
                    'Sign and write the date of examination in the spaces provided above.',
                    'Answer all the questions in this question paper.',
                    'All answers must be written in the spaces provided.',
                    'This paper consists of 9 printed pages.',
                    'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
                    'Candidates should answer the questions in English.'
                ]
            });
            setLogoPreview(coverpage?.school_logo || '/exam.png');
        }
    }, [coverpageData, selectedPaper]);

    // ====== HELPER FUNCTION: RENDER TEXT WITH IMAGES ======
    const renderTextWithImages = (text, images = [], imagePositions = {}, context = 'preview') => {
        if (!text) return [];
        
        return text.split(/(\*\*.*?\*\*|\*.*?\*|__.*?__|_.*?_|\[IMAGE:[\d.]+:(?:\d+x\d+|\d+)px\]|\[LINES:[\d.]+\])/g).map((part, index) => {
            // Bold formatting
            if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
                return <strong key={index}>{part.slice(2, -2)}</strong>;
            }
            
            // Italic formatting
            if (part.startsWith('*') && part.endsWith('*') && !part.startsWith('**') && part.length > 2) {
                return <em key={index} className="italic">{part.slice(1, -1)}</em>;
            }
            
            // Underline formatting
            if (part.startsWith('__') && part.endsWith('__') && part.length > 4) {
                return <u key={index}>{part.slice(2, -2)}</u>;
            }
            
            // Single underscore italic
            if (part.startsWith('_') && part.endsWith('_') && !part.startsWith('__') && part.length > 2) {
                return <em key={index} className="italic">{part.slice(1, -1)}</em>;
            }
            
            // Answer lines (placeholder for visualization)
            const linesMatch = part.match(/\[LINES:([\d.]+)\]/);
            if (linesMatch) {
                return <span key={index} className="text-gray-400 italic text-sm">[Answer Lines]</span>;
            }
            
            // Images
            const imageMatchNew = part.match(/\[IMAGE:([\d.]+):(\d+)x(\d+)px\]/);
            const imageMatchOld = part.match(/\[IMAGE:([\d.]+):(\d+)px\]/);
            
            if (imageMatchNew || imageMatchOld) {
                const imageId = parseFloat(imageMatchNew ? imageMatchNew[1] : imageMatchOld[1]);
                const imageWidth = parseInt(imageMatchNew ? imageMatchNew[2] : imageMatchOld[2]);
                const imageHeight = imageMatchNew ? parseInt(imageMatchNew[3]) : null;
                const image = images.find(img => Math.abs(img.id - imageId) < 0.001);
                const position = imagePositions?.[imageId];
                
                if (image) {
                    return (
                        <span 
                            key={index} 
                            className={position ? "absolute z-10" : "inline-block align-middle my-2 mx-1"}
                            style={position ? { left: `${position.x}px`, top: `${position.y}px` } : {}}
                        >
                            <img 
                                src={image.url} 
                                alt={image.name || 'Question image'}
                                style={{ 
                                    width: `${imageWidth}px`, 
                                    height: imageHeight ? `${imageHeight}px` : 'auto',
                                    maxWidth: context === 'paper' ? '500px' : '100%',
                                    display: 'block'
                                }}
                                className="border-2 border-gray-300 rounded shadow-sm"
                            />
                        </span>
                    );
                }
                
                // If image not found, show placeholder
                return <span key={index} className="text-gray-400 italic text-sm">[Image {imageId}]</span>;
            }
            
            // Regular text
            return <span key={index}>{part}</span>;
        });
    };

    const loadSubjects = async () => {
        try {
            setSubjectsLoading(true);
            const response = await getAllSubjects();
            const subjectsData = response?.data || [];
            setSubjects(subjectsData);
            
            // Auto-select first available subject and paper
            if (subjectsData.length > 0) {
                const firstSubject = subjectsData[0];
                setSelectedSubject(firstSubject.id);
                setPapers(firstSubject.papers || []);
                
                // Auto-select first paper if available
                if (firstSubject.papers && firstSubject.papers.length > 0) {
                    setSelectedPaperId(firstSubject.papers[0].id);
                }
            }
        } catch (err) {
            console.error('Error loading subjects:', err);
        } finally {
            setSubjectsLoading(false);
        }
    };

    const loadTopics = async () => {
        if (!selectedPaperId) {
            setTopics([]);
            return;
        }
        
        try {
            setLoading(true);
            setError(null);
            const data = await getTopicStatistics(selectedPaperId);
            setTopics(Array.isArray(data?.topics) ? data.topics : []);
        } catch (err) {
            setError(err?.message || 'Failed to load topics');
            console.error('Error loading topics:', err);
        } finally {
            setLoading(false);
        }
    };

    const loadGeneratedPapers = async () => {
        try {
            setHistoryLoading(true);
            const user = getCurrentUser();
            const data = await listGeneratedPapers({
                paperId: selectedPaperId,
                userId: user?.id,
                userOnly: true  // Only show current user's papers
            });
            setGeneratedPapers(Array.isArray(data?.generated_papers) ? data.generated_papers : []);
        } catch (err) {
            console.error('Failed to load generated papers:', err);
            setGeneratedPapers([]);
        } finally {
            setHistoryLoading(false);
        }
    };

    const handleSubjectChange = (e) => {
        const subjectId = e.target.value;
        setSelectedSubject(subjectId);
        
        // Find the selected subject and update papers
        const subject = subjects.find(s => s.id === subjectId);
        if (subject) {
            setPapers(subject.papers || []);
            // Auto-select first paper if available
            if (subject.papers && subject.papers.length > 0) {
                setSelectedPaperId(subject.papers[0].id);
            } else {
                setSelectedPaperId('');
            }
        } else {
            setPapers([]);
            setSelectedPaperId('');
        }
        
        // Reset selected topics
        setSelectedTopics([]);
    };

    const handlePaperChange = (e) => {
        const paperId = e.target.value;
        setSelectedPaperId(paperId);
        setSelectedTopics([]); // Reset selected topics when paper changes
    };

    const handleTopicToggle = (topicId) => {
        if (selectedTopics.includes(topicId)) {
            setSelectedTopics(selectedTopics.filter(id => id !== topicId));
        } else {
            setSelectedTopics([...selectedTopics, topicId]);
        }
    };

    const handleSelectAll = () => {
        if (selectedTopics.length === topics.length) {
            setSelectedTopics([]);
        } else {
            setSelectedTopics(topics.map(t => t.id));
        }
    };

    const handleGeneratePaper = async () => {
        if (selectedTopics.length === 0) {
            setError('Please select at least one topic');
            return;
        }

        if (!selectedPaperId) {
            setError('Please select a paper first');
            return;
        }

        // Check if enough topics selected
        if (selectedTopics.length < 5) {
            const confirmed = window.confirm(
                `You have selected only ${selectedTopics.length} topic(s). ` +
                `For best results and to meet best constraints, we recommend selecting at least 5 topics. ` +
                `\n\nDo you want to continue anyway?`
            );
            if (!confirmed) {
                return;
            }
        }

        try {
            setLoading(true);
            setError(null);
            setSuccess(null);
            setGeneratedResult(null);

            const result = await generatePaper(selectedPaperId, selectedTopics);
            
            console.log('Generation result:', result); // Debug log
            
            setGeneratedResult(result);
            
            // Extract the unique code from the result
            const paperCode = result?.generated_paper?.unique_code || result?.unique_code || 'N/A';
            setSuccess(`Paper generated successfully! Code: ${paperCode}`);
            
            // Clear selections
            setSelectedTopics([]);
        } catch (err) {
            const errorMessage = err?.message || 'Failed to generate paper';
            
            // Provide helpful error message
            if (errorMessage.includes('Failed to generate valid paper after')) {
                setError(
                    'Unable to generate a valid paper with the selected topics. ' +
                    'This usually means there aren\'t enough questions available to meet KCSE constraints. ' +
                    '\n\nTry selecting MORE topics (recommend all 6 topics) or add more questions to the database.'
                );
            } else {
                setError(errorMessage);
            }
        } finally {
            setLoading(false);
        }
    };

    const handleViewPaper = async (paperId) => {
        // Validate paper ID
        if (!paperId) {
            setError('Invalid paper ID');
            console.error('Paper ID is undefined or null');
            return;
        }

        try {
            setLoading(true);
            setError(null);
            console.log('📄 Loading coverpage for paper ID:', paperId);
            
            // First, get the paper details to store in selectedPaper
            const paperDetails = await viewFullPaper(paperId);
            console.log('✅ Paper details loaded:', paperDetails);
            setSelectedPaper(paperDetails);
            
            // Then, load coverpage data and go directly to coverpage editor
            setCoverpageLoading(true);
            console.log('📡 Fetching coverpage data...');
            const data = await getCoverpageData(paperId);
            console.log('✅ Coverpage data received:', data);
            setCoverpageData(data);
            
            // Go directly to coverpage editor (skip full paper view)
            setViewingCoverpage(true);
            setViewingPaper(false);
        } catch (err) {
            console.error('❌ Error loading paper/coverpage:', err);
            setError(err.message || 'Failed to load paper details');
        } finally {
            setLoading(false);
            setCoverpageLoading(false);
        }
    };

    const handleCloseViewer = () => {
        setViewingPaper(false);
        setViewingCoverpage(false);
        setSelectedPaper(null);
        setCoverpageData(null);
    };

    const handleProceedToCoverpage = async () => {
        console.log('🎯 Proceed to Coverpage clicked!', selectedPaper);
        try {
            setCoverpageLoading(true);
            setError(null);
            
            // Get the paper ID from selectedPaper
            const paperId = selectedPaper?.id || selectedPaper?.generated_paper?.id;
            console.log('📄 Paper ID:', paperId);
            
            if (!paperId) {
                throw new Error('Invalid paper ID');
            }
            
            // Fetch coverpage data
            console.log('📡 Fetching coverpage data...');
            const data = await getCoverpageData(paperId);
            console.log('✅ Coverpage data received:', data);
            setCoverpageData(data);
            setViewingPaper(false);
            setViewingCoverpage(true);
        } catch (err) {
            console.error('❌ Error loading coverpage:', err);
            setError(err.message || 'Failed to load coverpage');
        } finally {
            setCoverpageLoading(false);
        }
    };

    const getTopicById = (topicId) => {
        return topics.find(t => t?.id === topicId) || { name: 'Unknown Topic' };
    };

    // Render coverpage editor
    if (viewingCoverpage && coverpageData) {
        const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
        const paperId = selectedPaper?.id || selectedPaper?.generated_paper?.id;
        const coverpageHtmlUrl = `${API_BASE_URL}/papers/generated/${paperId}/coverpage/?output=html`;
        
        const handleSaveCoverpage = async () => {
            try {
                setSaving(true);
                setError(null);
                
                console.log('📤 Saving coverpage data:', editableData);
                await updateCoverpageData(paperId, editableData);
                setSuccess('Coverpage updated successfully!');
                
                // Refresh coverpage data from backend
                const updatedData = await getCoverpageData(paperId);
                console.log('📥 Received updated data:', updatedData);
                setCoverpageData(updatedData);
                
                // Small delay to ensure backend has processed the update
                await new Promise(resolve => setTimeout(resolve, 500));
                
                // Force refresh the iframe preview with cache busting
                const iframe = document.getElementById('coverpage-iframe');
                if (iframe) {
                    delete iframe.dataset.loaded;
                    // Add timestamp to prevent caching
                    const cacheBustUrl = `${coverpageHtmlUrl}&t=${Date.now()}`;
                    console.log('🔄 Fetching preview from:', cacheBustUrl);
                    
                    fetch(cacheBustUrl, {
                        method: 'GET',
                        headers: {
                            'Authorization': `Bearer ${getAuthToken()}`
                        }
                    })
                    .then(response => {
                        console.log('📡 Preview response status:', response.status);
                        return response.text();
                    })
                    .then(html => {
                        console.log('📄 Received HTML length:', html.length);
                        const doc = iframe.contentDocument || iframe.contentWindow.document;
                        doc.open();
                        doc.write(html);
                        doc.close();
                        iframe.dataset.loaded = 'true';
                        console.log('✅ Preview refreshed successfully');
                    })
                    .catch(err => {
                        console.error('❌ Error refreshing preview:', err);
                        setError('Failed to refresh preview. Please use the Refresh button.');
                    });
                }
            } catch (err) {
                console.error('Error saving coverpage:', err);
                setError(err.message || 'Failed to save coverpage');
            } finally {
                setSaving(false);
            }
        };
        
        return (
            <div className="min-h-screen bg-gray-50 p-4">
                <div className="max-w-7xl mx-auto">
                    {/* Header */}
                    <div className="bg-white rounded-lg shadow-md p-4 mb-4">
                        <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-3">
                            <div>
                                <h2 className="text-2xl font-bold text-gray-800">
                                    Coverpage Customization - {selectedPaper?.unique_code || 'N/A'}
                                </h2>
                                <p className="text-sm text-gray-600">
                                    Customize your exam coverpage with school details and instructions
                                </p>
                            </div>
                            <div className="flex flex-col sm:flex-row gap-2 w-full md:w-auto">
                                <button
                                    onClick={() => setPreviewMode(!previewMode)}
                                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition"
                                >
                                    {previewMode ? '✏️ Edit' : '👁️ Preview'}
                                </button>
                                <button
                                    onClick={handleCloseViewer}
                                    className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition"
                                >
                                    ← Back to Dashboard
                                </button>
                            </div>
                        </div>
                    </div>

                    {error && (
                        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-4">
                            {error}
                        </div>
                    )}
                    
                    {success && (
                        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg mb-4">
                            {success}
                        </div>
                    )}

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                        {/* Left Column - Edit Form */}
                        {!previewMode && (
                            <div className="bg-white rounded-lg shadow-md p-6">
                                <h3 className="text-lg font-bold text-gray-800 mb-4">📝 Coverpage Details</h3>
                                
                                {/* School Information */}
                                <div className="mb-4 sm:mb-6">
                                    <h4 className="font-semibold text-gray-700 mb-3">School Information</h4>
                                    <div className="space-y-3">
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                                School Name
                                            </label>
                                            <input
                                                type="text"
                                                value={editableData.school_name}
                                                onChange={(e) => setEditableData({...editableData, school_name: e.target.value})}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                placeholder="e.g., KENYA HIGH SCHOOL or leave as EXAMINATION CENTRE"
                                            />
                                            <p className="text-xs text-gray-500 mt-1">Default: EXAMINATION CENTRE</p>
                                        </div>
                                        
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                                Class/Form
                                            </label>
                                            <input
                                                type="text"
                                                value={editableData.class_name}
                                                onChange={(e) => setEditableData({...editableData, class_name: e.target.value})}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                placeholder="e.g., FORM 4"
                                            />
                                        </div>
                                        
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                                School Logo
                                            </label>
                                            <div className="space-y-2">
                                                <input
                                                    type="file"
                                                    accept="image/*"
                                                    onChange={(e) => {
                                                        const file = e.target.files[0];
                                                        if (file) {
                                                            const reader = new FileReader();
                                                            reader.onloadend = () => {
                                                                setEditableData({...editableData, school_logo: reader.result});
                                                                setLogoPreview(reader.result);
                                                            };
                                                            reader.readAsDataURL(file);
                                                        }
                                                    }}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                                                />
                                                {logoPreview && (
                                                    <div className="flex items-center gap-2">
                                                        <img src={logoPreview} alt="Logo preview" className="w-16 h-16 object-contain border rounded" />
                                                        <button
                                                            type="button"
                                                            onClick={() => {
                                                                setEditableData({...editableData, school_logo: '/exam.png'});
                                                                setLogoPreview('/exam.png');
                                                            }}
                                                            className="text-xs text-red-600 hover:text-red-700"
                                                        >
                                                            Reset to default
                                                        </button>
                                                    </div>
                                                )}
                                                <p className="text-xs text-gray-500">Default logo: /exam.png</p>
                                            </div>
                                        </div>
                                        
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                                Logo Position
                                            </label>
                                            <div className="flex gap-2">
                                                {['left', 'center', 'right'].map((position) => (
                                                    <button
                                                        key={position}
                                                        type="button"
                                                        onClick={() => setEditableData({...editableData, logo_position: position})}
                                                        className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition ${
                                                            editableData.logo_position === position
                                                                ? 'bg-blue-600 text-white'
                                                                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                                        }`}
                                                    >
                                                        {position.charAt(0).toUpperCase() + position.slice(1)}
                                                    </button>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Exam Information */}
                                <div className="mb-4 sm:mb-6">
                                    <h4 className="font-semibold text-gray-700 mb-3">Exam Information</h4>
                                    <div className="space-y-3">
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                                Exam Title
                                            </label>
                                            <input
                                                type="text"
                                                value={editableData.exam_title}
                                                onChange={(e) => setEditableData({...editableData, exam_title: e.target.value})}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                placeholder="e.g., END TERM 3 EXAMINATION 2025"
                                            />
                                        </div>
                                        
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                                Paper Title
                                            </label>
                                            <input
                                                type="text"
                                                value={editableData.paper_title}
                                                onChange={(e) => setEditableData({...editableData, paper_title: e.target.value})}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                placeholder="e.g., BIOLOGY PAPER 1"
                                            />
                                        </div>
                                        
                                        <div className="grid grid-cols-3 gap-3">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Time (HOURS)
                                                </label>
                                                <input
                                                    type="text"
                                                    value={editableData.time_allocation}
                                                    disabled
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Total Marks
                                                </label>
                                                <input
                                                    type="number"
                                                    value={editableData.total_marks}
                                                    disabled
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Questions
                                                </label>
                                                <input
                                                    type="number"
                                                    value={editableData.total_questions}
                                                    disabled
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100"
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Instructions */}
                                <div className="mb-4 sm:mb-6">
                                    <h4 className="font-semibold text-gray-700 mb-3">Instructions to Candidates</h4>
                                    <div className="space-y-2">
                                        {editableData.instructions.map((instruction, idx) => (
                                            <div key={idx} className="flex gap-2">
                                                <span className="text-sm text-gray-600 mt-2">{String.fromCharCode(97 + idx)})</span>
                                                <input
                                                    type="text"
                                                    value={instruction}
                                                    onChange={(e) => {
                                                        const newInstructions = [...editableData.instructions];
                                                        newInstructions[idx] = e.target.value;
                                                        setEditableData({...editableData, instructions: newInstructions});
                                                    }}
                                                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                                                />
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Save Button */}
                                <button
                                    onClick={handleSaveCoverpage}
                                    disabled={saving}
                                    className="w-full bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white font-semibold py-3 px-6 rounded-lg transition"
                                >
                                    {saving ? '💾 Saving...' : '💾 Save Coverpage'}
                                </button>
                            </div>
                        )}

                        {/* Right Column - Preview */}
                        <div className={`bg-white rounded-lg shadow-md p-4 ${previewMode ? 'lg:col-span-2' : ''}`}>
                            <div className="flex justify-between items-center mb-4">
                                <h3 className="text-lg font-bold text-gray-800">📄 Coverpage Preview</h3>
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => setShowFullExamModal(true)}
                                        className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition text-sm"
                                    >
                                        📋 Preview Full Exam
                                    </button>
                                    <button
                                        onClick={() => {
                                            const iframe = document.getElementById('coverpage-iframe');
                                            if (iframe && iframe.contentWindow) {
                                                iframe.contentWindow.print();
                                            }
                                        }}
                                        className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition text-sm"
                                    >
                                        🖨️ Print
                                    </button>
                                </div>
                            </div>
                            
                            {/* iframe for HTML preview */}
                            <div className="border-2 border-gray-300 rounded-lg overflow-hidden bg-white" style={{ height: previewMode ? '900px' : '700px' }}>
                                <div className="bg-gray-100 p-2 border-b flex justify-between items-center">
                                    <span className="text-xs text-gray-600">Live Preview (Save changes to update)</span>
                                    <button
                                        onClick={() => {
                                            const iframe = document.getElementById('coverpage-iframe');
                                            if (iframe) {
                                                // Clear loaded flag and reload
                                                delete iframe.dataset.loaded;
                                                // Fetch HTML with authentication
                                                fetch(coverpageHtmlUrl, {
                                                    method: 'GET',
                                                    headers: {
                                                        'Authorization': `Bearer ${getAuthToken()}`
                                                    }
                                                })
                                                .then(response => response.text())
                                                .then(html => {
                                                    const doc = iframe.contentDocument || iframe.contentWindow.document;
                                                    doc.open();
                                                    doc.write(html);
                                                    doc.close();
                                                    iframe.dataset.loaded = 'true';
                                                })
                                                .catch(err => {
                                                    console.error('Error refreshing coverpage:', err);
                                                });
                                            }
                                        }}
                                        className="text-xs bg-gray-200 hover:bg-gray-300 px-2 py-1 rounded"
                                    >
                                        🔄 Refresh
                                    </button>
                                </div>
                                <iframe
                                    id="coverpage-iframe"
                                    className="w-full"
                                    title="Coverpage Preview"
                                    style={{ border: 'none', height: 'calc(100% - 40px)' }}
                                    sandbox="allow-same-origin allow-scripts allow-popups"
                                    ref={(iframe) => {
                                        if (iframe && !iframe.dataset.loaded) {
                                            iframe.dataset.loaded = 'true';
                                            // Fetch HTML with authentication
                                            fetch(coverpageHtmlUrl, {
                                                method: 'GET',
                                                headers: {
                                                    'Authorization': `Bearer ${getAuthToken()}`
                                                }
                                            })
                                            .then(response => response.text())
                                            .then(html => {
                                                const doc = iframe.contentDocument || iframe.contentWindow.document;
                                                doc.open();
                                                doc.write(html);
                                                doc.close();
                                            })
                                            .catch(err => {
                                                console.error('Error loading coverpage:', err);
                                                const doc = iframe.contentDocument || iframe.contentWindow.document;
                                                doc.open();
                                                doc.write(`<div style="padding: 20px; color: red;">Error loading coverpage: ${err.message}</div>`);
                                                doc.close();
                                            });
                                        }
                                    }}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="mt-6 flex gap-4">
                        <button
                            onClick={() => {
                                setViewingCoverpage(false);
                                setViewingPaper(true);
                            }}
                            className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-3 px-6 rounded-lg transition"
                        >
                            ← Back to Questions
                        </button>
                        <button
                            onClick={handleCloseViewer}
                            className="flex-1 bg-gray-500 hover:bg-gray-600 text-white font-semibold py-3 px-6 rounded-lg transition"
                        >
                            Close and Return to Dashboard
                        </button>
                    </div>
                    
                    {/* Full Exam Preview Modal */}
                    {showFullExamModal && (
                        <div 
                            className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-2 sm:p-4"
                            onClick={() => setShowFullExamModal(false)}
                        >
                            <div 
                                className="bg-white rounded-lg shadow-2xl w-full max-w-6xl h-[95vh] sm:h-[90vh] flex flex-col"
                                onClick={(e) => e.stopPropagation()}
                            >
                                {/* Modal Header */}
                                <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-3 p-3 sm:p-4 border-b">
                                    <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 items-start sm:items-center">
                                        <h3 className="text-lg sm:text-xl font-bold text-gray-800">📋 Full Exam Preview</h3>
                                        <div className="flex gap-1 sm:gap-2 bg-gray-100 rounded-lg p-1 w-full sm:w-auto">
                                            <button
                                                onClick={() => setExamModalView('questions')}
                                                className={`flex-1 sm:flex-none px-3 sm:px-4 py-2 rounded-lg font-medium text-sm sm:text-base transition ${
                                                    examModalView === 'questions'
                                                        ? 'bg-blue-600 text-white'
                                                        : 'text-gray-600 hover:bg-gray-200'
                                                }`}
                                            >
                                                📝 Questions
                                            </button>
                                            <button
                                                onClick={() => setExamModalView('marking_scheme')}
                                                className={`flex-1 sm:flex-none px-3 sm:px-4 py-2 rounded-lg font-medium text-sm sm:text-base transition ${
                                                    examModalView === 'marking_scheme'
                                                        ? 'bg-green-600 text-white'
                                                        : 'text-gray-600 hover:bg-gray-200'
                                                }`}
                                            >
                                                ✓ Marking Scheme
                                            </button>
                                        </div>
                                    </div>
                                    <div className="flex gap-2 w-full md:w-auto">
                                        <button
                                            onClick={() => {
                                                const iframe = document.getElementById('full-exam-iframe');
                                                if (iframe && iframe.contentWindow) {
                                                    iframe.contentWindow.print();
                                                }
                                            }}
                                            className="flex-1 md:flex-none bg-purple-600 hover:bg-purple-700 text-white px-3 sm:px-4 py-2 rounded-lg transition text-sm"
                                        >
                                            🖨️ Print
                                        </button>
                                        <button
                                            onClick={() => {
                                                setShowFullExamModal(false);
                                                setExamModalView('questions'); // Reset to questions view
                                            }}
                                            className="flex-1 md:flex-none bg-red-600 hover:bg-red-700 text-white px-3 sm:px-4 py-2 rounded-lg transition text-sm"
                                        >
                                            ✕ Close
                                        </button>
                                    </div>
                                </div>
                                
                                {/* Modal Body - Iframe */}
                                <div className="flex-1 overflow-hidden">
                                    <iframe
                                        id="full-exam-iframe"
                                        key={examModalView} // Force re-render when view changes
                                        className="w-full h-full"
                                        title={examModalView === 'questions' ? 'Questions Preview' : 'Marking Scheme Preview'}
                                        style={{ border: 'none' }}
                                        sandbox="allow-same-origin allow-scripts allow-popups allow-popups-to-escape-sandbox"
                                        ref={(iframe) => {
                                            if (iframe && !iframe.dataset.loaded) {
                                                iframe.dataset.loaded = 'true';
                                                const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
                                                const viewParam = examModalView === 'marking_scheme' ? '&view=marking_scheme' : '';
                                                const fullExamUrl = `${API_BASE_URL}/papers/generated/${paperId}/preview/?output=html${viewParam}`;
                                                
                                                // Fetch HTML with authentication
                                                fetch(fullExamUrl, {
                                                    method: 'GET',
                                                    headers: {
                                                        'Authorization': `Bearer ${getAuthToken()}`
                                                    }
                                                })
                                                .then(response => response.text())
                                                .then(html => {
                                                    const doc = iframe.contentDocument || iframe.contentWindow.document;
                                                    doc.open();
                                                    doc.write(html);
                                                    doc.close();
                                                })
                                                .catch(err => {
                                                    console.error('Error loading full exam:', err);
                                                    const doc = iframe.contentDocument || iframe.contentWindow.document;
                                                    doc.open();
                                                    doc.write(`<div style="padding: 20px; color: red;">Error loading content: ${err.message}</div>`);
                                                    doc.close();
                                                });
                                            }
                                        }}
                                    />
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        );
    }

    // Render paper viewer
    if (viewingPaper && selectedPaper) {
        return (
            <div className="min-h-screen bg-gray-50 p-4">
                <div className="max-w-5xl mx-auto">
                    {/* Header */}
                    <div className="bg-white rounded-lg shadow-md p-4 mb-4">
                        <div className="flex justify-between items-center">
                            <div>
                                <h2 className="text-2xl font-bold text-gray-800">
                                    {selectedPaper?.paper?.subject_name || 'Biology'} {selectedPaper?.paper?.name || 'Paper 1'} - {selectedPaper?.unique_code || 'N/A'}
                                </h2>
                                <p className="text-sm text-gray-600">
                                    Generated on {selectedPaper?.created_at ? new Date(selectedPaper.created_at).toLocaleDateString() : 'Unknown'}
                                </p>
                            </div>
                            <button
                                onClick={handleCloseViewer}
                                className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition"
                            >
                                ← Back
                            </button>
                        </div>
                    </div>

                    {/* Paper Details */}
                    <div className="bg-white rounded-lg shadow-md p-6 mb-4">
                        <h3 className="text-xl font-bold mb-4">Paper Information</h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <p className="text-sm text-gray-600">Total Questions</p>
                                <p className="text-lg font-semibold">{selectedPaper?.statistics?.total_questions || selectedPaper?.questions?.length || 0}</p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-600">Total Marks</p>
                                <p className="text-lg font-semibold">{selectedPaper?.statistics?.total_marks || selectedPaper?.total_marks || 0}</p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-600">Nested Questions</p>
                                <p className="text-lg font-semibold">{selectedPaper?.statistics?.nested_count || 0}</p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-600">Standalone Questions</p>
                                <p className="text-lg font-semibold">{selectedPaper?.statistics?.standalone_count || 0}</p>
                            </div>
                        </div>
                    </div>

                    {/* Mark Distribution */}
                    {selectedPaper?.statistics?.mark_distribution && Object.keys(selectedPaper.statistics.mark_distribution).length > 0 && (
                        <div className="bg-white rounded-lg shadow-md p-6 mb-4">
                            <h3 className="text-xl font-bold mb-4">Mark Distribution</h3>
                            <div className="grid grid-cols-4 gap-4">
                                {Object.entries(selectedPaper.statistics.mark_distribution).map(([marks, count]) => (
                                    <div key={marks} className="text-center p-4 bg-blue-50 rounded-lg">
                                        <p className="text-sm text-gray-600">{marks}-Mark Questions</p>
                                        <p className="text-2xl font-bold text-blue-600">{count}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Questions */}
                    <div className="bg-white rounded-lg shadow-md p-6">
                        <h3 className="text-xl font-bold mb-4">Questions (Preview - No Answers)</h3>
                        <div className="space-y-6">
                            {selectedPaper?.questions?.map((question, index) => (
                                <div key={question?.id || index} className="border-b pb-4">
                                    <div className="flex justify-between items-start mb-2">
                                        <p className="font-bold text-lg">Question {question?.question_number || index + 1}</p>
                                        <div className="text-right">
                                            <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold">
                                                {question?.marks || 0} marks
                                            </span>
                                            {question?.is_nested && (
                                                <span className="ml-2 bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-xs font-semibold">
                                                    Nested
                                                </span>
                                            )}
                                            <p className="text-xs text-gray-500 mt-1">{question?.kcse_question_type || 'N/A'}</p>
                                        </div>
                                    </div>
                                    <div className="text-gray-800 mb-2 whitespace-pre-wrap">
                                        {renderTextWithImages(
                                            question?.question_text || 'No question text',
                                            question?.question_inline_images || [],
                                            question?.question_image_positions || {},
                                            'paper'
                                        )}
                                    </div>
                                    <p className="text-sm text-gray-600">
                                        <strong>Topic:</strong> {question?.topic?.name || 'Unknown'}
                                    </p>
                                </div>
                            ))}
                        </div>
                        
                        {/* Action Buttons */}
                        <div className="mt-6 flex gap-4">
                            <button
                                onClick={handleProceedToCoverpage}
                                disabled={coverpageLoading}
                                className="flex-1 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-semibold py-3 px-6 rounded-lg transition"
                            >
                                {coverpageLoading ? 'Loading...' : 'Proceed to Coverpage'}
                            </button>
                            <button
                                onClick={handleCloseViewer}
                                className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-3 px-6 rounded-lg transition"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-2 sm:p-4">
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <div className="bg-white rounded-lg shadow-md p-4 sm:p-6 mb-6">
                    <h1 className="text-2xl sm:text-3xl font-bold text-gray-800 mb-2">
                        Exam Generator
                    </h1>
                    <p className="text-gray-600">
                        Generate exam papers with automatic question selection and validation
                    </p>
                </div>

                {/* Subject and Paper Filter */}
                <div className="bg-white rounded-lg shadow-md p-4 sm:p-6 mb-6">
                    <h2 className="text-xl font-bold text-gray-800 mb-4">📚 Select Subject & Paper</h2>
                    
                    {subjectsLoading ? (
                        <div className="text-center py-4">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                            <p className="mt-2 text-gray-600">Loading subjects...</p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* Subject Dropdown */}
                            <div>
                                <label className="block text-sm font-semibold text-gray-700 mb-2">
                                    Subject
                                </label>
                                <select
                                    value={selectedSubject}
                                    onChange={handleSubjectChange}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                >
                                    <option value="">-- Select Subject --</option>
                                    {subjects.map(subject => (
                                        <option key={subject.id} value={subject.id}>
                                            {subject.name}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {/* Paper Dropdown */}
                            <div>
                                <label className="block text-sm font-semibold text-gray-700 mb-2">
                                    Paper
                                </label>
                                <select
                                    value={selectedPaperId}
                                    onChange={handlePaperChange}
                                    disabled={!selectedSubject || papers.length === 0}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
                                >
                                    <option value="">-- Select Paper --</option>
                                    {papers.map(paper => (
                                        <option key={paper.id} value={paper.id}>
                                            {paper.name}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>
                    )}
                    
                    {selectedSubject && papers.length === 0 && !subjectsLoading && (
                        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                            <p className="text-yellow-800">
                                ⚠️ No papers available for this subject yet.
                            </p>
                        </div>
                    )}
                </div>

                {/* Tabs */}
                <div className="bg-white rounded-lg shadow-md mb-6">
                    <div className="flex border-b">
                        <button
                            onClick={() => setActiveTab('generate')}
                            className={`flex-1 py-4 px-6 font-semibold transition ${
                                activeTab === 'generate'
                                    ? 'border-b-2 border-blue-600 text-blue-600'
                                    : 'text-gray-600 hover:text-gray-800'
                            }`}
                        >
                            Generate New Paper
                        </button>
                        <button
                            onClick={() => setActiveTab('history')}
                            className={`flex-1 py-4 px-6 font-semibold transition ${
                                activeTab === 'history'
                                    ? 'border-b-2 border-blue-600 text-blue-600'
                                    : 'text-gray-600 hover:text-gray-800'
                            }`}
                        >
                            Generated Papers
                        </button>
                    </div>
                </div>

                {/* Error/Success Messages */}
                {error && (
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
                        <p className="font-semibold">Error</p>
                        <p>{error}</p>
                    </div>
                )}

                {success && (
                    <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-4">
                        <p className="font-semibold">Success</p>
                        <p>{success}</p>
                    </div>
                )}

                {/* Generate Tab */}
                {activeTab === 'generate' && (
                    <div className="bg-white rounded-lg shadow-md p-4 sm:p-6">
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-xl sm:text-2xl font-bold text-gray-800">Select Topics</h2>
                            <button
                                onClick={handleSelectAll}
                                className="text-blue-600 hover:text-blue-700 font-semibold"
                            >
                                {selectedTopics.length === topics.length ? 'Deselect All' : 'Select All'}
                            </button>
                        </div>

                        {loading && topics.length === 0 ? (
                            <div className="text-center py-12">
                                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                                <p className="mt-4 text-gray-600">Loading topics...</p>
                            </div>
                        ) : (
                            <>
                                {/* Topics Grid */}
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                                    {topics.map((topic) => (
                                        <label
                                            key={topic?.id || Math.random()}
                                            className={`flex items-start p-4 border-2 rounded-lg cursor-pointer transition ${
                                                selectedTopics.includes(topic?.id)
                                                    ? 'border-blue-500 bg-blue-50'
                                                    : 'border-gray-300 hover:border-blue-300'
                                            }`}
                                        >
                                            <input
                                                type="checkbox"
                                                checked={selectedTopics.includes(topic?.id)}
                                                onChange={() => handleTopicToggle(topic?.id)}
                                                className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500 mt-1"
                                            />
                                            <div className="ml-3 flex-1">
                                                <p className="font-semibold text-gray-800">{topic?.name || 'Unknown Topic'}</p>
                                                <div className="mt-2">
                                                    <p className="text-xs text-gray-500">
                                                        Total questions: {topic?.total_questions || 0}
                                                    </p>
                                                    {topic?.total_questions === 0 && (
                                                        <span className="text-xs text-gray-400 italic">No questions available</span>
                                                    )}
                                                </div>
                                            </div>
                                        </label>
                                    ))}
                                </div>

                                {/* Selection Summary */}
                                {selectedTopics.length > 0 && (
                                    <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                                        <p className="text-sm font-bold text-blue-800 mb-2">
                                            Selected: {selectedTopics.length} of {topics.length} topics
                                        </p>
                                        <p className="text-sm text-blue-700">
                                            {topics
                                                .filter(t => selectedTopics.includes(t?.id))
                                                .map(t => t?.name || 'Unknown')
                                                .join(', ')}
                                        </p>
                                    </div>
                                )}

                                {/* Generate Button */}
                                <button
                                    onClick={handleGeneratePaper}
                                    disabled={loading || selectedTopics.length === 0}
                                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 px-6 rounded-lg transition duration-200 shadow-md hover:shadow-lg disabled:bg-gray-400 disabled:cursor-not-allowed"
                                >
                                    {loading ? (
                                        <span className="flex items-center justify-center">
                                            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                            </svg>
                                            Generating Paper...
                                        </span>
                                    ) : (
                                        'Generate Paper'
                                    )}
                                </button>

                                {/* Generated Result */}
                                {generatedResult && (
                                    <div className="mt-6 p-6 bg-green-50 border border-green-200 rounded-lg">
                                        <h3 className="text-xl font-bold text-green-800 mb-4">
                                            Paper Generated Successfully!
                                        </h3>
                                        <div className="grid grid-cols-2 gap-4 mb-4">
                                            <div>
                                                <p className="text-sm text-green-700">Unique Code</p>
                                                <p className="text-lg font-bold text-green-900">
                                                    {generatedResult?.generated_paper?.unique_code || generatedResult?.unique_code || 'N/A'}
                                                </p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-green-700">Total Marks</p>
                                                <p className="text-lg font-bold text-green-900">
                                                    {generatedResult?.generated_paper?.total_marks || generatedResult?.total_marks || 0}
                                                </p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-green-700">Questions</p>
                                                <p className="text-lg font-bold text-green-900">
                                                    {generatedResult?.generated_paper?.total_questions || generatedResult?.question_count || generatedResult?.total_questions || 0}
                                                </p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-green-700">Status</p>
                                                <p className="text-lg font-bold text-green-900">
                                                    {(generatedResult?.generated_paper?.status || generatedResult?.status || 'DRAFT').toUpperCase()}
                                                </p>
                                            </div>
                                        </div>
                                        {generatedResult?.generated_paper?.id || generatedResult?.id ? (
                                            <button
                                                onClick={() => handleViewPaper(generatedResult?.generated_paper?.id || generatedResult?.id)}
                                                className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg transition"
                                            >
                                                📄 Continue to Coverpage
                                            </button>
                                        ) : (
                                            <div className="text-center text-red-600">
                                                <p className="text-sm">⚠️ Paper ID not found in response</p>
                                                <p className="text-xs mt-1">Please check the browser console for details</p>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </>
                        )}
                    </div>
                )}

                {/* History Tab */}
                {activeTab === 'history' && (
                    <div className="bg-white rounded-lg shadow-md p-4 sm:p-6">
                        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-3">
                            <div>
                                <h2 className="text-xl sm:text-2xl font-bold text-gray-800">Your Generated Papers</h2>
                                <p className="text-sm text-gray-600 mt-1">
                                    📅 Papers are kept for 30 days from generation date
                                </p>
                            </div>
                            {generatedPapers.length > 0 && (
                                <div className="text-right">
                                    <p className="text-sm font-semibold text-gray-700">
                                        {generatedPapers.length} paper{generatedPapers.length !== 1 ? 's' : ''} available
                                    </p>
                                </div>
                            )}
                        </div>

                        {historyLoading ? (
                            <div className="text-center py-12">
                                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                                <p className="mt-4 text-gray-600">Loading papers...</p>
                            </div>
                        ) : generatedPapers.length === 0 ? (
                            <div className="text-center py-12">
                                <p className="text-gray-600">No papers generated yet.</p>
                                <button
                                    onClick={() => setActiveTab('generate')}
                                    className="mt-4 text-blue-600 hover:text-blue-700 font-semibold"
                                >
                                    Generate Your First Paper →
                                </button>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {generatedPapers.map((paper) => {
                                    const daysRemaining = paper?.days_remaining ?? null;
                                    const isExpiringSoon = daysRemaining !== null && daysRemaining <= 7;
                                    const isExpired = daysRemaining !== null && daysRemaining <= 0;
                                    
                                    return (
                                        <div
                                            key={paper?.id || Math.random()}
                                            className={`border rounded-lg p-4 hover:shadow-md transition ${
                                                isExpired ? 'border-red-300 bg-red-50' : 
                                                isExpiringSoon ? 'border-yellow-300 bg-yellow-50' : 
                                                'border-gray-200'
                                            }`}
                                        >
                                            <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-3">
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-3">
                                                        <h3 className="text-lg font-bold text-gray-800">
                                                            {paper?.unique_code || 'N/A'}
                                                        </h3>
                                                        {daysRemaining !== null && (
                                                            <span className={`text-xs px-2 py-1 rounded-full font-semibold ${
                                                                isExpired ? 'bg-red-200 text-red-800' :
                                                                isExpiringSoon ? 'bg-yellow-200 text-yellow-800' :
                                                                'bg-green-200 text-green-800'
                                                            }`}>
                                                                {isExpired ? 'Expired' : 
                                                                 isExpiringSoon ? `${daysRemaining} day${daysRemaining !== 1 ? 's' : ''} left` :
                                                                 `${daysRemaining} days left`}
                                                            </span>
                                                        )}
                                                    </div>
                                                    <p className="text-sm text-gray-600 mt-1">
                                                        🕒 Generated on {paper?.created_at ? new Date(paper.created_at).toLocaleDateString('en-US', {
                                                            year: 'numeric',
                                                            month: 'long',
                                                            day: 'numeric'
                                                        }) : 'Unknown'} at{' '}
                                                        {paper?.created_at ? new Date(paper.created_at).toLocaleTimeString('en-US', {
                                                            hour: '2-digit',
                                                            minute: '2-digit'
                                                        }) : ''}
                                                    </p>
                                                    <p className="text-sm text-gray-700 mt-1">
                                                        📚 {paper?.subject_name || 'Unknown Subject'} - {paper?.paper_name || 'Unknown Paper'}
                                                    </p>
                                                    <div className="mt-2 flex gap-4 text-sm">
                                                        <span className="text-gray-600">
                                                            <strong>Questions:</strong> {paper?.total_questions || paper?.question_count || 0}
                                                        </span>
                                                        <span className="text-gray-600">
                                                            <strong>Marks:</strong> {paper?.total_marks || 0}
                                                        </span>
                                                        <span className={`font-semibold ${
                                                            paper?.validation_passed ? 'text-green-600' : 'text-yellow-600'
                                                        }`}>
                                                            {paper?.validation_passed ? '✓ Validated' : '⚠ Not Validated'}
                                                        </span>
                                                    </div>
                                                    {!paper?.id && (
                                                        <p className="text-xs text-red-600 mt-1">⚠️ Missing paper ID</p>
                                                    )}
                                                </div>
                                                <button
                                                    onClick={() => handleViewPaper(paper?.id)}
                                                    disabled={!paper?.id}
                                                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition disabled:bg-gray-400 disabled:cursor-not-allowed whitespace-nowrap w-full md:w-auto"
                                                >
                                                    📄 Edit Coverpage
                                                </button>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
