const express = require('express');
const router = express.Router();
const { Subject, Paper, Section, Topic } = require('../models/schema');
const { authMiddleware } = require('../middleware/auth');

/**
 * SUBJECT MANAGEMENT ROUTES
 * 
 * Hierarchy: Subject → Papers → Topics
 * Papers can have 0 or more Sections
 * Topics are filtered by Paper
 * 
 * Routes:
 * - POST /api/subjects - Create new subject with papers
 * - GET /api/subjects - Get all subjects
 * - GET /api/subjects/:id - Get single subject with papers and topics
 * - PUT /api/subjects/:id - Update subject
 * - DELETE /api/subjects/:id - Delete subject
 * - POST /api/subjects/:id/papers - Add paper to subject
 * - POST /api/subjects/:subjectId/papers/:paperId/sections - Add section to paper
 * - POST /api/subjects/:subjectId/papers/:paperId/topics - Add topic to paper
 * - GET /api/subjects/:subjectId/papers/:paperId/topics - Get topics filtered by paper
 */

// Apply authentication middleware to all routes
router.use(authMiddleware);

// ==================== SUBJECT ROUTES ====================

/**
 * @route   POST /api/subjects
 * @desc    Create new subject with papers, sections, and topics
 * @access  Private (Authenticated users)
 */
router.post('/', async (req, res) => {
    try {
        const { name, description, papers } = req.body;
        console.log('[SUBJECT] Creating subject:', { name, papersCount: papers?.length || 0 });

        // Validate input
        if (!name) {
            console.log('[SUBJECT] Subject name missing');
            return res.status(400).json({ 
                success: false, 
                message: 'Subject name is required' 
            });
        }

        // Check if subject already exists
        const existingSubject = await Subject.findOne({ name });
        if (existingSubject) {
            console.log('[SUBJECT] Subject already exists:', name);
            return res.status(400).json({ 
                success: false, 
                message: 'Subject already exists' 
            });
        }

        // Create subject
        const subject = await Subject.create({
            name,
            description,
            createdBy: req.user.userId
        });
        console.log('[SUBJECT] Subject created:', subject._id);

        // Create papers if provided
        const paperIds = [];
        if (papers && Array.isArray(papers)) {
            for (const paperData of papers) {
                // Create paper
                const paper = await Paper.create({
                    name: paperData.name,
                    subject: subject._id,
                    description: paperData.description,
                    createdBy: req.user.userId
                });

                paperIds.push(paper._id);

                // Create sections if provided
                const sectionIds = [];
                if (paperData.sections && Array.isArray(paperData.sections)) {
                    for (let i = 0; i < paperData.sections.length; i++) {
                        const sectionName = paperData.sections[i];
                        if (sectionName && sectionName.trim()) {
                            const section = await Section.create({
                                name: sectionName,
                                paper: paper._id,
                                order: i,
                                createdBy: req.user.userId
                            });
                            sectionIds.push(section._id);
                        }
                    }
                }

                // Update paper with sections
                paper.sections = sectionIds;
                await paper.save();

                // Create topics if provided
                const topicIds = [];
                if (paperData.topics && Array.isArray(paperData.topics)) {
                    for (const topicName of paperData.topics) {
                        if (topicName && topicName.trim()) {
                            const topic = await Topic.create({
                                name: topicName,
                                paper: paper._id,
                                createdBy: req.user.userId
                            });
                            topicIds.push(topic._id);
                        }
                    }
                }

                // Update paper with topics
                paper.topics = topicIds;
                await paper.save();
            }
        }

        // Update subject with papers
        subject.papers = paperIds;
        await subject.save();

        // Fetch complete subject with all relations
        const completeSubject = await Subject.findById(subject._id)
            .populate({
                path: 'papers',
                populate: [
                    { path: 'sections' },
                    { path: 'topics' }
                ]
            });

        console.log('[SUBJECT] Subject created successfully with', paperIds.length, 'papers');
        res.status(201).json({ 
            success: true, 
            message: 'Subject created successfully',
            data: completeSubject
        });

    } catch (error) {
        console.error('[SUBJECT ERROR] Create subject error:', error.message);
        console.error(error.stack);
        res.status(500).json({ 
            success: false, 
            message: 'Server error. Please try again later.',
            error: process.env.NODE_ENV === 'development' ? error.message : undefined
        });
    }
});

/**
 * @route   GET /api/subjects
 * @desc    Get all subjects with papers
 * @access  Private
 */
router.get('/', async (req, res) => {
    try {
        const { active } = req.query;
        console.log('[SUBJECT] Fetching all subjects, active filter:', active);

        // Build query
        const query = {};
        if (active !== undefined) {
            query.isActive = active === 'true';
        }

        // Get subjects with populated papers
        const subjects = await Subject.find(query)
            .populate({
                path: 'papers',
                match: active !== undefined ? { isActive: active === 'true' } : {},
                populate: [
                    { path: 'sections' },
                    { path: 'topics' }
                ]
            })
            .sort({ name: 1 });

        console.log('[SUBJECT] Found', subjects.length, 'subjects');
        res.json({ 
            success: true, 
            count: subjects.length,
            data: subjects
        });

    } catch (error) {
        console.error('[SUBJECT ERROR] Get subjects error:', error.message);
        console.error(error.stack);
        res.status(500).json({ 
            success: false, 
            message: 'Server error. Please try again later.',
            error: process.env.NODE_ENV === 'development' ? error.message : undefined
        });
    }
});

/**
 * @route   GET /api/subjects/:id
 * @desc    Get single subject with all details
 * @access  Private
 */
router.get('/:id', async (req, res) => {
    try {
        const subject = await Subject.findById(req.params.id)
            .populate({
                path: 'papers',
                populate: [
                    { path: 'sections' },
                    { path: 'topics' }
                ]
            });

        if (!subject) {
            return res.status(404).json({ 
                success: false, 
                message: 'Subject not found' 
            });
        }

        res.json({ 
            success: true, 
            data: subject
        });

    } catch (error) {
        console.error('Get subject error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Server error. Please try again later.' 
        });
    }
});

/**
 * @route   PUT /api/subjects/:id
 * @desc    Update subject
 * @access  Private
 */
router.put('/:id', async (req, res) => {
    try {
        const { name, description, isActive } = req.body;

        const subject = await Subject.findById(req.params.id);
        if (!subject) {
            return res.status(404).json({ 
                success: false, 
                message: 'Subject not found' 
            });
        }

        // Update fields
        if (name) subject.name = name;
        if (description !== undefined) subject.description = description;
        if (isActive !== undefined) subject.isActive = isActive;

        await subject.save();

        res.json({ 
            success: true, 
            message: 'Subject updated successfully',
            data: subject
        });

    } catch (error) {
        console.error('Update subject error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Server error. Please try again later.' 
        });
    }
});

/**
 * @route   DELETE /api/subjects/:id
 * @desc    Delete subject (soft delete - set isActive to false)
 * @access  Private
 */
router.delete('/:id', async (req, res) => {
    try {
        const subject = await Subject.findById(req.params.id);
        if (!subject) {
            return res.status(404).json({ 
                success: false, 
                message: 'Subject not found' 
            });
        }

        // Soft delete
        subject.isActive = false;
        await subject.save();

        res.json({ 
            success: true, 
            message: 'Subject deleted successfully'
        });

    } catch (error) {
        console.error('Delete subject error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Server error. Please try again later.' 
        });
    }
});

// ==================== PAPER ROUTES ====================

/**
 * @route   POST /api/subjects/:id/papers
 * @desc    Add paper to subject
 * @access  Private
 */
router.post('/:id/papers', async (req, res) => {
    try {
        const { name, description } = req.body;

        const subject = await Subject.findById(req.params.id);
        if (!subject) {
            return res.status(404).json({ 
                success: false, 
                message: 'Subject not found' 
            });
        }

        // Create paper
        const paper = await Paper.create({
            name,
            description,
            subject: subject._id,
            createdBy: req.user.userId
        });

        // Add paper to subject
        subject.papers.push(paper._id);
        await subject.save();

        res.status(201).json({ 
            success: true, 
            message: 'Paper added successfully',
            data: paper
        });

    } catch (error) {
        console.error('Add paper error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Server error. Please try again later.' 
        });
    }
});

/**
 * @route   GET /api/subjects/:subjectId/papers/:paperId
 * @desc    Get single paper with sections and topics
 * @access  Private
 */
router.get('/:subjectId/papers/:paperId', async (req, res) => {
    try {
        const paper = await Paper.findById(req.params.paperId)
            .populate('sections')
            .populate('topics');

        if (!paper) {
            return res.status(404).json({ 
                success: false, 
                message: 'Paper not found' 
            });
        }

        res.json({ 
            success: true, 
            data: paper
        });

    } catch (error) {
        console.error('Get paper error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Server error. Please try again later.' 
        });
    }
});

// ==================== SECTION ROUTES ====================

/**
 * @route   POST /api/subjects/:subjectId/papers/:paperId/sections
 * @desc    Add section to paper
 * @access  Private
 */
router.post('/:subjectId/papers/:paperId/sections', async (req, res) => {
    try {
        const { name, description } = req.body;

        const paper = await Paper.findById(req.params.paperId);
        if (!paper) {
            return res.status(404).json({ 
                success: false, 
                message: 'Paper not found' 
            });
        }

        // Get next order number
        const order = paper.sections.length;

        // Create section
        const section = await Section.create({
            name,
            description,
            paper: paper._id,
            order,
            createdBy: req.user.userId
        });

        // Add section to paper
        paper.sections.push(section._id);
        await paper.save();

        res.status(201).json({ 
            success: true, 
            message: 'Section added successfully',
            data: section
        });

    } catch (error) {
        console.error('Add section error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Server error. Please try again later.' 
        });
    }
});

// ==================== TOPIC ROUTES ====================

/**
 * @route   POST /api/subjects/:subjectId/papers/:paperId/topics
 * @desc    Add topic to paper
 * @access  Private
 */
router.post('/:subjectId/papers/:paperId/topics', async (req, res) => {
    try {
        const { name, description, sectionId } = req.body;

        const paper = await Paper.findById(req.params.paperId);
        if (!paper) {
            return res.status(404).json({ 
                success: false, 
                message: 'Paper not found' 
            });
        }

        // If section is provided, verify it belongs to this paper
        if (sectionId) {
            const section = await Section.findById(sectionId);
            if (!section || section.paper.toString() !== paper._id.toString()) {
                return res.status(400).json({ 
                    success: false, 
                    message: 'Invalid section' 
                });
            }
        }

        // Create topic
        const topic = await Topic.create({
            name,
            description,
            paper: paper._id,
            section: sectionId || null,
            createdBy: req.user.userId
        });

        // Add topic to paper
        paper.topics.push(topic._id);
        await paper.save();

        res.status(201).json({ 
            success: true, 
            message: 'Topic added successfully',
            data: topic
        });

    } catch (error) {
        console.error('Add topic error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Server error. Please try again later.' 
        });
    }
});

/**
 * @route   GET /api/subjects/:subjectId/papers/:paperId/topics
 * @desc    Get topics filtered by paper (and optionally by section)
 * @access  Private
 */
router.get('/:subjectId/papers/:paperId/topics', async (req, res) => {
    try {
        const { sectionId } = req.query;

        // Build query
        const query = { 
            paper: req.params.paperId,
            isActive: true
        };

        if (sectionId) {
            query.section = sectionId;
        }

        // Get topics
        const topics = await Topic.find(query).sort({ name: 1 });

        res.json({ 
            success: true, 
            count: topics.length,
            data: topics
        });

    } catch (error) {
        console.error('Get topics error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Server error. Please try again later.' 
        });
    }
});

module.exports = router;
