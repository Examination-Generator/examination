// src/components/SubjectSelector.jsx
import React from 'react';

export default function SubjectSelector({
    subjects,
    isLoading,
    selectedSubject, selectedPaper, selectedTopic, selectedSection,
    onSubjectChange, onPaperChange, onTopicChange, onSectionChange,
    onGoToSubjects,
}) {
    if (isLoading) {
        return (
            <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600" />
                <span className="ml-3 text-gray-600">Loading subjects...</span>
            </div>
        );
    }

    if (Object.keys(subjects).length === 0) {
        return (
            <div className="text-center py-8">
                <p className="text-gray-600 mb-4">No subjects found. Please add subjects first.</p>
                <button onClick={onGoToSubjects} className="bg-green-600 text-white px-6 py-2 rounded-lg font-semibold">
                    Go to Add Subject
                </button>
            </div>
        );
    }

    const papers = selectedSubject ? subjects[selectedSubject]?.papers || [] : [];
    const topics = selectedSubject && selectedPaper
        ? subjects[selectedSubject]?.topics?.[selectedPaper] || []
        : [];
    const sections = selectedSubject && selectedPaper
        ? subjects[selectedSubject]?.sections?.[selectedPaper] || []
        : [];

    return (
        <div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                    <label className="block text-sm font-bold text-gray-700 mb-2">Select Subject *</label>
                    <select
                        value={selectedSubject}
                        onChange={e => onSubjectChange(e.target.value)}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
                    >
                        <option value="">Choose Subject</option>
                        {Object.keys(subjects).map(s => (
                            <option key={s} value={s}>{s}</option>
                        ))}
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-bold text-gray-700 mb-2">Select Paper *</label>
                    <select
                        value={selectedPaper}
                        onChange={e => onPaperChange(e.target.value)}
                        disabled={!selectedSubject}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 outline-none disabled:bg-gray-100"
                    >
                        <option value="">Choose Paper</option>
                        {papers.map(p => <option key={p} value={p}>{p}</option>)}
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-bold text-gray-700 mb-2">Select Topic</label>
                    <select
                        value={selectedTopic}
                        onChange={e => onTopicChange(e.target.value)}
                        disabled={!selectedPaper}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 outline-none disabled:bg-gray-100"
                    >
                        <option value="">Choose Topic</option>
                        {topics.map(t => <option key={t} value={t}>{t}</option>)}
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-bold text-gray-700 mb-2">Select Section</label>
                    <select
                        value={selectedSection}
                        onChange={e => onSectionChange(e.target.value)}
                        disabled={!selectedPaper || sections.length === 0}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 outline-none disabled:bg-gray-100"
                    >
                        <option value="">{sections.length === 0 ? 'No Sections' : 'Choose Section'}</option>
                        {sections.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                </div>
            </div>

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
    );
}