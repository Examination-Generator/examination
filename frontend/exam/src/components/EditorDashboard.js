import { useState, useEffect, useRef } from 'react';
import mammoth from 'mammoth';
import * as pdfjsLib from 'pdfjs-dist';

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
    const [drawingTool, setDrawingTool] = useState('pen');
    const [drawingColor, setDrawingColor] = useState('#000000');
    const [drawingWidth, setDrawingWidth] = useState(2);
    const canvasRef = useRef(null);
    const [isDrawing, setIsDrawing] = useState(false);
    const questionTextareaRef = useRef(null);
    
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
    const answerTextareaRef = useRef(null);
    
    // Inline images for answer
    const [answerInlineImages, setAnswerInlineImages] = useState([]);
    
    // Bulk entry states
    const [bulkText, setBulkText] = useState('');
    const [showBulkEntry, setShowBulkEntry] = useState(false);
    const [bulkQuestions, setBulkQuestions] = useState([]);
    const [currentBulkIndex, setCurrentBulkIndex] = useState(0);
    
    // Statistics and filters
    const [savedQuestions, setSavedQuestions] = useState([]); // Mock database
    const [filterSubject, setFilterSubject] = useState('');
    const [filterPaper, setFilterPaper] = useState('');
    const [filterTopic, setFilterTopic] = useState('');
    const [filterStatus, setFilterStatus] = useState('all'); // 'all', 'active', 'inactive'

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
        
        if (!selectedSubject || !selectedPaper) {
            alert('Please select subject and paper');
            return;
        }

        const questionData = {
            id: Date.now(),
            subject: selectedSubject,
            topic: selectedTopic || 'Unknown',
            paper: selectedPaper,
            section: selectedSection || 'No Section',
            questionText,
            answerText,
            marks: parseInt(marks),
            status: isQuestionActive ? 'Active' : 'Inactive',
            questionImages: uploadedImages,
            answerImages: uploadedAnswerImages,
            timestamp: new Date().toISOString()
        };

        // Save to local state (mock database)
        setSavedQuestions(prev => [...prev, questionData]);
        console.log('Submitting question:', questionData);
        // TODO: Send to database
        
        // Clear form after submission
        setQuestionText('');
        setAnswerText('');
        setMarks('');
        setUploadedImages([]);
        setUploadedAnswerImages([]);
        setIsQuestionActive(true);
        setSimilarQuestions([]);
        alert('Question submitted successfully!');
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
                    
                    // Auto-insert the image directly into content
                    setTimeout(() => {
                        insertInlineImage(newImage.id, 'question');
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
        const ctx = canvas.getContext('2d');
        
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.strokeStyle = drawingColor;
        ctx.lineWidth = drawingWidth;
        ctx.lineCap = 'round';
    };

    const draw = (e) => {
        if (!isDrawing) return;
        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const ctx = canvas.getContext('2d');
        
        if (drawingTool === 'eraser') {
            ctx.strokeStyle = 'white';
            ctx.lineWidth = 20;
        } else {
            ctx.strokeStyle = drawingColor;
            ctx.lineWidth = drawingWidth;
        }
        
        ctx.lineTo(x, y);
        ctx.stroke();
    };

    const stopDrawing = () => {
        setIsDrawing(false);
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
        
        // Add to inline images
        setQuestionInlineImages(prev => [...prev, newImage]);
        
        // Also keep in uploaded images for backwards compatibility
        setUploadedImages(prev => [...prev, newImage]);
        
        // Auto-insert the drawing directly into content
        setTimeout(() => {
            insertInlineImage(newImage.id, 'question');
        }, 100);
        
        setShowDrawingTool(false);
    };

    const insertInlineImage = (imageId, targetType = 'question') => {
        const images = targetType === 'question' ? questionInlineImages : answerInlineImages;
        const setImages = targetType === 'question' ? setQuestionInlineImages : setAnswerInlineImages;
        const setText = targetType === 'question' ? setQuestionText : setAnswerText;
        const text = targetType === 'question' ? questionText : answerText;
        const textareaRef = targetType === 'question' ? questionTextareaRef : answerTextareaRef;
        
        const image = images.find(img => img.id === imageId);
        if (!image) return;
        
        // Get cursor position
        const textarea = textareaRef.current;
        const cursorPosition = textarea ? textarea.selectionStart : text.length;
        
        // Insert image placeholder at cursor position with width and height
        const imagePlaceholder = `\n[IMAGE:${image.id}:${image.width}x${image.height}px]\n`;
        const newText = text.slice(0, cursorPosition) + imagePlaceholder + text.slice(cursorPosition);
        setText(newText);
        
        // Update image position
        setImages(prev => prev.map(img => 
            img.id === imageId ? { ...img, position: cursorPosition } : img
        ));
        
        alert('✅ Image inserted at cursor position!');
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
                alert('⚠️ Please drop only image files (.jpg, .png, .gif, etc.)');
            }
        });
    };

    // Answer section handlers
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
                    
                    setAnswerInlineImages(prev => [...prev, newImage]);
                    setUploadedAnswerImages(prev => [...prev, newImage]);
                    
                    // Auto-insert the image directly into content
                    setTimeout(() => {
                        insertInlineImage(newImage.id, 'answer');
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

    // Answer canvas drawing functions
    useEffect(() => {
        if (showAnswerDrawingTool && answerCanvasRef.current) {
            const canvas = answerCanvasRef.current;
            const ctx = canvas.getContext('2d');
            
            // Set canvas size to A4 printable area: 210mm x 297mm
            // At 96 DPI: 210mm = ~794px, 297mm = ~1123px
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
            
            ctx.fillStyle = 'white';
            ctx.fillRect(0, 0, displayWidth, displayHeight);
            
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
        const ctx = canvas.getContext('2d');
        
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.strokeStyle = answerDrawingColor;
        ctx.lineWidth = answerDrawingWidth;
        ctx.lineCap = 'round';
    };

    const drawAnswer = (e) => {
        if (!isAnswerDrawing) return;
        const canvas = answerCanvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const ctx = canvas.getContext('2d');
        
        if (answerDrawingTool === 'eraser') {
            ctx.strokeStyle = 'white';
            ctx.lineWidth = 20;
        } else {
            ctx.strokeStyle = answerDrawingColor;
            ctx.lineWidth = answerDrawingWidth;
        }
        
        ctx.lineTo(x, y);
        ctx.stroke();
    };

    const stopAnswerDrawing = () => {
        setIsAnswerDrawing(false);
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
        // Export at high quality - PNG format preserves quality
        const imageUrl = canvas.toDataURL('image/png', 1.0);
        const newImage = {
            id: Date.now(),
            url: imageUrl,
            name: 'Answer_Drawing_' + new Date().getTime() + '.png',
            width: 600, // Larger default for better visibility
            height: 400, // Maintain aspect ratio
            position: answerText.length
        };
        
        // Add to inline images
        setAnswerInlineImages(prev => [...prev, newImage]);
        
        // Also keep in uploaded images for backwards compatibility
        setUploadedAnswerImages(prev => [...prev, newImage]);
        
        // Auto-insert the drawing directly into content
        setTimeout(() => {
            insertInlineImage(newImage.id, 'answer');
        }, 100);
        
        setShowAnswerDrawingTool(false);
    };

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
            totalQuestions: savedQuestions.length,
            activeQuestions: savedQuestions.filter(q => q.status === 'Active').length,
            inactiveQuestions: savedQuestions.filter(q => q.status === 'Inactive').length,
            unknownTopics: savedQuestions.filter(q => q.topic === 'Unknown').length,
            bySubject: {},
            byPaper: {},
            byTopic: {}
        };

        savedQuestions.forEach(q => {
            // By subject
            stats.bySubject[q.subject] = (stats.bySubject[q.subject] || 0) + 1;
            
            // By paper
            const paperKey = `${q.subject} - ${q.paper}`;
            stats.byPaper[paperKey] = (stats.byPaper[paperKey] || 0) + 1;
            
            // By topic
            if (q.topic !== 'Unknown') {
                stats.byTopic[q.topic] = (stats.byTopic[q.topic] || 0) + 1;
            }
        });

        return stats;
    };

    const getFilteredQuestions = () => {
        return savedQuestions.filter(q => {
            if (filterSubject && q.subject !== filterSubject) return false;
            if (filterPaper && q.paper !== filterPaper) return false;
            if (filterTopic && q.topic !== filterTopic) return false;
            if (filterStatus !== 'all') {
                if (filterStatus === 'active' && q.status !== 'Active') return false;
                if (filterStatus === 'inactive' && q.status !== 'Inactive') return false;
            }
            return true;
        });
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
                                Select Topic (Optional)
                            </label>
                            <select
                                value={selectedTopic}
                                onChange={(e) => handleTopicChange(e.target.value)}
                                disabled={!selectedPaper}
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition disabled:bg-gray-100"
                            >
                                <option value="">Choose Topic or leave as Unknown</option>
                                <option value="Unknown" className="font-bold text-orange-600">⚠️ Unknown Topic</option>
                                {selectedSubject && subjects[selectedSubject].topics.map((topic) => (
                                    <option key={topic} value={topic}>{topic}</option>
                                ))}
                            </select>
                            {selectedTopic === 'Unknown' && (
                                <p className="text-xs text-orange-600 mt-1">
                                    ⚠️ This question will be marked for topic classification later
                                </p>
                            )}
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
                        <form onSubmit={bulkQuestions.length > 0 ? handleBulkSubmit : handleSubmit} className="bg-white rounded-xl shadow-lg p-6">
                            <h2 className="text-xl font-bold text-gray-800 mb-4">
                                Question Entry {bulkQuestions.length > 0 && `(${currentBulkIndex + 1} of ${bulkQuestions.length})`}
                            </h2>
                            
                            {/* Question Text */}
                            <div className="mb-4">
                                <label className="block text-sm font-bold text-gray-700 mb-2">
                                    Question Content *
                                    <span className="text-xs font-normal text-gray-500 ml-2">
                                        (Text, images, and graphs appear together)
                                    </span>
                                </label>
                                
                                {/* Rich Content Display Area */}
                                <div className="border-2 border-gray-300 rounded-lg bg-white min-h-[200px] max-h-[600px] overflow-y-auto p-4 focus-within:ring-2 focus-within:ring-green-500 focus-within:border-transparent">
                                    {/* Render content with images inline */}
                                    <div className="whitespace-pre-wrap">
                                        {questionText.split(/(\[IMAGE:\d+(?:\.\d+)?:(?:\d+x\d+|\d+)px\])/g).map((part, index) => {
                                            // Support both old format [IMAGE:id:widthpx] and new format [IMAGE:id:widthxheightpx]
                                            // Also support float IDs like 1730736726759.794
                                            const imageMatchNew = part.match(/\[IMAGE:([\d.]+):(\d+)x(\d+)px\]/);
                                            const imageMatchOld = part.match(/\[IMAGE:([\d.]+):(\d+)px\]/);
                                            
                                            if (imageMatchNew || imageMatchOld) {
                                                const imageId = parseFloat(imageMatchNew ? imageMatchNew[1] : imageMatchOld[1]);
                                                const imageWidth = parseInt(imageMatchNew ? imageMatchNew[2] : imageMatchOld[2]);
                                                const imageHeight = imageMatchNew ? parseInt(imageMatchNew[3]) : null;
                                                const image = questionInlineImages.find(img => Math.abs(img.id - imageId) < 0.001);
                                                
                                                if (image) {
                                                    return (
                                                        <div key={index} className="inline-block my-2 relative group">
                                                            <img 
                                                                src={image.url} 
                                                                alt={image.name} 
                                                                style={{ 
                                                                    width: `${imageWidth}px`, 
                                                                    height: imageHeight ? `${imageHeight}px` : 'auto',
                                                                    maxWidth: '100%' 
                                                                }}
                                                                className="border-2 border-blue-300 rounded shadow-sm"
                                                            />
                                                            <div className="absolute top-0 right-0 opacity-0 group-hover:opacity-100 transition-opacity bg-white rounded-bl px-2 py-1 shadow">
                                                                <button
                                                                    type="button"
                                                                    onClick={() => removeImage(imageId)}
                                                                    className="text-red-600 hover:text-red-800 text-xs font-bold"
                                                                    title="Remove image"
                                                                >
                                                                    ✕
                                                                </button>
                                                            </div>
                                                        </div>
                                                    );
                                                }
                                                // If image not found, hide the placeholder completely (return nothing)
                                                return null;
                                            }
                                            return <span key={index}>{part}</span>;
                                        })}
                                        {questionText.length === 0 && (
                                            <span className="text-gray-400">Type your question here or drag & drop images...</span>
                                        )}
                                    </div>
                                </div>
                                
                                {/* Hidden textarea for form submission */}
                                <textarea
                                    ref={questionTextareaRef}
                                    value={questionText}
                                    onChange={(e) => setQuestionText(e.target.value)}
                                    onDragOver={handleTextareaDragOver}
                                    onDrop={handleQuestionDrop}
                                    className="w-full px-4 py-3 mt-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition font-mono text-sm"
                                    rows="4"
                                    placeholder="📝 Raw content (edit text and image placeholders here)"
                                    required
                                />
                            </div>

                            {/* Quick Image Manager - Compact Version */}
                            {questionInlineImages.length > 0 && (
                                <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                                    <details>
                                        <summary className="cursor-pointer font-semibold text-blue-900 text-sm">
                                            📸 Manage Images ({questionInlineImages.length}) - Click to expand
                                        </summary>
                                        <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-2">
                                            {questionInlineImages.map((img) => (
                                                <div key={img.id} className="bg-white border border-gray-300 rounded p-2">
                                                    <img src={img.url} alt={img.name} className="w-full h-20 object-contain mb-1 border rounded" />
                                                    <p className="text-xs text-gray-600 truncate mb-1">{img.name}</p>
                                                    <div className="text-xs text-gray-600 mb-1">W: {img.width}px | H: {img.height}px</div>
                                                    <input 
                                                        type="range" 
                                                        min="100" 
                                                        max="800" 
                                                        step="50"
                                                        value={img.width} 
                                                        onChange={(e) => updateImageWidth(img.id, parseInt(e.target.value), 'question')}
                                                        className="w-full h-1 mb-1"
                                                        title={`Width: ${img.width}px`}
                                                    />
                                                    <input 
                                                        type="range" 
                                                        min="50" 
                                                        max="600" 
                                                        step="50"
                                                        value={img.height} 
                                                        onChange={(e) => updateImageHeight(img.id, parseInt(e.target.value), 'question')}
                                                        className="w-full h-1"
                                                        title={`Height: ${img.height}px`}
                                                    />
                                                    <div className="flex gap-1 mt-1">
                                                        <button 
                                                            type="button"
                                                            onClick={() => insertInlineImage(img.id, 'question')}
                                                            className="flex-1 bg-green-600 hover:bg-green-700 text-white text-xs px-2 py-1 rounded"
                                                        >
                                                            Insert
                                                        </button>
                                                        <button 
                                                            type="button"
                                                            onClick={() => removeImage(img.id)}
                                                            className="bg-red-600 hover:bg-red-700 text-white text-xs px-2 py-1 rounded"
                                                        >
                                                            ✕
                                                        </button>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </details>
                                </div>
                            )}

                            {/* Question Tools */}
                            <div className="mb-4 flex flex-wrap gap-3">
                                {/* File Upload */}
                                <label className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg cursor-pointer transition flex items-center space-x-2">
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                    </svg>
                                    <span>Upload Image</span>
                                    <input type="file" accept="image/*" multiple onChange={handleFileUpload} className="hidden" />
                                </label>

                                {/* Drawing Tool */}
                                <button
                                    type="button"
                                    onClick={() => setShowDrawingTool(!showDrawingTool)}
                                    className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition flex items-center space-x-2"
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                                    </svg>
                                    <span>{showDrawingTool ? 'Hide Drawing' : 'Drawing Tools'}</span>
                                </button>

                                {/* Graph Paper Toggle */}
                                <button
                                    type="button"
                                    onClick={() => {
                                        setShowGraphPaper(!showGraphPaper);
                                        if (!showDrawingTool) setShowDrawingTool(true);
                                    }}
                                    className={`${showGraphPaper ? 'bg-green-600' : 'bg-gray-600'} hover:bg-green-700 text-white px-4 py-2 rounded-lg transition flex items-center space-x-2`}
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                    </svg>
                                    <span>{showGraphPaper ? 'Graph ON' : 'Graph Paper'}</span>
                                </button>
                            </div>

                            {/* Drawing Tool Interface */}
                            {showDrawingTool && (
                                <div className="mb-4 border-2 border-purple-200 rounded-lg p-4 bg-purple-50">
                                    <div className="flex flex-wrap items-center gap-3 mb-3">
                                        <span className="font-bold text-gray-700">Tools:</span>
                                        
                                        {/* Drawing Tools */}
                                        <button type="button" onClick={() => setDrawingTool('pen')} className={`px-3 py-1 rounded ${drawingTool === 'pen' ? 'bg-purple-600 text-white' : 'bg-white'}`}>Pen</button>
                                        <button type="button" onClick={() => setDrawingTool('eraser')} className={`px-3 py-1 rounded ${drawingTool === 'eraser' ? 'bg-purple-600 text-white' : 'bg-white'}`}>Eraser</button>
                                        
                                        {/* Color Picker */}
                                        <div className="flex items-center space-x-2">
                                            <span className="text-sm">Color:</span>
                                            <input type="color" value={drawingColor} onChange={(e) => setDrawingColor(e.target.value)} className="w-10 h-8 rounded cursor-pointer" />
                                        </div>
                                        
                                        {/* Width Slider */}
                                        <div className="flex items-center space-x-2">
                                            <span className="text-sm">Width:</span>
                                            <input type="range" min="1" max="10" value={drawingWidth} onChange={(e) => setDrawingWidth(e.target.value)} className="w-20" />
                                            <span className="text-sm">{drawingWidth}px</span>
                                        </div>
                                        
                                        {/* Action Buttons */}
                                        <button type="button" onClick={clearCanvas} className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600">Clear</button>
                                        <button type="button" onClick={saveDrawing} className="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700">Save Drawing</button>
                                    </div>
                                    
                                    {/* Canvas */}
                                    <canvas
                                        ref={canvasRef}
                                        onMouseDown={startDrawing}
                                        onMouseMove={draw}
                                        onMouseUp={stopDrawing}
                                        onMouseLeave={stopDrawing}
                                        className="mx-auto border-2 border-gray-300 rounded cursor-crosshair bg-white"
                                        style={{ width: '794px', height: '1123px', maxWidth: '100%' }}
                                    />
                                </div>
                            )}

                            {/* Uploaded Images Display */}
                            {uploadedImages.length > 0 && (
                                <div className="mb-4">
                                    <label className="block text-sm font-bold text-gray-700 mb-2">
                                        Attached Images ({uploadedImages.length})
                                    </label>
                                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                                        {uploadedImages.map((image) => (
                                            <div key={image.id} className="relative group">
                                                <img src={image.url} alt={image.name} className="w-full h-32 object-cover rounded-lg border-2 border-gray-300" />
                                                <button
                                                    type="button"
                                                    onClick={() => removeImage(image.id)}
                                                    className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition"
                                                >
                                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                                    </svg>
                                                </button>
                                                <p className="text-xs text-gray-600 mt-1 truncate">{image.name}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

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
                                    Answer/Solution Content *
                                    <span className="text-xs font-normal text-gray-500 ml-2">
                                        (Text, images, and graphs appear together)
                                    </span>
                                </label>
                                
                                {/* Rich Content Display Area */}
                                <div className="border-2 border-gray-300 rounded-lg bg-white min-h-[200px] max-h-[600px] overflow-y-auto p-4 focus-within:ring-2 focus-within:ring-green-500 focus-within:border-transparent">
                                    {/* Render content with images inline */}
                                    <div className="whitespace-pre-wrap">
                                        {answerText.split(/(\[IMAGE:\d+(?:\.\d+)?:(?:\d+x\d+|\d+)px\])/g).map((part, index) => {
                                            // Support both old format [IMAGE:id:widthpx] and new format [IMAGE:id:widthxheightpx]
                                            // Also support float IDs like 1730736726759.794
                                            const imageMatchNew = part.match(/\[IMAGE:([\d.]+):(\d+)x(\d+)px\]/);
                                            const imageMatchOld = part.match(/\[IMAGE:([\d.]+):(\d+)px\]/);
                                            
                                            if (imageMatchNew || imageMatchOld) {
                                                const imageId = parseFloat(imageMatchNew ? imageMatchNew[1] : imageMatchOld[1]);
                                                const imageWidth = parseInt(imageMatchNew ? imageMatchNew[2] : imageMatchOld[2]);
                                                const imageHeight = imageMatchNew ? parseInt(imageMatchNew[3]) : null;
                                                const image = answerInlineImages.find(img => Math.abs(img.id - imageId) < 0.001);
                                                
                                                if (image) {
                                                    return (
                                                        <div key={index} className="inline-block my-2 relative group">
                                                            <img 
                                                                src={image.url} 
                                                                alt={image.name} 
                                                                style={{ 
                                                                    width: `${imageWidth}px`, 
                                                                    height: imageHeight ? `${imageHeight}px` : 'auto',
                                                                    maxWidth: '100%' 
                                                                }}
                                                                className="border-2 border-orange-300 rounded shadow-sm"
                                                            />
                                                            <div className="absolute top-0 right-0 opacity-0 group-hover:opacity-100 transition-opacity bg-white rounded-bl px-2 py-1 shadow">
                                                                <button
                                                                    type="button"
                                                                    onClick={() => removeAnswerImage(imageId)}
                                                                    className="text-red-600 hover:text-red-800 text-xs font-bold"
                                                                    title="Remove image"
                                                                >
                                                                    ✕
                                                                </button>
                                                            </div>
                                                        </div>
                                                    );
                                                }
                                                // If image not found, hide the placeholder completely (return nothing)
                                                return null;
                                            }
                                            return <span key={index}>{part}</span>;
                                        })}
                                        {answerText.length === 0 && (
                                            <span className="text-gray-400">Type your answer/solution here or drag & drop images...</span>
                                        )}
                                    </div>
                                </div>                                {/* Hidden textarea for form submission */}
                                <textarea
                                    ref={answerTextareaRef}
                                    value={answerText}
                                    onChange={(e) => setAnswerText(e.target.value)}
                                    onDragOver={handleTextareaDragOver}
                                    onDrop={handleAnswerDrop}
                                    className="w-full px-4 py-3 mt-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition font-mono text-sm"
                                    rows="4"
                                    placeholder="📝 Raw content (edit text and image placeholders here)"
                                    required
                                />
                                <p className="text-xs text-gray-500 mt-1">
                                    💡 Start with "Solution:" or "Answer:" to clearly identify the solution
                                </p>
                            </div>

                            {/* Quick Image Manager for Answer - Compact Version */}
                            {answerInlineImages.length > 0 && (
                                <div className="mb-4 p-3 bg-orange-50 border border-orange-200 rounded-lg">
                                    <details>
                                        <summary className="cursor-pointer font-semibold text-orange-900 text-sm">
                                            📸 Manage Answer Images ({answerInlineImages.length}) - Click to expand
                                        </summary>
                                        <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-2">
                                            {answerInlineImages.map((img) => (
                                                <div key={img.id} className="bg-white border border-gray-300 rounded p-2">
                                                    <img src={img.url} alt={img.name} className="w-full h-20 object-contain mb-1 border rounded" />
                                                    <p className="text-xs text-gray-600 truncate mb-1">{img.name}</p>
                                                    <div className="text-xs text-gray-600 mb-1">W: {img.width}px | H: {img.height}px</div>
                                                    <input 
                                                        type="range" 
                                                        min="100" 
                                                        max="800" 
                                                        step="50"
                                                        value={img.width} 
                                                        onChange={(e) => updateImageWidth(img.id, parseInt(e.target.value), 'answer')}
                                                        className="w-full h-1 mb-1"
                                                        title={`Width: ${img.width}px`}
                                                    />
                                                    <input 
                                                        type="range" 
                                                        min="50" 
                                                        max="600" 
                                                        step="50"
                                                        value={img.height} 
                                                        onChange={(e) => updateImageHeight(img.id, parseInt(e.target.value), 'answer')}
                                                        className="w-full h-1"
                                                        title={`Height: ${img.height}px`}
                                                    />
                                                    <div className="flex gap-1 mt-1">
                                                        <button 
                                                            type="button"
                                                            onClick={() => insertInlineImage(img.id, 'answer')}
                                                            className="flex-1 bg-green-600 hover:bg-green-700 text-white text-xs px-2 py-1 rounded"
                                                        >
                                                            Insert
                                                        </button>
                                                        <button 
                                                            type="button"
                                                            onClick={() => removeAnswerImage(img.id)}
                                                            className="bg-red-600 hover:bg-red-700 text-white text-xs px-2 py-1 rounded"
                                                        >
                                                            ✕
                                                        </button>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </details>
                                </div>
                            )}

                            {/* Answer Tools */}
                            <div className="mb-4 flex flex-wrap gap-3">
                                {/* File Upload for Answer */}
                                <label className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg cursor-pointer transition flex items-center space-x-2">
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                    </svg>
                                    <span>Upload Answer Image</span>
                                    <input type="file" accept="image/*" multiple onChange={handleAnswerFileUpload} className="hidden" />
                                </label>

                                {/* Drawing Tool for Answer */}
                                <button
                                    type="button"
                                    onClick={() => setShowAnswerDrawingTool(!showAnswerDrawingTool)}
                                    className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition flex items-center space-x-2"
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                                    </svg>
                                    <span>{showAnswerDrawingTool ? 'Hide Drawing' : 'Answer Drawing'}</span>
                                </button>

                                {/* Graph Paper Toggle for Answer */}
                                <button
                                    type="button"
                                    onClick={() => {
                                        setShowAnswerGraphPaper(!showAnswerGraphPaper);
                                        if (!showAnswerDrawingTool) setShowAnswerDrawingTool(true);
                                    }}
                                    className={`${showAnswerGraphPaper ? 'bg-green-600' : 'bg-gray-600'} hover:bg-green-700 text-white px-4 py-2 rounded-lg transition flex items-center space-x-2`}
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                    </svg>
                                    <span>{showAnswerGraphPaper ? 'Graph ON' : 'Answer Graph'}</span>
                                </button>
                            </div>

                            {/* Answer Drawing Tool Interface */}
                            {showAnswerDrawingTool && (
                                <div className="mb-4 border-2 border-indigo-200 rounded-lg p-4 bg-indigo-50">
                                    <div className="flex flex-wrap items-center gap-3 mb-3">
                                        <span className="font-bold text-gray-700">Answer Tools:</span>
                                        
                                        <button type="button" onClick={() => setAnswerDrawingTool('pen')} className={`px-3 py-1 rounded ${answerDrawingTool === 'pen' ? 'bg-indigo-600 text-white' : 'bg-white'}`}>Pen</button>
                                        <button type="button" onClick={() => setAnswerDrawingTool('eraser')} className={`px-3 py-1 rounded ${answerDrawingTool === 'eraser' ? 'bg-indigo-600 text-white' : 'bg-white'}`}>Eraser</button>
                                        
                                        <div className="flex items-center space-x-2">
                                            <span className="text-sm">Color:</span>
                                            <input type="color" value={answerDrawingColor} onChange={(e) => setAnswerDrawingColor(e.target.value)} className="w-10 h-8 rounded cursor-pointer" />
                                        </div>
                                        
                                        <div className="flex items-center space-x-2">
                                            <span className="text-sm">Width:</span>
                                            <input type="range" min="1" max="10" value={answerDrawingWidth} onChange={(e) => setAnswerDrawingWidth(e.target.value)} className="w-20" />
                                            <span className="text-sm">{answerDrawingWidth}px</span>
                                        </div>
                                        
                                        <button type="button" onClick={clearAnswerCanvas} className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600">Clear</button>
                                        <button type="button" onClick={saveAnswerDrawing} className="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700">Save Drawing</button>
                                    </div>
                                    
                                    <canvas
                                        ref={answerCanvasRef}
                                        onMouseDown={startAnswerDrawing}
                                        onMouseMove={drawAnswer}
                                        onMouseUp={stopAnswerDrawing}
                                        onMouseLeave={stopAnswerDrawing}
                                        className="mx-auto border-2 border-gray-300 rounded cursor-crosshair bg-white"
                                        style={{ width: '794px', height: '1123px', maxWidth: '100%' }}
                                    />
                                </div>
                            )}

                            {/* Uploaded Answer Images Display */}
                            {uploadedAnswerImages.length > 0 && (
                                <div className="mb-4">
                                    <label className="block text-sm font-bold text-gray-700 mb-2">
                                        Attached Answer Images ({uploadedAnswerImages.length})
                                    </label>
                                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                                        {uploadedAnswerImages.map((image) => (
                                            <div key={image.id} className="relative group">
                                                <img src={image.url} alt={image.name} className="w-full h-32 object-cover rounded-lg border-2 border-orange-300" />
                                                <button
                                                    type="button"
                                                    onClick={() => removeAnswerImage(image.id)}
                                                    className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition"
                                                >
                                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                                    </svg>
                                                </button>
                                                <p className="text-xs text-gray-600 mt-1 truncate">{image.name}</p>
                                            </div>
                                        ))}
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

                {/* Statistics Tab Content */}
                {activeTab === 'stats' && (() => {
                    const stats = getStatistics();
                    const filteredQuestions = getFilteredQuestions();
                    
                    return (
                        <div>
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
                                    <select value={filterSubject} onChange={(e) => setFilterSubject(e.target.value)} className="px-4 py-2 border rounded-lg">
                                        <option value="">All Subjects</option>
                                        {Object.keys(subjects).map(s => <option key={s} value={s}>{s}</option>)}
                                    </select>
                                    <select value={filterPaper} onChange={(e) => setFilterPaper(e.target.value)} className="px-4 py-2 border rounded-lg">
                                        <option value="">All Papers</option>
                                        {filterSubject && subjects[filterSubject]?.papers.map(p => <option key={p} value={p}>{p}</option>)}
                                    </select>
                                    <select value={filterTopic} onChange={(e) => setFilterTopic(e.target.value)} className="px-4 py-2 border rounded-lg">
                                        <option value="">All Topics</option>
                                        {filterSubject && subjects[filterSubject]?.topics.map(t => <option key={t} value={t}>{t}</option>)}
                                    </select>
                                    <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)} className="px-4 py-2 border rounded-lg">
                                        <option value="all">All Status</option>
                                        <option value="active">Active Only</option>
                                        <option value="inactive">Inactive Only</option>
                                    </select>
                                </div>
                                <button onClick={() => {setFilterSubject(''); setFilterPaper(''); setFilterTopic(''); setFilterStatus('all');}} className="mt-4 text-blue-600 hover:text-blue-700 font-semibold">Clear Filters</button>
                            </div>

                            {/* By Subject */}
                            <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
                                <h3 className="text-lg font-bold mb-4">Questions by Subject</h3>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    {Object.entries(stats.bySubject).map(([subject, count]) => (
                                        <div key={subject} className="border-2 border-gray-200 rounded-lg p-4 hover:border-green-500 transition">
                                            <p className="text-gray-600 text-sm">{subject}</p>
                                            <p className="text-2xl font-bold text-green-600">{count}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* By Paper */}
                            <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
                                <h3 className="text-lg font-bold mb-4">Questions by Paper</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                                    {Object.entries(stats.byPaper).map(([paper, count]) => (
                                        <div key={paper} className="border border-gray-200 rounded-lg p-3 flex justify-between items-center">
                                            <span className="text-sm text-gray-700">{paper}</span>
                                            <span className="font-bold text-blue-600">{count}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* By Topic */}
                            <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
                                <h3 className="text-lg font-bold mb-4">Questions by Topic</h3>
                                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                                    {Object.entries(stats.byTopic).map(([topic, count]) => (
                                        <div key={topic} className="border border-gray-200 rounded-lg p-3">
                                            <p className="text-xs text-gray-600">{topic}</p>
                                            <p className="text-lg font-bold text-purple-600">{count}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Filtered Questions List */}
                            <div className="bg-white rounded-xl shadow-lg p-6">
                                <h3 className="text-lg font-bold mb-4">Questions List ({filteredQuestions.length})</h3>
                                <div className="space-y-3 max-h-96 overflow-y-auto">
                                    {filteredQuestions.map(q => (
                                        <div key={q.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
                                            <div className="flex justify-between items-start mb-2">
                                                <div className="flex-1">
                                                    <span className={`inline-block px-2 py-1 rounded text-xs font-bold ${q.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                                        {q.status}
                                                    </span>
                                                    <span className="ml-2 text-sm font-semibold text-gray-700">{q.subject} - {q.paper}</span>
                                                    {q.topic === 'Unknown' && <span className="ml-2 text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded">⚠️ Unknown Topic</span>}
                                                </div>
                                                <span className="text-sm font-bold text-blue-600">{q.marks} marks</span>
                                            </div>
                                            <p className="text-sm text-gray-600 line-clamp-2">{q.questionText}</p>
                                            <p className="text-xs text-gray-500 mt-1">Topic: {q.topic} | Section: {q.section}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    );
                })()}
            </div>
        </div>
    );
}