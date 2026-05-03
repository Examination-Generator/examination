
import { useState, useRef, useCallback } from 'react';

export function useEditForm() {
    const [selectedQuestion, setSelectedQuestion] = useState(null);
    const [editQuestionText, setEditQuestionText] = useState('');
    const [editAnswerText, setEditAnswerText] = useState('');
    const [editMarks, setEditMarks] = useState('');
    const [editTopic, setEditTopic] = useState('');
    const [editSection, setEditSection] = useState('');
    const [editIsActive, setEditIsActive] = useState(true);
    const [editIsNested, setEditIsNested] = useState(false);
    const [editIsEssayQuestion, setEditIsEssayQuestion] = useState(false);
    const [editIsGraphQuestion, setEditIsGraphQuestion] = useState(false);
    const [editIsMapQuestion, setEditIsMapQuestion] = useState(false);

    const [editQuestionInlineImages, setEditQuestionInlineImages] = useState([]);
    const [editAnswerInlineImages, setEditAnswerInlineImages] = useState([]);
    const [editQuestionImagePositions, setEditQuestionImagePositions] = useState({});
    const [editAnswerImagePositions, setEditAnswerImagePositions] = useState({});
    const [editQuestionAnswerLines, setEditQuestionAnswerLines] = useState([]);
    const [editAnswerAnswerLines, setEditAnswerAnswerLines] = useState([]);
    const [editQuestionWorkingSpaces, setEditQuestionWorkingSpaces] = useState([]);
    const [editAnswerWorkingSpaces, setEditAnswerWorkingSpaces] = useState([]);
    const [editQuestionTopics, setEditQuestionTopics] = useState([]);
    const [editQuestionSections, setEditQuestionSections] = useState([]);

    const editQuestionTextareaRef = useRef(null);
    const editAnswerTextareaRef = useRef(null);

    const loadQuestion = useCallback((question) => {
        if (!question) {
            clearEdit();
            return;
        }
        setSelectedQuestion(question);
        setEditQuestionText(question.question_text || '');
        setEditAnswerText(question.answer_text || '');
        setEditMarks(question.marks || '');
        setEditTopic(question.topic || '');
        setEditSection(question.section || '');
        setEditIsActive(question.is_active !== false);
        setEditIsNested(question.is_nested === true);
        setEditIsEssayQuestion(question.is_essay_question === true);
        setEditIsGraphQuestion(question.is_graph_question === true);
        setEditIsMapQuestion(question.is_map_question === true);
        setEditQuestionInlineImages(question.question_inline_images || []);
        setEditAnswerInlineImages(question.answer_inline_images || []);
        setEditQuestionImagePositions(question.question_image_positions || {});
        setEditAnswerImagePositions(question.answer_image_positions || {});
        setEditQuestionAnswerLines(question.question_answer_lines || []);
        setEditAnswerAnswerLines(question.answer_answer_lines || []);
        setEditQuestionWorkingSpaces(question.question_working_spaces || []);
        setEditAnswerWorkingSpaces(question.answer_working_spaces || []);
    }, []);

    const clearEdit = useCallback(() => {
        setSelectedQuestion(null);
        setEditQuestionText('');
        setEditAnswerText('');
        setEditMarks('');
        setEditTopic('');
        setEditSection('');
        setEditIsActive(true);
        setEditIsNested(false);
        setEditIsEssayQuestion(false);
        setEditIsGraphQuestion(false);
        setEditIsMapQuestion(false);
        setEditQuestionInlineImages([]);
        setEditAnswerInlineImages([]);
        setEditQuestionImagePositions({});
        setEditAnswerImagePositions({});
        setEditQuestionAnswerLines([]);
        setEditAnswerAnswerLines([]);
        setEditQuestionWorkingSpaces([]);
        setEditAnswerWorkingSpaces([]);
        setEditQuestionTopics([]);
        setEditQuestionSections([]);
    }, []);

    return {
        selectedQuestion,
        editQuestionText, setEditQuestionText,
        editAnswerText, setEditAnswerText,
        editMarks, setEditMarks,
        editTopic, setEditTopic,
        editSection, setEditSection,
        editIsActive, setEditIsActive,
        editIsNested, setEditIsNested,
        editIsEssayQuestion, setEditIsEssayQuestion,
        editIsGraphQuestion, setEditIsGraphQuestion,
        editIsMapQuestion, setEditIsMapQuestion,
        editQuestionInlineImages, setEditQuestionInlineImages,
        editAnswerInlineImages, setEditAnswerInlineImages,
        editQuestionImagePositions, setEditQuestionImagePositions,
        editAnswerImagePositions, setEditAnswerImagePositions,
        editQuestionAnswerLines, setEditQuestionAnswerLines,
        editAnswerAnswerLines, setEditAnswerAnswerLines,
        editQuestionWorkingSpaces, setEditQuestionWorkingSpaces,
        editAnswerWorkingSpaces, setEditAnswerWorkingSpaces,
        editQuestionTopics, setEditQuestionTopics,
        editQuestionSections, setEditQuestionSections,
        editQuestionTextareaRef,
        editAnswerTextareaRef,
        loadQuestion,
        clearEdit,
    };
}