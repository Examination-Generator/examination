// src/components/EditFilters.jsx
import React, { memo } from 'react';

const EditFilters = memo(function EditFilters({
    searchQuery, onSearchChange,
    filterSubject, onSubjectChange,
    filterPaper, onPaperChange,
    filterTopic, onTopicChange,
    filterStatus, onStatusChange,
    filterType, onTypeChange,
    existingSubjects,
    availablePapers,
    availableTopics,
    onClearAll,
}) {
    const hasFilters = filterSubject || filterPaper || filterTopic ||
        filterStatus !== 'all' || filterType !== 'all';

    return (
        <div className="space-y-4">
            {/* Search */}
            <div className="flex gap-3">
                <input
                    type="text"
                    value={searchQuery}
                    onChange={e => onSearchChange(e.target.value)}
                    placeholder="Search questions..."
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                />
            </div>

            {/* Filter grid */}
            <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4">
                <div className="flex justify-between items-center mb-3">
                    <h4 className="text-sm font-bold text-gray-800">Advanced Filters</h4>
                    {hasFilters && (
                        <button onClick={onClearAll} className="text-xs text-blue-600 hover:text-blue-800 font-semibold">
                            Clear All
                        </button>
                    )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">
                    <select value={filterSubject} onChange={e => onSubjectChange(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white outline-none">
                        <option value="">All Subjects</option>
                        {existingSubjects.map(s => <option key={s.id} value={s.name}>{s.name}</option>)}
                    </select>

                    <select value={filterPaper} onChange={e => onPaperChange(e.target.value)}
                        disabled={!filterSubject}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white outline-none disabled:bg-gray-100">
                        <option value="">All Papers</option>
                        {availablePapers.map(p => <option key={p.id} value={p.name}>{p.name}</option>)}
                    </select>

                    <select value={filterTopic} onChange={e => onTopicChange(e.target.value)}
                        disabled={!filterPaper}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white outline-none disabled:bg-gray-100">
                        <option value="">All Topics</option>
                        {availableTopics.map(t => <option key={t.id} value={t.name}>{t.name}</option>)}
                    </select>
                </div>

                <div className="grid grid-cols-2 gap-3">
                    <select value={filterStatus} onChange={e => onStatusChange(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white outline-none">
                        <option value="all">All Status</option>
                        <option value="active">✓ Active Only</option>
                        <option value="inactive">✕ Inactive Only</option>
                    </select>

                    <select value={filterType} onChange={e => onTypeChange(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white outline-none">
                        <option value="all">All Types</option>
                        <option value="nested">⊕ Nested Only</option>
                        <option value="standalone">◉ Standalone Only</option>
                        <option value="essay">✎ Essay Only</option>
                        <option value="graph">📈 Graph Only</option>
                    </select>
                </div>

                {/* Active filter badges */}
                {hasFilters && (
                    <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-blue-200">
                        {filterSubject && (
                            <span className="inline-flex items-center gap-1 bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
                                📚 {filterSubject}
                                <button onClick={() => onSubjectChange('')} className="hover:bg-blue-200 rounded-full p-0.5">✕</button>
                            </span>
                        )}
                        {filterPaper && (
                            <span className="inline-flex items-center gap-1 bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-xs">
                                📄 {filterPaper}
                                <button onClick={() => onPaperChange('')} className="hover:bg-purple-200 rounded-full p-0.5">✕</button>
                            </span>
                        )}
                        {filterTopic && (
                            <span className="inline-flex items-center gap-1 bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">
                                📖 {filterTopic}
                                <button onClick={() => onTopicChange('')} className="hover:bg-green-200 rounded-full p-0.5">✕</button>
                            </span>
                        )}
                        {filterStatus !== 'all' && (
                            <span className="inline-flex items-center gap-1 bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs">
                                {filterStatus === 'active' ? '✓ Active' : '✕ Inactive'}
                                <button onClick={() => onStatusChange('all')} className="hover:bg-yellow-200 rounded-full p-0.5">✕</button>
                            </span>
                        )}
                        {filterType !== 'all' && (
                            <span className="inline-flex items-center gap-1 bg-indigo-100 text-indigo-800 px-2 py-1 rounded-full text-xs">
                                {filterType}
                                <button onClick={() => onTypeChange('all')} className="hover:bg-indigo-200 rounded-full p-0.5">✕</button>
                            </span>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
});

export default EditFilters;