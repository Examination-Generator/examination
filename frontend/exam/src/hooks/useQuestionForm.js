import { useState, useRef } from 'react';

export function useQuestionForm() {
    const [questionText, setQuestionText] = useState('');
    const [answerText, setAnswerText] = useState('');
    const [marks, setMarks] = useState('');
    const [isQuestionActive, setIsQuestionActive] = useState(true);
    const [isNested, setIsNested] = useState(false);
    const [isEssayQuestion, setIsEssayQuestion] = useState(false);
    const [isGraphQuestion, setIsGraphQuestion] = useState(false);
    const [isMapQuestion, setIsMapQuestion] = useState(false);

    // Inline images
    const [questionInlineImages, setQuestionInlineImages] = useState([]);
    const [answerInlineImages, setAnswerInlineImages] = useState([]);
    const [questionImagePositions, setQuestionImagePositions] = useState({});
    const [answerImagePositions, setAnswerImagePositions] = useState({});

    // Answer lines and working spaces
    const [questionAnswerLines, setQuestionAnswerLines] = useState([]);
    const [answerAnswerLines, setAnswerAnswerLines] = useState([]);
    const [questionWorkingSpaces, setQuestionWorkingSpaces] = useState([]);
    const [answerWorkingSpaces, setAnswerWorkingSpaces] = useState([]);

    // Textarea refs
    const questionTextareaRef = useRef(null);
    const answerTextareaRef = useRef(null);

    const resetForm = () => {
        setQuestionText('');
        setAnswerText('');
        setMarks('');
        setIsQuestionActive(true);
        setIsNested(false);
        setIsEssayQuestion(false);
        setIsGraphQuestion(false);
        setIsMapQuestion(false);
        setQuestionInlineImages([]);
        setAnswerInlineImages([]);
        setQuestionImagePositions({});
        setAnswerImagePositions({});
        setQuestionAnswerLines([]);
        setAnswerAnswerLines([]);
        setQuestionWorkingSpaces([]);
        setAnswerWorkingSpaces([]);
    };

    return {
        // Text
        questionText, setQuestionText,
        answerText, setAnswerText,
        marks, setMarks,
        // Flags
        isQuestionActive, setIsQuestionActive,
        isNested, setIsNested,
        isEssayQuestion, setIsEssayQuestion,
        isGraphQuestion, setIsGraphQuestion,
        isMapQuestion, setIsMapQuestion,
        // Images
        questionInlineImages, setQuestionInlineImages,
        answerInlineImages, setAnswerInlineImages,
        questionImagePositions, setQuestionImagePositions,
        answerImagePositions, setAnswerImagePositions,
        // Lines & spaces
        questionAnswerLines, setQuestionAnswerLines,
        answerAnswerLines, setAnswerAnswerLines,
        questionWorkingSpaces, setQuestionWorkingSpaces,
        answerWorkingSpaces, setAnswerWorkingSpaces,
        // Refs
        questionTextareaRef,
        answerTextareaRef,
        // Actions
        resetForm,
    };
}