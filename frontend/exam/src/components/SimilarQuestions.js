import React, { memo } from 'react';

const SimilarQuestions = memo(function SimilarQuestions({ questions, isSearching, questionText }) {
    if (isSearching) {
        return (
            <div className="text-center py-8">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-green-600 mx-auto" />
                <p className="text-sm text-gray-600 mt-2">Searching...</p>
            </div>
        );
    }

    if (questionText.length <= 10) {
        return (
            <div className="text-center py-8">
                <p className="text-sm text-gray-500">
                    Start typing a question to see similar questions from the database
                </p>
            </div>
        );
    }

    if (questions.length === 0) {
        return (
            <div className="text-center py-8">
                <div className="text-green-600 mb-2">
                    <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                </div>
                <p className="text-sm text-green-600 font-semibold">No similar questions found!</p>
                <p className="text-xs text-gray-500 mt-1">This appears to be a unique question</p>
            </div>
        );
    }

    return (
        <div className="space-y-3">
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                <p className="text-xs font-bold text-yellow-800">⚠️ Similar questions detected!</p>
                <p className="text-xs text-yellow-700 mt-1">
                    Found {questions.length} similar question{questions.length > 1 ? 's' : ''}
                </p>
            </div>

            {questions.map((question, index) => (
                <div key={question.id || index} className="border border-gray-200 rounded-lg p-4 bg-white hover:shadow-md transition">
                    <div className="flex justify-between items-center mb-2">
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-bold bg-green-100 text-green-800">
                            {question.similarity_score ? `${Math.round(question.similarity_score)}% Match` : 'Similar'}
                        </span>
                        <span className="text-xs text-gray-500">ID: {question.id}</span>
                    </div>

                    <div className="text-sm text-gray-800 mb-3 leading-relaxed border-l-2 border-green-400 pl-3">
                        {question.question_text?.substring(0, 200)}
                        {question.question_text?.length > 200 ? '...' : ''}
                    </div>

                    <div className="grid grid-cols-2 gap-2 pt-3 border-t border-gray-100 text-xs text-gray-600">
                        <span>📚 {question.topic || 'N/A'}</span>
                        <span>📄 {question.paper || 'N/A'}</span>
                        <span>📑 {question.section || 'N/A'}</span>
                        <span className="font-bold text-green-600">⭐ {question.marks || 0} marks</span>
                    </div>
                </div>
            ))}
        </div>
    );
});

export default SimilarQuestions;