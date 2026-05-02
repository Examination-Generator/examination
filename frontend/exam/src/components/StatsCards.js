// src/components/StatsCards.jsx
import React, { memo } from 'react';

const StatsCards = memo(function StatsCards({ stats }) {
    const cards = [
        {
            label: 'Total Questions',
            value: stats.totalQuestions,
            gradient: 'from-blue-500 to-blue-600',
            textColor: 'text-blue-100',
        },
        {
            label: 'Active Questions',
            value: stats.activeQuestions,
            gradient: 'from-green-500 to-green-600',
            textColor: 'text-green-100',
        },
        {
            label: 'Inactive Questions',
            value: stats.inactiveQuestions,
            gradient: 'from-red-500 to-red-600',
            textColor: 'text-red-100',
        },
        {
            label: 'Unknown Topics',
            value: stats.unknownTopics,
            gradient: 'from-orange-500 to-orange-600',
            textColor: 'text-orange-100',
        },
    ];

    return (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            {cards.map(card => (
                <div key={card.label} className={`bg-gradient-to-br ${card.gradient} rounded-xl shadow-lg p-6 text-white`}>
                    <p className={`${card.textColor} text-sm`}>{card.label}</p>
                    <p className="text-3xl font-bold">{card.value}</p>
                </div>
            ))}
        </div>
    );
});

export default StatsCards;