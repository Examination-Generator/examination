const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const Question = sequelize.define('Question', {
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true
    },
    subjectId: {
        type: DataTypes.UUID,
        allowNull: false,
        field: 'subject_id',
        references: {
            model: 'subjects',
            key: 'id'
        }
    },
    paperId: {
        type: DataTypes.UUID,
        allowNull: false,
        field: 'paper_id',
        references: {
            model: 'papers',
            key: 'id'
        }
    },
    topicId: {
        type: DataTypes.UUID,
        allowNull: false,
        field: 'topic_id',
        references: {
            model: 'topics',
            key: 'id'
        }
    },
    sectionId: {
        type: DataTypes.UUID,
        field: 'section_id',
        references: {
            model: 'sections',
            key: 'id'
        }
    },
    questionText: {
        type: DataTypes.TEXT,
        allowNull: false,
        field: 'question_text'
    },
    questionType: {
        type: DataTypes.ENUM('multiple_choice', 'true_false', 'short_answer', 'essay', 'structured'),
        defaultValue: 'multiple_choice',
        field: 'question_type'
    },
    difficulty: {
        type: DataTypes.ENUM('easy', 'medium', 'hard'),
        defaultValue: 'medium'
    },
    marks: {
        type: DataTypes.INTEGER,
        defaultValue: 1
    },
    correctAnswer: {
        type: DataTypes.TEXT,
        field: 'correct_answer'
    },
    answerExplanation: {
        type: DataTypes.TEXT,
        field: 'answer_explanation'
    },
    options: {
        type: DataTypes.JSONB
    },
    isActive: {
        type: DataTypes.BOOLEAN,
        defaultValue: true,
        field: 'is_active'
    },
    timesUsed: {
        type: DataTypes.INTEGER,
        defaultValue: 0,
        field: 'times_used'
    },
    lastUsed: {
        type: DataTypes.DATE,
        field: 'last_used'
    },
    createdBy: {
        type: DataTypes.UUID,
        allowNull: false,
        field: 'created_by',
        references: {
            model: 'users',
            key: 'id'
        }
    }
}, {
    tableName: 'questions',
    timestamps: true,
    underscored: true
});

module.exports = Question;
