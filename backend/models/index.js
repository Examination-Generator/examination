const User = require('./User');
const Subject = require('./Subject');
const Paper = require('./Paper');
const Topic = require('./Topic');
const Section = require('./Section');
const Question = require('./Question');
const OTPLog = require('./OTPLog');

// Define associations

// User associations
User.hasMany(Subject, { foreignKey: 'createdBy', as: 'subjects' });
User.hasMany(Paper, { foreignKey: 'createdBy', as: 'papers' });
User.hasMany(Topic, { foreignKey: 'createdBy', as: 'topics' });
User.hasMany(Section, { foreignKey: 'createdBy', as: 'sections' });
User.hasMany(Question, { foreignKey: 'createdBy', as: 'questions' });

// Subject associations
Subject.belongsTo(User, { foreignKey: 'createdBy', as: 'creator' });
Subject.hasMany(Paper, { foreignKey: 'subjectId', as: 'papers', onDelete: 'CASCADE' });
Subject.hasMany(Question, { foreignKey: 'subjectId', as: 'questions', onDelete: 'CASCADE' });

// Paper associations
Paper.belongsTo(Subject, { foreignKey: 'subjectId', as: 'subject' });
Paper.belongsTo(User, { foreignKey: 'createdBy', as: 'creator' });
Paper.hasMany(Topic, { foreignKey: 'paperId', as: 'topics', onDelete: 'CASCADE' });
Paper.hasMany(Section, { foreignKey: 'paperId', as: 'sections', onDelete: 'CASCADE' });
Paper.hasMany(Question, { foreignKey: 'paperId', as: 'questions', onDelete: 'CASCADE' });

// Topic associations
Topic.belongsTo(Paper, { foreignKey: 'paperId', as: 'paper' });
Topic.belongsTo(User, { foreignKey: 'createdBy', as: 'creator' });
Topic.hasMany(Question, { foreignKey: 'topicId', as: 'questions', onDelete: 'CASCADE' });

// Section associations
Section.belongsTo(Paper, { foreignKey: 'paperId', as: 'paper' });
Section.belongsTo(User, { foreignKey: 'createdBy', as: 'creator' });
Section.hasMany(Question, { foreignKey: 'sectionId', as: 'questions', onDelete: 'SET NULL' });

// Question associations
Question.belongsTo(Subject, { foreignKey: 'subjectId', as: 'subject' });
Question.belongsTo(Paper, { foreignKey: 'paperId', as: 'paper' });
Question.belongsTo(Topic, { foreignKey: 'topicId', as: 'topic' });
Question.belongsTo(Section, { foreignKey: 'sectionId', as: 'section' });
Question.belongsTo(User, { foreignKey: 'createdBy', as: 'creator' });

module.exports = {
    User,
    Subject,
    Paper,
    Topic,
    Section,
    Question,
    OTPLog
};
