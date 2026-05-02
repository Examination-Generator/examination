import React, { memo } from 'react';

const QuestionFlags = memo(function QuestionFlags({
    isQuestionActive, setIsQuestionActive,
    isNested, setIsNested,
    isEssayQuestion, setIsEssayQuestion,
    isGraphQuestion, setIsGraphQuestion,
    isMapQuestion, setIsMapQuestion,
}) {
    const flags = [
        {
            label: 'This is a Nested Question',
            checked: isNested,
            onChange: setIsNested,
            activeColor: 'purple',
            activeText: '✓ Nested question - has multiple parts',
            inactiveText: 'Standalone question',
        },
        {
            label: 'This is an Essay Question',
            checked: isEssayQuestion,
            onChange: setIsEssayQuestion,
            activeColor: 'yellow',
            activeText: '✓ Essay question - requires extended written response',
            inactiveText: 'Not an essay question',
        },
        {
            label: 'This is a Graph Question',
            checked: isGraphQuestion,
            onChange: setIsGraphQuestion,
            activeColor: 'cyan',
            activeText: '✓ Graph question - requires drawing/plotting',
            inactiveText: 'Not a graph question',
        },
        {
            label: 'This is a Map Question',
            checked: isMapQuestion,
            onChange: setIsMapQuestion,
            activeColor: 'emerald',
            activeText: '✓ Map question - requires map-based response',
            inactiveText: 'Not a map question',
        },
    ];

    const colorMap = {
        purple: { border: '#8b5cf6', bg: '#f3e8ff', text: '#6b21a8' },
        yellow: { border: '#f59e0b', bg: '#fef3c7', text: '#b45309' },
        cyan:   { border: '#06b6d4', bg: '#cffafe', text: '#0e7490' },
        emerald:{ border: '#059669', bg: '#bbf7d0', text: '#065f46' },
    };

    return (
        <div className="mb-6">
            {/* Active status — full width */}
            <div
                className="mb-4 border-2 rounded-lg p-4"
                style={{
                    borderColor: isQuestionActive ? '#10b981' : '#ef4444',
                    backgroundColor: isQuestionActive ? '#d1fae5' : '#fee2e2',
                }}
            >
                <label className="flex items-center cursor-pointer">
                    <input
                        type="checkbox"
                        checked={isQuestionActive}
                        onChange={e => setIsQuestionActive(e.target.checked)}
                        className="w-5 h-5 text-green-600 rounded"
                    />
                    <span className="ml-3 text-sm font-bold text-gray-700">Question is Active</span>
                </label>
                <p className="text-xs mt-2 ml-8" style={{ color: isQuestionActive ? '#065f46' : '#991b1b' }}>
                    {isQuestionActive
                        ? '✓ Active — Question can be used in exams'
                        : '⚠️ Inactive — Question is disabled and won\'t appear in exams'}
                </p>
            </div>

            {/* Other flags — grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {flags.map(flag => {
                    const colors = colorMap[flag.activeColor];
                    return (
                        <div
                            key={flag.label}
                            className="border-2 rounded-lg p-4"
                            style={{
                                borderColor: flag.checked ? colors.border : '#d1d5db',
                                backgroundColor: flag.checked ? colors.bg : '#f9fafb',
                            }}
                        >
                            <label className="flex items-center cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={flag.checked}
                                    onChange={e => flag.onChange(e.target.checked)}
                                    className="w-5 h-5 rounded"
                                />
                                <span className="ml-3 text-sm font-bold text-gray-700">{flag.label}</span>
                            </label>
                            <p className="text-xs mt-2 ml-8" style={{ color: flag.checked ? colors.text : '#6b7280' }}>
                                {flag.checked ? flag.activeText : flag.inactiveText}
                            </p>
                        </div>
                    );
                })}
            </div>
        </div>
    );
});

export default QuestionFlags;