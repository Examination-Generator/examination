import { useState } from 'react';

export default function UserDashboard({ onLogout }) {
    const [step, setStep] = useState(1); // 1: Selection, 2: Cover Page, 3: Preview
    
    // Exam Selection States
    const [selectedSubject, setSelectedSubject] = useState('');
    const [selectedPaper, setSelectedPaper] = useState('');
    const [selectedTopics, setSelectedTopics] = useState([]);
    const [numberOfQuestions, setNumberOfQuestions] = useState('');
    
    // Cover Page States
    const [schoolName, setSchoolName] = useState('');
    const [examTerm, setExamTerm] = useState('');
    const [examYear, setExamYear] = useState(new Date().getFullYear());
    const [formClass, setFormClass] = useState('');
    const [duration, setDuration] = useState('');
    const [instructions, setInstructions] = useState('');
    const [totalMarks, setTotalMarks] = useState('');
    const [logoUrl, setLogoUrl] = useState('/exam.png'); // Default logo
    const [useCustomLogo, setUseCustomLogo] = useState(false);
    
    // Generated Exam States
    const [generatedExam, setGeneratedExam] = useState(null);
    const [markingScheme, setMarkingScheme] = useState(null);

    // Mock subjects data - should match EditorDashboard
    const subjects = {
        'Mathematics': {
            papers: ['Paper 1', 'Paper 2', 'Paper 3'],
            topics: {
                'Paper 1': ['Algebra', 'Geometry', 'Calculus'],
                'Paper 2': ['Statistics', 'Trigonometry'],
                'Paper 3': ['Advanced Calculus', 'Number Theory']
            }
        },
        'English': {
            papers: ['Paper 1', 'Paper 2'],
            topics: {
                'Paper 1': ['Grammar', 'Composition', 'Literature'],
                'Paper 2': ['Comprehension', 'Poetry Analysis']
            }
        },
        'Physics': {
            papers: ['Paper 1', 'Paper 2', 'Paper 3'],
            topics: {
                'Paper 1': ['Mechanics', 'Electricity'],
                'Paper 2': ['Waves', 'Thermodynamics'],
                'Paper 3': ['Modern Physics', 'Optics']
            }
        },
        'Chemistry': {
            papers: ['Paper 1', 'Paper 2', 'Paper 3'],
            topics: {
                'Paper 1': ['Organic Chemistry', 'Inorganic Chemistry'],
                'Paper 2': ['Physical Chemistry', 'Analytical Chemistry'],
                'Paper 3': ['Biochemistry', 'Industrial Chemistry']
            }
        },
        'Biology': {
            papers: ['Paper 1', 'Paper 2', 'Paper 3'],
            topics: {
                'Paper 1': ['Cell Biology', 'Genetics'],
                'Paper 2': ['Evolution', 'Ecology'],
                'Paper 3': ['Human Biology', 'Microbiology']
            }
        }
    };

    const handleSubjectChange = (subject) => {
        setSelectedSubject(subject);
        setSelectedPaper('');
        setSelectedTopics([]);
    };

    const handlePaperChange = (paper) => {
        setSelectedPaper(paper);
        setSelectedTopics([]);
    };

    const handleTopicToggle = (topic) => {
        if (selectedTopics.includes(topic)) {
            setSelectedTopics(selectedTopics.filter(t => t !== topic));
        } else {
            setSelectedTopics([...selectedTopics, topic]);
        }
    };

    const handleGenerateExam = (e) => {
        e.preventDefault();
        
        // Mock exam generation
        const mockQuestions = Array.from({ length: parseInt(numberOfQuestions) }, (_, i) => ({
            number: i + 1,
            text: `Sample question ${i + 1} from ${selectedTopics.join(', ')}`,
            marks: Math.floor(Math.random() * 10) + 1,
            topic: selectedTopics[i % selectedTopics.length]
        }));

        const mockMarkingScheme = mockQuestions.map(q => ({
            number: q.number,
            answer: `Solution to question ${q.number}`,
            marks: q.marks
        }));

        setGeneratedExam(mockQuestions);
        setMarkingScheme(mockMarkingScheme);
        setStep(3);
    };

    const handleProceedToCoverPage = () => {
        if (!selectedSubject || !selectedPaper || selectedTopics.length === 0) {
            alert('Please select subject, paper, and at least one topic');
            return;
        }
        setStep(2);
    };

    const handleBackToSelection = () => {
        setStep(1);
    };

    const handlePrintExam = () => {
        window.print();
    };

    const handleDownloadExam = () => {
        alert('Exam download functionality will be implemented');
    };

    const handleLogoUpload = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setLogoUrl(reader.result);
                setUseCustomLogo(true);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleUseDefaultLogo = () => {
        setLogoUrl('/exam.png');
        setUseCustomLogo(false);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100">
            {/* Header */}
            <header className="bg-white shadow-md print:hidden">
                <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <img src="/exam.png" alt="Exam Logo" className="w-12 h-12 object-contain" />
                            <h1 className="text-2xl font-bold text-green-600">Exam Generator</h1>
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

            {/* Step 1: Exam Selection */}
            {step === 1 && (
                <div className="max-w-4xl mx-auto px-4 py-8">
                    <div className="bg-white rounded-xl shadow-lg p-8">
                        <h2 className="text-2xl font-bold text-gray-800 mb-6">Create New Exam</h2>
                        
                        <form onSubmit={(e) => { e.preventDefault(); handleProceedToCoverPage(); }}>
                            {/* Subject Selection */}
                            <div className="mb-6">
                                <label className="block text-sm font-bold text-gray-700 mb-2">
                                    Select Subject *
                                </label>
                                <select
                                    value={selectedSubject}
                                    onChange={(e) => handleSubjectChange(e.target.value)}
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                    required
                                >
                                    <option value="">Choose Subject</option>
                                    {Object.keys(subjects).map((subject) => (
                                        <option key={subject} value={subject}>{subject}</option>
                                    ))}
                                </select>
                            </div>

                            {/* Paper Selection */}
                            <div className="mb-6">
                                <label className="block text-sm font-bold text-gray-700 mb-2">
                                    Select Paper *
                                </label>
                                <select
                                    value={selectedPaper}
                                    onChange={(e) => handlePaperChange(e.target.value)}
                                    disabled={!selectedSubject}
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition disabled:bg-gray-100"
                                    required
                                >
                                    <option value="">Choose Paper</option>
                                    {selectedSubject && subjects[selectedSubject].papers.map((paper) => (
                                        <option key={paper} value={paper}>{paper}</option>
                                    ))}
                                </select>
                            </div>

                            {/* Topic Selection */}
                            {selectedPaper && (
                                <div className="mb-6">
                                    <label className="block text-sm font-bold text-gray-700 mb-2">
                                        Select Topics * (Choose at least one)
                                    </label>
                                    <div className="grid grid-cols-2 gap-3">
                                        {subjects[selectedSubject].topics[selectedPaper].map((topic) => (
                                            <label
                                                key={topic}
                                                className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition ${
                                                    selectedTopics.includes(topic)
                                                        ? 'border-green-500 bg-green-50'
                                                        : 'border-gray-300 hover:border-green-300'
                                                }`}
                                            >
                                                <input
                                                    type="checkbox"
                                                    checked={selectedTopics.includes(topic)}
                                                    onChange={() => handleTopicToggle(topic)}
                                                    className="w-5 h-5 text-green-600 rounded focus:ring-green-500"
                                                />
                                                <span className="ml-3 font-medium text-gray-700">{topic}</span>
                                            </label>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Number of Questions */}
                            <div className="mb-6">
                                <label className="block text-sm font-bold text-gray-700 mb-2">
                                    Number of Questions *
                                </label>
                                <input
                                    type="number"
                                    value={numberOfQuestions}
                                    onChange={(e) => setNumberOfQuestions(e.target.value)}
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                    placeholder="Enter number of questions"
                                    min="1"
                                    max="50"
                                    required
                                />
                            </div>

                            {/* Selected Summary */}
                            {selectedSubject && selectedPaper && selectedTopics.length > 0 && (
                                <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                                    <p className="text-sm font-bold text-green-800 mb-2">Selection Summary:</p>
                                    <p className="text-sm text-green-700">
                                        <strong>Subject:</strong> {selectedSubject}<br />
                                        <strong>Paper:</strong> {selectedPaper}<br />
                                        <strong>Topics:</strong> {selectedTopics.join(', ')}
                                    </p>
                                </div>
                            )}

                            <button
                                type="submit"
                                disabled={!selectedSubject || !selectedPaper || selectedTopics.length === 0 || !numberOfQuestions}
                                className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 shadow-md hover:shadow-lg disabled:bg-gray-400 disabled:cursor-not-allowed"
                            >
                                Proceed to Cover Page
                            </button>
                        </form>
                    </div>
                </div>
            )}

            {/* Step 2: Cover Page Configuration */}
            {step === 2 && (
                <div className="max-w-4xl mx-auto px-4 py-8">
                    <div className="bg-white rounded-xl shadow-lg p-8">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-2xl font-bold text-gray-800">Configure Cover Page</h2>
                            <button
                                onClick={handleBackToSelection}
                                className="text-green-600 hover:text-green-700 font-semibold"
                            >
                                ← Back
                            </button>
                        </div>
                        
                        <form onSubmit={handleGenerateExam}>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {/* Logo Upload */}
                                <div className="md:col-span-2">
                                    <label className="block text-sm font-bold text-gray-700 mb-2">
                                        School Logo (Optional)
                                    </label>
                                    <div className="flex items-center space-x-4">
                                        <div className="flex-shrink-0">
                                            <img 
                                                src={logoUrl} 
                                                alt="School Logo" 
                                                className="w-20 h-20 object-contain border-2 border-gray-300 rounded-lg p-2"
                                            />
                                        </div>
                                        <div className="flex-1">
                                            <input
                                                type="file"
                                                accept="image/*"
                                                onChange={handleLogoUpload}
                                                className="hidden"
                                                id="logo-upload"
                                            />
                                            <label
                                                htmlFor="logo-upload"
                                                className="inline-block bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg cursor-pointer transition mr-2"
                                            >
                                                Upload Custom Logo
                                            </label>
                                            {useCustomLogo && (
                                                <button
                                                    type="button"
                                                    onClick={handleUseDefaultLogo}
                                                    className="inline-block bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition"
                                                >
                                                    Use Default Logo
                                                </button>
                                            )}
                                            <p className="text-xs text-gray-500 mt-2">
                                                Upload your school logo or use the default exam.png
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                {/* School Name */}
                                <div className="md:col-span-2">
                                    <label className="block text-sm font-bold text-gray-700 mb-2">
                                        School Name *
                                    </label>
                                    <input
                                        type="text"
                                        value={schoolName}
                                        onChange={(e) => setSchoolName(e.target.value)}
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                        placeholder="Enter school name"
                                        required
                                    />
                                </div>

                                {/* Term */}
                                <div>
                                    <label className="block text-sm font-bold text-gray-700 mb-2">
                                        Term *
                                    </label>
                                    <select
                                        value={examTerm}
                                        onChange={(e) => setExamTerm(e.target.value)}
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                        required
                                    >
                                        <option value="">Select Term</option>
                                        <option value="Term 1">Term 1</option>
                                        <option value="Term 2">Term 2</option>
                                        <option value="Term 3">Term 3</option>
                                        <option value="Mid-Term">Mid-Term</option>
                                        <option value="End-Term">End-Term</option>
                                    </select>
                                </div>

                                {/* Year */}
                                <div>
                                    <label className="block text-sm font-bold text-gray-700 mb-2">
                                        Year *
                                    </label>
                                    <input
                                        type="number"
                                        value={examYear}
                                        onChange={(e) => setExamYear(e.target.value)}
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                        required
                                    />
                                </div>

                                {/* Form/Class */}
                                <div>
                                    <label className="block text-sm font-bold text-gray-700 mb-2">
                                        Form/Class *
                                    </label>
                                    <input
                                        type="text"
                                        value={formClass}
                                        onChange={(e) => setFormClass(e.target.value)}
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                        placeholder="e.g., Form 4"
                                        required
                                    />
                                </div>

                                {/* Duration */}
                                <div>
                                    <label className="block text-sm font-bold text-gray-700 mb-2">
                                        Duration *
                                    </label>
                                    <input
                                        type="text"
                                        value={duration}
                                        onChange={(e) => setDuration(e.target.value)}
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                        placeholder="e.g., 2 Hours 30 Minutes"
                                        required
                                    />
                                </div>

                                {/* Total Marks */}
                                <div className="md:col-span-2">
                                    <label className="block text-sm font-bold text-gray-700 mb-2">
                                        Total Marks *
                                    </label>
                                    <input
                                        type="number"
                                        value={totalMarks}
                                        onChange={(e) => setTotalMarks(e.target.value)}
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                        placeholder="Enter total marks"
                                        required
                                    />
                                </div>

                                {/* Instructions */}
                                <div className="md:col-span-2">
                                    <label className="block text-sm font-bold text-gray-700 mb-2">
                                        Instructions *
                                    </label>
                                    <textarea
                                        value={instructions}
                                        onChange={(e) => setInstructions(e.target.value)}
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                        rows="5"
                                        placeholder="Enter exam instructions..."
                                        required
                                    />
                                </div>
                            </div>

                            <button
                                type="submit"
                                className="w-full mt-6 bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 shadow-md hover:shadow-lg"
                            >
                                Generate Exam
                            </button>
                        </form>
                    </div>
                </div>
            )}

            {/* Step 3: Exam Preview */}
            {step === 3 && generatedExam && (
                <div>
                    {/* Action Buttons - Hidden on Print */}
                    <div className="max-w-7xl mx-auto px-4 py-4 print:hidden">
                        <div className="flex justify-between items-center bg-white rounded-lg shadow-md p-4">
                            <button
                                onClick={() => setStep(1)}
                                className="text-green-600 hover:text-green-700 font-semibold"
                            >
                                ← Create New Exam
                            </button>
                            <div className="flex space-x-4">
                                <button
                                    onClick={handlePrintExam}
                                    className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg transition"
                                >
                                    Print Exam
                                </button>
                                <button
                                    onClick={handleDownloadExam}
                                    className="bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-6 rounded-lg transition"
                                >
                                    Download PDF
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Exam Paper */}
                    <div className="max-w-5xl mx-auto px-4 py-8 bg-white print:p-0">
                        {/* Cover Page */}
                        <div className="bg-white rounded-lg mb-8 print:border-0 print:h-screen print:flex print:flex-col print:justify-between" style={{ pageBreakAfter: 'always' }}>
                            <div className="p-8">
                                {/* Logo and Header */}
                                <div className="mb-6">
                                    <div className="flex justify-start mb-4">
                                        <img 
                                            src={logoUrl} 
                                            alt="School Logo" 
                                            className="w-16 h-16 object-contain"
                                        />
                                    </div>
                                    <div className="text-center">
                                        <h1 className="text-2xl font-bold mb-1">{schoolName}</h1>
                                        <h2 className="text-lg font-semibold mb-2">{examTerm} {examYear} EXAMINATION</h2>
                                        <div className="py-2 my-2">
                                            <h3 className="text-xl font-bold">{selectedSubject.toUpperCase()}</h3>
                                            <h4 className="text-lg">{selectedPaper}</h4>
                                        </div>
                                    </div>
                                </div>

                                {/* Student Details */}
                                <div className="mb-4">
                                    <h4 className="font-bold mb-3 text-sm">CANDIDATE DETAILS</h4>
                                    <div className="space-y-2 text-sm">
                                        <div className="flex">
                                            <span className="font-semibold w-40">Name:</span>
                                            <span className="flex-1 border-b border-gray-400"></span>
                                        </div>
                                        <div className="flex">
                                            <span className="font-semibold w-40">Admission Number:</span>
                                            <span className="flex-1 border-b border-gray-400"></span>
                                        </div>
                                        <div className="flex">
                                            <span className="font-semibold w-40">Class/Stream:</span>
                                            <span className="flex-1 border-b border-gray-400"></span>
                                        </div>
                                        <div className="flex">
                                            <span className="font-semibold w-40">Date:</span>
                                            <span className="flex-1 border-b border-gray-400"></span>
                                        </div>
                                        <div className="flex">
                                            <span className="font-semibold w-40">Signature:</span>
                                            <span className="flex-1 border-b border-gray-400"></span>
                                        </div>
                                    </div>
                                </div>

                                {/* Exam Info */}
                                <div className="mb-4 text-sm">
                                    <div className="flex justify-between">
                                        <span><strong>Class:</strong> {formClass}</span>
                                        <span><strong>Duration:</strong> {duration}</span>
                                    </div>
                                </div>

                                {/* Instructions */}
                                <div className="mb-4">
                                    <h4 className="font-bold mb-2 text-sm">INSTRUCTIONS TO CANDIDATES:</h4>
                                    <ol className="text-sm leading-relaxed list-decimal list-inside space-y-1">
                                        {instructions.split('\n').filter(line => line.trim()).map((instruction, index) => (
                                            <li key={index}>{instruction.trim()}</li>
                                        ))}
                                    </ol>
                                </div>
                            </div>

                            {/* Examiner's Use Only - Bottom of page */}
                            <div className="p-8 pt-0">
                                <div className="p-4">
                                    <h4 className="font-bold text-center mb-3 text-sm">FOR EXAMINER'S USE ONLY</h4>
                                    <table className="w-full border-collapse">
                                        <thead>
                                            <tr className="border-2 border-gray-800">
                                                <th className="border-2 border-gray-800 p-2 text-sm">Total Marks</th>
                                                <th className="border-2 border-gray-800 p-2 text-sm">Marks Scored</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td className="border-2 border-gray-800 p-3 text-center text-lg font-bold">{totalMarks}</td>
                                                <td className="border-2 border-gray-800 p-3"></td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>

                        {/* Questions */}
                        <div className="bg-white p-12 print:p-8">
                            <h2 className="text-2xl font-bold mb-6 text-center">SECTION A: QUESTIONS</h2>
                            
                            {generatedExam.map((question, index) => {
                                // Calculate space based on marks: 60px base + 40px per mark
                                const answerSpace = 60 + (question.marks * 40);
                                
                                return (
                                    <div key={question.number} className="mb-6">
                                        <div className="flex justify-between items-start">
                                            <p className="font-semibold">
                                                {question.number}. {question.text}
                                            </p>
                                            <span className="text-sm font-bold ml-4">({question.marks} marks)</span>
                                        </div>
                                        <div 
                                            className="mt-4" 
                                            style={{ minHeight: `${answerSpace}px` }}
                                        ></div>
                                    </div>
                                );
                            })}
                        </div>

                        {/* Footer with Page Number */}
                        <div className="bg-white p-4 print:p-4">
                            <div className="text-right text-sm text-gray-600">
                                Page 1 of 1
                            </div>
                        </div>

                        {/* Marking Scheme - Separate Document */}
                        <div className="bg-white print:p-0" style={{ pageBreakBefore: 'always' }}>
                            {/* Marking Scheme Cover Page */}
                            <div className="bg-whiterounded-lg mb-8 print:border-0 print:h-screen print:flex print:flex-col print:justify-between" style={{ pageBreakAfter: 'always' }}>
                                <div className="p-8">
                                    {/* Logo and Header */}
                                    <div className="mb-6">
                                        <div className="flex justify-start mb-4">
                                            <img 
                                                src={logoUrl} 
                                                alt="School Logo" 
                                                className="w-16 h-16 object-contain"
                                            />
                                        </div>
                                        <div className="text-center">
                                            <h1 className="text-2xl font-bold mb-1">{schoolName}</h1>
                                            <h2 className="text-lg font-semibold mb-2">{examTerm} {examYear} EXAMINATION</h2>
                                            <div className="py-2 my-2">
                                                <h3 className="text-xl font-bold">{selectedSubject.toUpperCase()}</h3>
                                                <h4 className="text-lg">{selectedPaper}</h4>
                                            </div>
                                            <div className="mt-4">
                                                <h3 className="text-2xl font-bold text-green-600">MARKING SCHEME</h3>
                                                <p className="text-red-600 font-semibold mt-2">CONFIDENTIAL - FOR EXAMINER'S USE ONLY</p>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Document Info */}
                                    <div className="mb-4">
                                        <h4 className="font-bold mb-3 text-sm">DOCUMENT INFORMATION</h4>
                                        <div className="space-y-2 text-sm">
                                            <div className="flex">
                                                <span className="font-semibold w-40">Subject:</span>
                                                <span className="flex-1">{selectedSubject}</span>
                                            </div>
                                            <div className="flex">
                                                <span className="font-semibold w-40">Paper:</span>
                                                <span className="flex-1">{selectedPaper}</span>
                                            </div>
                                            <div className="flex">
                                                <span className="font-semibold w-40">Class:</span>
                                                <span className="flex-1">{formClass}</span>
                                            </div>
                                            <div className="flex">
                                                <span className="font-semibold w-40">Total Marks:</span>
                                                <span className="flex-1 font-bold">{totalMarks}</span>
                                            </div>
                                            <div className="flex">
                                                <span className="font-semibold w-40">Number of Questions:</span>
                                                <span className="flex-1">{generatedExam.length}</span>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Instructions for Examiners */}
                                    <div className="mb-4">
                                        <h4 className="font-bold mb-2 text-sm">INSTRUCTIONS TO EXAMINERS:</h4>
                                        <ol className="text-sm leading-relaxed list-decimal list-inside space-y-1">
                                            <li>This marking scheme is strictly confidential and must not be shared with candidates.</li>
                                            <li>Award marks as indicated for correct answers or acceptable alternatives.</li>
                                            <li>Be consistent in marking across all scripts.</li>
                                            <li>Use the provided answer key as a guide for awarding marks.</li>
                                            <li>Ensure all questions are marked and totals are verified.</li>
                                        </ol>
                                    </div>
                                </div>

                                {/* Footer */}
                                <div className="p-8 pt-0">
                                    <div className="border-t-2 border-gray-400 pt-4 text-center text-sm text-gray-600">
                                        <p className="font-semibold">This document is the property of {schoolName}</p>
                                        <p>© {examYear} - All Rights Reserved</p>
                                    </div>
                                </div>
                            </div>

                            {/* Marking Scheme Content */}
                            <div className="bg-white p-12 print:p-8">
                                <h2 className="text-2xl font-bold mb-6 text-center text-green-600">DETAILED MARKING SCHEME</h2>
                                
                                {markingScheme.map((item) => (
                                    <div key={item.number} className="mb-6 pb-4">
                                        <p className="font-bold mb-2">Question {item.number} ({item.marks} marks)</p>
                                        <p className="text-gray-700"><strong>Answer:</strong> {item.answer}</p>
                                    </div>
                                ))}
                            </div>

                            {/* Footer with Page Number */}
                            <div className="bg-white p-4 print:p-4">
                                <div className="text-right text-sm text-gray-600">
                                    Page 1 of {Math.ceil(markingScheme.length / 10)}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
