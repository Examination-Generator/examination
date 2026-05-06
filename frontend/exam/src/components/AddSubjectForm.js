import React, { useState } from 'react';
import * as subjectService from '../services/subjectService';
import { useError } from '../contexts/ErrorContext';

export default function AddSubjectForm({ onSuccess, onRefresh }) {
    const { showError, showSuccess } = useError();
    const [newSubjectName, setNewSubjectName] = useState('');
    const [newSubjectPapers, setNewSubjectPapers] = useState([
        { name: '', topics: [''], sections: [''], durationHours: 2, durationMinutes: 0 }
    ]);

    // Paper management
    const addPaper = () => {
        setNewSubjectPapers([...newSubjectPapers, { name: '', topics: [''], sections: [''], durationHours: 2, durationMinutes: 0 }]);
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

    const updatePaperDuration = (index, field, value) => {
        const updated = [...newSubjectPapers];
        const numValue = parseInt(value) || 0;
        if (field === 'hours') {
            updated[index].durationHours = Math.max(0, Math.min(24, numValue));
        } else if (field === 'minutes') {
            updated[index].durationMinutes = Math.max(0, Math.min(59, numValue));
        }
        setNewSubjectPapers(updated);
    };

    // Topic management
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

    // Section management
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

    // Form submission
    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!newSubjectName.trim()) {
            showError('Please enter a subject name');
            return;
        }
        const validPapers = newSubjectPapers.filter(p => p.name.trim() !== '');
        if (validPapers.length === 0) {
            showError('Please add at least one paper');
            return;
        }
        const subjectData = {
            name: newSubjectName.trim(),
            papers: validPapers.map(paper => ({
                name: paper.name.trim(),
                durationHours: paper.durationHours || 2,
                durationMinutes: paper.durationMinutes || 0,
                topics: paper.topics.filter(t => t.trim() !== ''),
                sections: paper.sections.filter(s => s.trim() !== '').length > 0
                    ? paper.sections.filter(s => s.trim() !== '')
                    : []
            }))
        };
        try {
            const result = await subjectService.createSubject(subjectData);
            showSuccess(`Subject "${newSubjectName}" added successfully!`);
            setNewSubjectName('');
            setNewSubjectPapers([{ name: '', topics: [''], sections: [''], durationHours: 2, durationMinutes: 0 }]);
            if (onSuccess) onSuccess(result);
            if (onRefresh) setTimeout(onRefresh, 500);
        } catch (error) {
            showError(error.message || 'Failed to add subject. Please try again.');
        }
    };

    return (
        <div className="bg-white rounded-xl shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Add New Subject</h2>
            <form onSubmit={handleSubmit}>
                {/* Subject Name */}
                <div className="mb-6">
                    <label className="block text-sm font-bold text-gray-700 mb-2">Subject Name *</label>
                    <input
                        type="text"
                        value={newSubjectName}
                        onChange={e => setNewSubjectName(e.target.value)}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
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
                            className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm transition"
                        >
                            + Add Paper
                        </button>
                    </div>

                    {newSubjectPapers.map((paper, paperIndex) => (
                        <div key={paperIndex} className="border border-gray-200 rounded-lg p-4 mb-4">
                            <div className="flex justify-between items-center mb-3">
                                <h4 className="text-md font-semibold text-gray-700">Paper {paperIndex + 1}</h4>
                                {newSubjectPapers.length > 1 && (
                                    <button
                                        type="button"
                                        onClick={() => removePaper(paperIndex)}
                                        className="text-red-600 hover:text-red-700 text-sm font-semibold transition"
                                    >
                                        Remove
                                    </button>
                                )}
                            </div>

                            {/* Paper Name */}
                            <div className="mb-3">
                                <label className="block text-sm font-semibold text-gray-700 mb-1">Paper Name</label>
                                <input
                                    type="text"
                                    value={paper.name}
                                    onChange={e => updatePaperName(paperIndex, e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-1 focus:ring-green-500 outline-none"
                                    placeholder="e.g., Paper 1"
                                />
                            </div>

                            {/* Duration */}
                            <div className="flex gap-3 mb-3">
                                <div className="flex-1">
                                    <label className="block text-sm font-semibold text-gray-700 mb-1">Duration (Hours)</label>
                                    <input
                                        type="number"
                                        min="0"
                                        max="24"
                                        value={paper.durationHours}
                                        onChange={e => updatePaperDuration(paperIndex, 'hours', e.target.value)}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-1 focus:ring-green-500 outline-none"
                                    />
                                </div>
                                <div className="flex-1">
                                    <label className="block text-sm font-semibold text-gray-700 mb-1">Minutes</label>
                                    <input
                                        type="number"
                                        min="0"
                                        max="59"
                                        value={paper.durationMinutes}
                                        onChange={e => updatePaperDuration(paperIndex, 'minutes', e.target.value)}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-1 focus:ring-green-500 outline-none"
                                    />
                                </div>
                            </div>

                            {/* Topics */}
                            <div className="mb-3">
                                <div className="flex items-center justify-between mb-2">
                                    <h5 className="text-sm font-semibold text-gray-600">Topics</h5>
                                    <button
                                        type="button"
                                        onClick={() => addTopic(paperIndex)}
                                        className="text-sm text-blue-600 hover:text-blue-700 transition"
                                    >
                                        + Add Topic
                                    </button>
                                </div>
                                {paper.topics.map((topic, topicIndex) => (
                                    <div key={topicIndex} className="flex items-center gap-2 mb-2">
                                        <input
                                            type="text"
                                            value={topic}
                                            onChange={e => updateTopic(paperIndex, topicIndex, e.target.value)}
                                            className="flex-1 px-3 py-1 border border-gray-300 rounded focus:ring-1 focus:ring-green-500 outline-none"
                                            placeholder="Topic name"
                                        />
                                        <button
                                            type="button"
                                            onClick={() => removeTopic(paperIndex, topicIndex)}
                                            className="text-red-600 hover:text-red-700 text-sm transition"
                                        >
                                            Remove
                                        </button>
                                    </div>
                                ))}
                            </div>

                            {/* Sections */}
                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <h5 className="text-sm font-semibold text-gray-600">Sections</h5>
                                    <button
                                        type="button"
                                        onClick={() => addSection(paperIndex)}
                                        className="text-sm text-blue-600 hover:text-blue-700 transition"
                                    >
                                        + Add Section
                                    </button>
                                </div>
                                {paper.sections.map((section, sectionIndex) => (
                                    <div key={sectionIndex} className="flex items-center gap-2 mb-2">
                                        <input
                                            type="text"
                                            value={section}
                                            onChange={e => updateSection(paperIndex, sectionIndex, e.target.value)}
                                            className="flex-1 px-3 py-1 border border-gray-300 rounded focus:ring-1 focus:ring-green-500 outline-none"
                                            placeholder="Section name"
                                        />
                                        <button
                                            type="button"
                                            onClick={() => removeSection(paperIndex, sectionIndex)}
                                            className="text-red-600 hover:text-red-700 text-sm transition"
                                        >
                                            Remove
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>

                {/* Submit Button */}
                <div className="flex justify-end gap-3">
                    <button
                        type="submit"
                        className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg font-semibold transition"
                    >
                        Create Subject
                    </button>
                </div>
            </form>
        </div>
    );
}
