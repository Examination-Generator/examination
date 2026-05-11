import { useReducer, useRef, useCallback, useMemo } from 'react';

// ---------------------------------------------------------------------------
// All edit-form fields live in a single state object. This means loadQuestion
// and clearEdit each fire exactly ONE state update (one re-render) instead of
// the original 20 individual setState calls that could cascade into 20 renders.
// ---------------------------------------------------------------------------

const INITIAL_STATE = {
    selectedQuestion:           null,
    editQuestionText:           '',
    editAnswerText:             '',
    editMarks:                  '',
    editTopic:                  '',
    editSection:                '',
    editIsActive:               true,
    editIsNested:               false,
    editIsEssayQuestion:        false,
    editIsGraphQuestion:        false,
    editIsMapQuestion:          false,
    editQuestionInlineImages:   [],
    editAnswerInlineImages:     [],
    editQuestionImagePositions: {},
    editAnswerImagePositions:   {},
    editQuestionAnswerLines:    [],
    editAnswerAnswerLines:      [],
    editQuestionWorkingSpaces:  [],
    editAnswerWorkingSpaces:    [],
    editQuestionTopics:         [],
    editQuestionSections:       [],
};

function editFormReducer(state, action) {
    switch (action.type) {
        // Load a question — replaces the entire form state in one shot
        case 'LOAD_QUESTION': {
            const q = action.question;
            return {
                selectedQuestion:           q,
                editQuestionText:           q.question_text           || '',
                editAnswerText:             q.answer_text             || '',
                editMarks:                  q.marks                   || '',
                editTopic:                  q.topic                   || '',
                editSection:                q.section                 || '',
                editIsActive:               q.is_active               !== false,
                editIsNested:               q.is_nested               === true,
                editIsEssayQuestion:        q.is_essay_question       === true,
                editIsGraphQuestion:        q.is_graph_question       === true,
                editIsMapQuestion:          q.is_map_question         === true,
                editQuestionInlineImages:   q.question_inline_images  || [],
                editAnswerInlineImages:     q.answer_inline_images    || [],
                editQuestionImagePositions: q.question_image_positions || {},
                editAnswerImagePositions:   q.answer_image_positions  || {},
                editQuestionAnswerLines:    q.question_answer_lines   || [],
                editAnswerAnswerLines:      q.answer_answer_lines     || [],
                editQuestionWorkingSpaces:  q.question_working_spaces || [],
                editAnswerWorkingSpaces:    q.answer_working_spaces   || [],
                editQuestionTopics:         [],
                editQuestionSections:       [],
            };
        }

        // Clear the form — resets to initial state in one shot
        case 'CLEAR':
            return INITIAL_STATE;

        
        case 'SET_FIELD':
            return { ...state, [action.field]: action.value };

        
        case 'SET_FIELD_FN':
            return { ...state, [action.field]: action.updater(state[action.field]) };

        default:
            return state;
    }
}

export function useEditForm() {
    const [state, dispatch] = useReducer(editFormReducer, INITIAL_STATE);

    const editQuestionTextareaRef = useRef(null);
    const editAnswerTextareaRef   = useRef(null);

    
    const loadQuestion = useCallback((question) => {
        if (!question) {
            dispatch({ type: 'CLEAR' });
            return;
        }
        dispatch({ type: 'LOAD_QUESTION', question });
    }, []);

    
    const clearEdit = useCallback(() => {
        dispatch({ type: 'CLEAR' });
    }, []);

    
    const makeFieldSetter = useCallback((field) => {
        return (valueOrUpdater) => {
            if (typeof valueOrUpdater === 'function') {
                dispatch({ type: 'SET_FIELD_FN', field, updater: valueOrUpdater });
            } else {
                dispatch({ type: 'SET_FIELD', field, value: valueOrUpdater });
            }
        };
    }, []);

    // Stable setter references — created once, never recreated
    const setEditQuestionText           = useMemo(() => makeFieldSetter('editQuestionText'),           [makeFieldSetter]);
    const setEditAnswerText             = useMemo(() => makeFieldSetter('editAnswerText'),             [makeFieldSetter]);
    const setEditMarks                  = useMemo(() => makeFieldSetter('editMarks'),                  [makeFieldSetter]);
    const setEditTopic                  = useMemo(() => makeFieldSetter('editTopic'),                  [makeFieldSetter]);
    const setEditSection                = useMemo(() => makeFieldSetter('editSection'),                [makeFieldSetter]);
    const setEditIsActive               = useMemo(() => makeFieldSetter('editIsActive'),               [makeFieldSetter]);
    const setEditIsNested               = useMemo(() => makeFieldSetter('editIsNested'),               [makeFieldSetter]);
    const setEditIsEssayQuestion        = useMemo(() => makeFieldSetter('editIsEssayQuestion'),        [makeFieldSetter]);
    const setEditIsGraphQuestion        = useMemo(() => makeFieldSetter('editIsGraphQuestion'),        [makeFieldSetter]);
    const setEditIsMapQuestion          = useMemo(() => makeFieldSetter('editIsMapQuestion'),          [makeFieldSetter]);
    const setEditQuestionInlineImages   = useMemo(() => makeFieldSetter('editQuestionInlineImages'),   [makeFieldSetter]);
    const setEditAnswerInlineImages     = useMemo(() => makeFieldSetter('editAnswerInlineImages'),     [makeFieldSetter]);
    const setEditQuestionImagePositions = useMemo(() => makeFieldSetter('editQuestionImagePositions'), [makeFieldSetter]);
    const setEditAnswerImagePositions   = useMemo(() => makeFieldSetter('editAnswerImagePositions'),   [makeFieldSetter]);
    const setEditQuestionAnswerLines    = useMemo(() => makeFieldSetter('editQuestionAnswerLines'),    [makeFieldSetter]);
    const setEditAnswerAnswerLines      = useMemo(() => makeFieldSetter('editAnswerAnswerLines'),      [makeFieldSetter]);
    const setEditQuestionWorkingSpaces  = useMemo(() => makeFieldSetter('editQuestionWorkingSpaces'),  [makeFieldSetter]);
    const setEditAnswerWorkingSpaces    = useMemo(() => makeFieldSetter('editAnswerWorkingSpaces'),    [makeFieldSetter]);
    const setEditQuestionTopics         = useMemo(() => makeFieldSetter('editQuestionTopics'),         [makeFieldSetter]);
    const setEditQuestionSections       = useMemo(() => makeFieldSetter('editQuestionSections'),       [makeFieldSetter]);

    
    return useMemo(() => ({
        // State values (spread from reducer state)
        selectedQuestion:           state.selectedQuestion,
        editQuestionText:           state.editQuestionText,
        editAnswerText:             state.editAnswerText,
        editMarks:                  state.editMarks,
        editTopic:                  state.editTopic,
        editSection:                state.editSection,
        editIsActive:               state.editIsActive,
        editIsNested:               state.editIsNested,
        editIsEssayQuestion:        state.editIsEssayQuestion,
        editIsGraphQuestion:        state.editIsGraphQuestion,
        editIsMapQuestion:          state.editIsMapQuestion,
        editQuestionInlineImages:   state.editQuestionInlineImages,
        editAnswerInlineImages:     state.editAnswerInlineImages,
        editQuestionImagePositions: state.editQuestionImagePositions,
        editAnswerImagePositions:   state.editAnswerImagePositions,
        editQuestionAnswerLines:    state.editQuestionAnswerLines,
        editAnswerAnswerLines:      state.editAnswerAnswerLines,
        editQuestionWorkingSpaces:  state.editQuestionWorkingSpaces,
        editAnswerWorkingSpaces:    state.editAnswerWorkingSpaces,
        editQuestionTopics:         state.editQuestionTopics,
        editQuestionSections:       state.editQuestionSections,

        // Stable setters — identical API to the original useState setters
        setEditQuestionText,
        setEditAnswerText,
        setEditMarks,
        setEditTopic,
        setEditSection,
        setEditIsActive,
        setEditIsNested,
        setEditIsEssayQuestion,
        setEditIsGraphQuestion,
        setEditIsMapQuestion,
        setEditQuestionInlineImages,
        setEditAnswerInlineImages,
        setEditQuestionImagePositions,
        setEditAnswerImagePositions,
        setEditQuestionAnswerLines,
        setEditAnswerAnswerLines,
        setEditQuestionWorkingSpaces,
        setEditAnswerWorkingSpaces,
        setEditQuestionTopics,
        setEditQuestionSections,

        // Refs
        editQuestionTextareaRef,
        editAnswerTextareaRef,

        // Actions
        loadQuestion,
        clearEdit,
    }), [
        state,
        setEditQuestionText,
        setEditAnswerText,
        setEditMarks,
        setEditTopic,
        setEditSection,
        setEditIsActive,
        setEditIsNested,
        setEditIsEssayQuestion,
        setEditIsGraphQuestion,
        setEditIsMapQuestion,
        setEditQuestionInlineImages,
        setEditAnswerInlineImages,
        setEditQuestionImagePositions,
        setEditAnswerImagePositions,
        setEditQuestionAnswerLines,
        setEditAnswerAnswerLines,
        setEditQuestionWorkingSpaces,
        setEditAnswerWorkingSpaces,
        setEditQuestionTopics,
        setEditQuestionSections,
        loadQuestion,
        clearEdit,
    ]);
}