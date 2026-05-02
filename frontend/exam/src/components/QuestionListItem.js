// src/components/QuestionListItem.jsx
import React, { memo } from 'react';

const QuestionListItem = memo(function QuestionListItem({ question, isSelected, onClick }) {
    const questionText = question.question_text || '';
    const answerText = question.answer_text || '';

    return (
        <div
            onClick={() => onClick(question)}
            className={`p-4 border rounded-lg cursor-pointer transition ${
                isSelected
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
            }`}
        >
            <div className="flex justify-between items-start mb-2">
                <div className="flex-1">
                    <p className="text-sm font-semibold text-gray-800 line-clamp-2">
                        {questionText.substring(0, 180)}{questionText.length > 180 ? '...' : ''}
                    </p>
                    {answerText && (
                        <p className="mt-1 text-sm text-gray-600 line-clamp-1">
                            <span className="font-semibold">Answer:</span>{' '}
                            {answerText.substring(0, 120)}{answerText.length > 120 ? '...' : ''}
                        </p>
                    )}
                </div>
                <span className="ml-3 text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full whitespace-nowrap">
                    {question.marks} marks
                </span>
            </div>

            <div className="flex flex-wrap gap-2 text-xs">
                <span className="bg-gray-100 px-2 py-1 rounded">
                    📚 {question.subject_name || 'Unknown'}
                </span>
                {question.paper_name && (
                    <span className="bg-gray-100 px-2 py-1 rounded">📄 {question.paper_name}</span>
                )}
                {question.topic_name && (
                    <span className="bg-gray-100 px-2 py-1 rounded">📖 {question.topic_name}</span>
                )}
                <span className={`px-2 py-1 rounded font-semibold ${
                    question.is_active !== false ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                }`}>
                    {question.is_active !== false ? '✓ Active' : '✕ Inactive'}
                </span>
                <span className={`px-2 py-1 rounded font-semibold ${
                    question.is_nested ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'
                }`}>
                    {question.is_nested ? '⊕ Nested' : '◉ Standalone'}
                </span>
            </div>
        </div>
    );
}, (prev, next) => (
    // Only re-render if these specific props change
    prev.question.id === next.question.id &&
    prev.isSelected === next.isSelected &&
    prev.question.is_active === next.question.is_active
));

export default QuestionListItem;