const express = require('express');
const router = express.Router();
const { Question, Subject, Paper, Topic, Section } = require('../models/schema');
const { authMiddleware } = require('../middleware/auth');

/**
 * QUESTION MANAGEMENT ROUTES
 * 
 * Routes:
 * - POST /api/questions - Create new question
 * - GET /api/questions - Get all questions with filters
 * - GET /api/questions/:id - Get single question
 * - PUT /api/questions/:id - Update question
 * - DELETE /api/questions/:id - Delete question (soft delete)
 * - GET /api/questions/search - Search similar questions
 * - POST /api/questions/bulk - Create multiple questions
 */

// Apply authentication middleware to all routes
router.use(authMiddleware);

// ==================== QUESTION ROUTES ====================

/**
 * @route   POST /api/questions
 * @desc    Create new question with inline images
 * @access  Private
 */
router.post('/', async (req, res) => {
    try {
        const { 
            subject, 
            paper, 
            topic, 
            section,
            questionText, 
            questionInlineImages,
            answerText, 
            answerInlineImages,
            marks,
            isActive 
        } = req.body;

        // Validate required fields
        if (!subject || !paper || !topic || !questionText || !answerText || !marks) {
            return res.status(400).json({ 
                success: false, 
                message: 'Subject, paper, topic, question, answer, and marks are required' 
            });
        }

        // Verify subject exists
        const subjectExists = await Subject.findById(subject);
        if (!subjectExists) {
            return res.status(404).json({ 
                success: false, 
                message: 'Subject not found' 
            });
        }

        // Verify paper exists and belongs to subject
        const paperExists = await Paper.findById(paper);
        if (!paperExists || paperExists.subject.toString() !== subject) {
            return res.status(404).json({ 
                success: false, 
                message: 'Paper not found or does not belong to subject' 
            });
        }

        // Verify topic exists and belongs to paper
        const topicExists = await Topic.findById(topic);
        if (!topicExists || topicExists.paper.toString() !== paper) {
            return res.status(404).json({ 
                success: false, 
                message: 'Topic not found or does not belong to paper' 
            });
        }

        // If section provided, verify it exists and belongs to paper
        if (section) {
            const sectionExists = await Section.findById(section);
            if (!sectionExists || sectionExists.paper.toString() !== paper) {
                return res.status(404).json({ 
                    success: false, 
                    message: 'Section not found or does not belong to paper' 
                });
            }
        }

        // Create question
        const question = await Question.create({
            subject,
            paper,
            topic,
            section: section || null,
            questionText,
            questionInlineImages: questionInlineImages || [],
            answerText,
            answerInlineImages: answerInlineImages || [],
            marks,
            isActive: isActive !== undefined ? isActive : true,
            createdBy: req.user.userId
        });

        // Populate references
        await question.populate([
            { path: 'subject', select: 'name' },
            { path: 'paper', select: 'name' },
            { path: 'topic', select: 'name' },
            { path: 'section', select: 'name' }
        ]);

        res.status(201).json({ 
            success: true, 
            message: 'Question created successfully',
            data: question
        });

    } catch (error) {
        console.error('Create question error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Server error. Please try again later.' 
        });
    }
});

/**
 * @route   GET /api/questions
 * @desc    Get all questions with filters
 * @access  Private
 */
router.get('/', async (req, res) => {
    try {
        const { 
            subject, 
            paper, 
            topic, 
            section,
            isActive,
            page = 1,
            limit = 50
        } = req.query;

        // Build query
        const query = {};
        if (subject) query.subject = subject;
        if (paper) query.paper = paper;
        if (topic) query.topic = topic;
        if (section) query.section = section;
        if (isActive !== undefined) query.isActive = isActive === 'true';

        // Calculate pagination
        const skip = (parseInt(page) - 1) * parseInt(limit);

        // Get questions
        const questions = await Question.find(query)
            .populate([
                { path: 'subject', select: 'name' },
                { path: 'paper', select: 'name' },
                { path: 'topic', select: 'name' },
                { path: 'section', select: 'name' },
                { path: 'createdBy', select: 'fullName' }
            ])
            .sort({ createdAt: -1 })
            .skip(skip)
            .limit(parseInt(limit));

        // Get total count
        const total = await Question.countDocuments(query);

        res.json({ 
            success: true, 
            count: questions.length,
            total,
            page: parseInt(page),
            pages: Math.ceil(total / parseInt(limit)),
            data: questions
        });

    } catch (error) {
        console.error('Get questions error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Server error. Please try again later.' 
        });
    }
});

/**
 * @route   GET /api/questions/:id
 * @desc    Get single question
 * @access  Private
 */
router.get('/:id', async (req, res) => {
    try {
        const question = await Question.findById(req.params.id)
            .populate([
                { path: 'subject', select: 'name' },
                { path: 'paper', select: 'name' },
                { path: 'topic', select: 'name' },
                { path: 'section', select: 'name' },
                { path: 'createdBy', select: 'fullName phoneNumber' }
            ]);

        if (!question) {
            return res.status(404).json({ 
                success: false, 
                message: 'Question not found' 
            });
        }

        res.json({ 
            success: true, 
            data: question
        });

    } catch (error) {
        console.error('Get question error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Server error. Please try again later.' 
        });
    }
});

/**
 * @route   PUT /api/questions/:id
 * @desc    Update question
 * @access  Private
 */
router.put('/:id', async (req, res) => {
    try {
        const question = await Question.findById(req.params.id);
        if (!question) {
            return res.status(404).json({ 
                success: false, 
                message: 'Question not found' 
            });
        }

        // Update fields
        const updateFields = [
            'subject', 'paper', 'topic', 'section',
            'questionText', 'questionInlineImages',
            'answerText', 'answerInlineImages',
            'marks', 'isActive'
        ];

        updateFields.forEach(field => {
            if (req.body[field] !== undefined) {
                question[field] = req.body[field];
            }
        });

        await question.save();

        // Populate references
        await question.populate([
            { path: 'subject', select: 'name' },
            { path: 'paper', select: 'name' },
            { path: 'topic', select: 'name' },
            { path: 'section', select: 'name' }
        ]);

        res.json({ 
            success: true, 
            message: 'Question updated successfully',
            data: question
        });

    } catch (error) {
        console.error('Update question error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Server error. Please try again later.' 
        });
    }
});

/**
 * @route   DELETE /api/questions/:id
 * @desc    Delete question (soft delete)
 * @access  Private
 */
router.delete('/:id', async (req, res) => {
    try {
        const question = await Question.findById(req.params.id);
        if (!question) {
            return res.status(404).json({ 
                success: false, 
                message: 'Question not found' 
            });
        }

        // Soft delete
        question.isActive = false;
        await question.save();

        res.json({ 
            success: true, 
            message: 'Question deleted successfully'
        });

    } catch (error) {
        console.error('Delete question error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Server error. Please try again later.' 
        });
    }
});

/**
 * @route   GET /api/questions/search/similar
 * @desc    Search for similar questions
 * @access  Private
 */
router.get('/search/similar', async (req, res) => {
    try {
        const { text, subject, paper, topic, limit = 10 } = req.query;

        if (!text || text.length < 10) {
            return res.status(400).json({ 
                success: false, 
                message: 'Search text must be at least 10 characters' 
            });
        }

        // Build query with text search
        const query = {
            $text: { $search: text },
            isActive: true
        };

        if (subject) query.subject = subject;
        if (paper) query.paper = paper;
        if (topic) query.topic = topic;

        // Search questions
        const questions = await Question.find(
            query,
            { score: { $meta: "textScore" } }
        )
        .sort({ score: { $meta: "textScore" } })
        .limit(parseInt(limit))
        .populate([
            { path: 'subject', select: 'name' },
            { path: 'paper', select: 'name' },
            { path: 'topic', select: 'name' }
        ]);

        res.json({ 
            success: true, 
            count: questions.length,
            data: questions
        });

    } catch (error) {
        console.error('Search questions error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Server error. Please try again later.' 
        });
    }
});

/**
 * @route   POST /api/questions/bulk
 * @desc    Create multiple questions at once
 * @access  Private
 */
router.post('/bulk', async (req, res) => {
    try {
        const { questions } = req.body;

        if (!Array.isArray(questions) || questions.length === 0) {
            return res.status(400).json({ 
                success: false, 
                message: 'Questions array is required' 
            });
        }

        // Add createdBy to all questions
        const questionsToCreate = questions.map(q => ({
            ...q,
            createdBy: req.user.userId
        }));

        // Create all questions
        const createdQuestions = await Question.insertMany(questionsToCreate);

        res.status(201).json({ 
            success: true, 
            message: `${createdQuestions.length} questions created successfully`,
            count: createdQuestions.length,
            data: createdQuestions
        });

    } catch (error) {
        console.error('Bulk create questions error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Server error. Please try again later.' 
        });
    }
});

/**
 * @route   GET /api/questions/stats/overview
 * @desc    Get question statistics
 * @access  Private
 */
router.get('/stats/overview', async (req, res) => {
    try {
        const { subject, paper } = req.query;

        // Build match query
        const matchQuery = { isActive: true };
        if (subject) matchQuery.subject = mongoose.Types.ObjectId(subject);
        if (paper) matchQuery.paper = mongoose.Types.ObjectId(paper);

        // Aggregate statistics
        const stats = await Question.aggregate([
            { $match: matchQuery },
            {
                $group: {
                    _id: null,
                    totalQuestions: { $sum: 1 },
                    totalMarks: { $sum: '$marks' },
                    avgMarks: { $avg: '$marks' },
                    totalUsage: { $sum: '$timesUsed' }
                }
            }
        ]);

        // Get questions by subject
        const bySubject = await Question.aggregate([
            { $match: { isActive: true } },
            {
                $group: {
                    _id: '$subject',
                    count: { $sum: 1 }
                }
            },
            {
                $lookup: {
                    from: 'subjects',
                    localField: '_id',
                    foreignField: '_id',
                    as: 'subject'
                }
            },
            { $unwind: '$subject' },
            {
                $project: {
                    subjectName: '$subject.name',
                    count: 1
                }
            }
        ]);

        res.json({ 
            success: true, 
            data: {
                overview: stats[0] || {
                    totalQuestions: 0,
                    totalMarks: 0,
                    avgMarks: 0,
                    totalUsage: 0
                },
                bySubject
            }
        });

    } catch (error) {
        console.error('Get stats error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Server error. Please try again later.' 
        });
    }
});

module.exports = router;
