import { useState, useEffect } from 'react';

export default function EditorDashboard({ onLogout }) {
    const [activeTab, setActiveTab] = useState('questions'); // 'questions' or 'subjects'
    const [selectedSubject, setSelectedSubject] = useState('');
    const [selectedTopic, setSelectedTopic] = useState('');
    const [selectedPaper, setSelectedPaper] = useState('');
    const [selectedSection, setSelectedSection] = useState('');
    const [questionText, setQuestionText] = useState('');
    const [answerText, setAnswerText] = useState('');
    const [marks, setMarks] = useState('');
    const [similarQuestions, setSimilarQuestions] = useState([]);
    const [isSearching, setIsSearching] = useState(false);
    const [showMobileSimilar, setShowMobileSimilar] = useState(false);

    // New Subject Form States
    const [newSubjectName, setNewSubjectName] = useState('');
    const [newSubjectPapers, setNewSubjectPapers] = useState([{ name: '', topics: [''], sections: [''] }]);

    // Subject configuration with topics, papers and sections
    const subjects = {
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

    // Search for similar questions when question text changes
    useEffect(() => {
        if (questionText.length > 10) {
            setIsSearching(true);
            // Simulate API call to search for similar questions
            const timer = setTimeout(() => {
                // Mock similar questions - replace with actual API call
                const mockSimilar = [
                    { id: 1, text: 'Calculate the area of a triangle with base 10cm...', similarity: 85, count: 3 },
                    { id: 2, text: 'Find the area of a rectangular triangle...', similarity: 72, count: 2 },
                ];
                setSimilarQuestions(mockSimilar);
                setIsSearching(false);
            }, 500);
            return () => clearTimeout(timer);
        } else {
            setSimilarQuestions([]);
        }
    }, [questionText]);

    const handleSubjectChange = (subject) => {
        setSelectedSubject(subject);
        setSelectedPaper('');
        setSelectedTopic('');
        setSelectedSection('');
    };

    const handlePaperChange = (paper) => {
        setSelectedPaper(paper);
        setSelectedTopic('');
        setSelectedSection('');
    };

    const handleTopicChange = (topic) => {
        setSelectedTopic(topic);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        
        if (!selectedSubject || !selectedTopic || !selectedPaper) {
            alert('Please select subject, topic and paper');
            return;
        }

        const questionData = {
            subject: selectedSubject,
            topic: selectedTopic,
            paper: selectedPaper,
            section: selectedSection || 'No Section',
            questionText,
            answerText,
            marks: parseInt(marks),
            timestamp: new Date().toISOString()
        };

        console.log('Submitting question:', questionData);
        // TODO: Send to database
        
        // Clear form after submission
        setQuestionText('');
        setAnswerText('');
        setMarks('');
        setSimilarQuestions([]);
        alert('Question submitted successfully!');
    };

    const scrollToSimilar = () => {
        const similarSection = document.getElementById('similar-questions-section');
        if (similarSection) {
            similarSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
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

    const handleSubmitNewSubject = (e) => {
        e.preventDefault();
        
        const subjectData = {
            name: newSubjectName,
            papers: newSubjectPapers.map(paper => ({
                name: paper.name,
                topics: paper.topics.filter(t => t.trim() !== ''),
                sections: paper.sections.filter(s => s.trim() !== '').length > 0 
                    ? paper.sections.filter(s => s.trim() !== '')
                    : ['None']
            }))
        };

        console.log('Submitting new subject:', subjectData);
        // TODO: Send to database
        
        alert('Subject added successfully!');
        // Reset form
        setNewSubjectName('');
        setNewSubjectPapers([{ name: '', topics: [''], sections: [''] }]);
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
                            onClick={onLogout}
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
                {/* Selection Section */}
                <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
                    <h2 className="text-xl font-bold text-gray-800 mb-4">Exam Organization</h2>
                    
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
                                {selectedSubject && subjects[selectedSubject].papers.map((paper) => (
                                    <option key={paper} value={paper}>{paper}</option>
                                ))}
                            </select>
                        </div>

                        {/* Topic Selection */}
                        <div>
                            <label className="block text-sm font-bold text-gray-700 mb-2">
                                Select Topic *
                            </label>
                            <select
                                value={selectedTopic}
                                onChange={(e) => handleTopicChange(e.target.value)}
                                disabled={!selectedPaper}
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition disabled:bg-gray-100"
                            >
                                <option value="">Choose Topic</option>
                                {selectedSubject && subjects[selectedSubject].topics.map((topic) => (
                                    <option key={topic} value={topic}>{topic}</option>
                                ))}
                            </select>
                        </div>

                        {/* Section Selection */}
                        <div>
                            <label className="block text-sm font-bold text-gray-700 mb-2">
                                Select Section {selectedPaper && subjects[selectedSubject]?.sections[selectedPaper]?.length > 0 && '*'}
                            </label>
                            <select
                                value={selectedSection}
                                onChange={(e) => setSelectedSection(e.target.value)}
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

                    {/* Current Selection Display */}
                    {selectedSubject && (
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
                        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-lg p-6">
                            <h2 className="text-xl font-bold text-gray-800 mb-4">Question Entry</h2>
                            
                            {/* Question Text */}
                            <div className="mb-4">
                                <label className="block text-sm font-bold text-gray-700 mb-2">
                                    Question Text *
                                </label>
                                <textarea
                                    value={questionText}
                                    onChange={(e) => setQuestionText(e.target.value)}
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                    rows="6"
                                    placeholder="Enter the question text here..."
                                    required
                                />
                            </div>

                            {/* Question Preview in Answer Section */}
                            {questionText && (
                                <div className="mb-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                                    <p className="text-xs font-bold text-blue-800 mb-2">QUESTION PREVIEW:</p>
                                    <p className="text-sm text-gray-700">{questionText}</p>
                                </div>
                            )}

                            {/* Answer Text */}
                            <div className="mb-4">
                                <label className="block text-sm font-bold text-gray-700 mb-2">
                                    Answer/Solution *
                                </label>
                                <textarea
                                    value={answerText}
                                    onChange={(e) => setAnswerText(e.target.value)}
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                    rows="6"
                                    placeholder="Solution: Enter the answer or solution here..."
                                    required
                                />
                                <p className="text-xs text-gray-500 mt-1">
                                    Start with "Solution:" or "Answer:" to clearly identify the solution
                                </p>
                            </div>

                            {/* Marks */}
                            <div className="mb-6">
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

                            {/* Submit Button */}
                            <button
                                type="submit"
                                disabled={!selectedSubject || !selectedTopic || !selectedPaper}
                                className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 shadow-md hover:shadow-lg disabled:bg-gray-400 disabled:cursor-not-allowed"
                            >
                                Submit Question
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
                                            Review these questions to avoid duplicates
                                        </p>
                                    </div>

                                    {similarQuestions.map((question) => (
                                        <div key={question.id} className="border border-gray-200 rounded-lg p-3 hover:border-green-500 transition">
                                            <div className="flex justify-between items-start mb-2">
                                                <span className="text-xs font-bold text-green-600">
                                                    {question.similarity}% Match
                                                </span>
                                                <span className="text-xs text-gray-500">
                                                    Used {question.count}x
                                                </span>
                                            </div>
                                            <p className="text-sm text-gray-700">{question.text}</p>
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
                )}
            </div>
        </div>
    );
}
