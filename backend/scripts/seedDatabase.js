const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const dotenv = require('dotenv');
const { User, Subject, Paper, Section, Topic, Question } = require('../models/schema');

// Load environment variables
dotenv.config();

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/examination_system';

/**
 * Database Seeding Script
 * Populates database with initial test data
 */

const seedDatabase = async () => {
    try {
        // Connect to MongoDB
        await mongoose.connect(MONGODB_URI);
        console.log('✅ Connected to MongoDB');

        // Clear existing data (CAUTION: This will delete all data)
        console.log('\nsClearing existing data...');
        await User.deleteMany({});
        await Subject.deleteMany({});
        await Paper.deleteMany({});
        await Section.deleteMany({});
        await Topic.deleteMany({});
        await Question.deleteMany({});
        console.log('✅ Existing data cleared');

        // Create admin user
        console.log('\n👤 Creating admin user...');
        const hashedPassword = await bcrypt.hash('admin123', 10);
        const adminUser = await User.create({
            fullName: 'Admin User',
            phoneNumber: '+254700000000',
            password: hashedPassword,
            role: 'admin',
            otp: {
                verified: true
            }
        });
        console.log('✅ Admin user created');
        console.log(`   Phone: ${adminUser.phoneNumber}`);
        console.log(`   Password: admin123`);

        // Create test editor user
        console.log('\n👤 Creating editor user...');
        const editorPassword = await bcrypt.hash('editor123', 10);
        const editorUser = await User.create({
            fullName: 'Editor User',
            phoneNumber: '+254700000001',
            password: editorPassword,
            role: 'editor',
            otp: {
                verified: true
            }
        });
        console.log('✅ Editor user created');
        console.log(`   Phone: ${editorUser.phoneNumber}`);
        console.log(`   Password: editor123`);

        // Create Mathematics subject with full structure
        console.log('\n📚 Creating Mathematics subject...');
        const mathSubject = await Subject.create({
            name: 'Mathematics',
            description: 'Mathematics subject for secondary education',
            createdBy: adminUser._id
        });

        // Create papers for Mathematics
        const mathPaper1 = await Paper.create({
            name: 'Paper 1',
            description: 'Algebra and Calculus',
            subject: mathSubject._id,
            createdBy: adminUser._id
        });

        const mathPaper2 = await Paper.create({
            name: 'Paper 2',
            description: 'Geometry and Trigonometry',
            subject: mathSubject._id,
            createdBy: adminUser._id
        });

        // Create sections for Paper 1
        const mathP1SectionA = await Section.create({
            name: 'Section A',
            paper: mathPaper1._id,
            order: 0,
            createdBy: adminUser._id
        });

        const mathP1SectionB = await Section.create({
            name: 'Section B',
            paper: mathPaper1._id,
            order: 1,
            createdBy: adminUser._id
        });

        // Update Paper 1 with sections
        mathPaper1.sections = [mathP1SectionA._id, mathP1SectionB._id];
        await mathPaper1.save();

        // Create topics for Paper 1
        const algebraTopic = await Topic.create({
            name: 'Algebra',
            paper: mathPaper1._id,
            section: mathP1SectionA._id,
            createdBy: adminUser._id
        });

        const calculusTopic = await Topic.create({
            name: 'Calculus',
            paper: mathPaper1._id,
            section: mathP1SectionB._id,
            createdBy: adminUser._id
        });

        // Update Paper 1 with topics
        mathPaper1.topics = [algebraTopic._id, calculusTopic._id];
        await mathPaper1.save();

        // Create topics for Paper 2
        const geometryTopic = await Topic.create({
            name: 'Geometry',
            paper: mathPaper2._id,
            createdBy: adminUser._id
        });

        const trigonometryTopic = await Topic.create({
            name: 'Trigonometry',
            paper: mathPaper2._id,
            createdBy: adminUser._id
        });

        // Update Paper 2 with topics
        mathPaper2.topics = [geometryTopic._id, trigonometryTopic._id];
        await mathPaper2.save();

        // Update subject with papers
        mathSubject.papers = [mathPaper1._id, mathPaper2._id];
        await mathSubject.save();

        console.log('✅ Mathematics subject created with papers, sections, and topics');

        // Create sample questions
        console.log('\n❓ Creating sample questions...');

        const question1 = await Question.create({
            subject: mathSubject._id,
            paper: mathPaper1._id,
            topic: algebraTopic._id,
            section: mathP1SectionA._id,
            questionText: 'Solve for x: 2x + 5 = 15',
            questionInlineImages: [],
            answerText: 'x = 5\n\nExplanation:\n2x + 5 = 15\n2x = 15 - 5\n2x = 10\nx = 5',
            answerInlineImages: [],
            marks: 3,
            createdBy: editorUser._id
        });

        const question2 = await Question.create({
            subject: mathSubject._id,
            paper: mathPaper1._id,
            topic: calculusTopic._id,
            section: mathP1SectionB._id,
            questionText: 'Find the derivative of f(x) = 3x² + 2x - 1',
            questionInlineImages: [],
            answerText: "f'(x) = 6x + 2\n\nExplanation:\nUsing the power rule:\nd/dx(3x²) = 6x\nd/dx(2x) = 2\nd/dx(-1) = 0\nTherefore, f'(x) = 6x + 2",
            answerInlineImages: [],
            marks: 4,
            createdBy: editorUser._id
        });

        const question3 = await Question.create({
            subject: mathSubject._id,
            paper: mathPaper2._id,
            topic: geometryTopic._id,
            questionText: 'Calculate the area of a triangle with base 10cm and height 8cm',
            questionInlineImages: [],
            answerText: 'Area = 40 cm²\n\nExplanation:\nArea of triangle = (1/2) × base × height\nArea = (1/2) × 10 × 8\nArea = 40 cm²',
            answerInlineImages: [],
            marks: 2,
            createdBy: editorUser._id
        });

        console.log('✅ Sample questions created');

        // Create English subject
        console.log('\n📚 Creating English subject...');
        const englishSubject = await Subject.create({
            name: 'English',
            description: 'English language and literature',
            createdBy: adminUser._id
        });

        const englishPaper1 = await Paper.create({
            name: 'Paper 1',
            description: 'Grammar and Composition',
            subject: englishSubject._id,
            createdBy: adminUser._id
        });

        const grammarTopic = await Topic.create({
            name: 'Grammar',
            paper: englishPaper1._id,
            createdBy: adminUser._id
        });

        englishPaper1.topics = [grammarTopic._id];
        await englishPaper1.save();

        englishSubject.papers = [englishPaper1._id];
        await englishSubject.save();

        console.log('✅ English subject created');

        // Print summary
        console.log('\n' + '='.repeat(50));
        console.log('📊 DATABASE SEEDING COMPLETE');
        console.log('='.repeat(50));
        console.log('\n✅ Created:');
        console.log(`   - 2 Users (1 Admin, 1 Editor)`);
        console.log(`   - 2 Subjects (Mathematics, English)`);
        console.log(`   - 3 Papers`);
        console.log(`   - 2 Sections`);
        console.log(`   - 5 Topics`);
        console.log(`   - 3 Questions`);
        
        console.log('\n🔑 Login Credentials:');
        console.log('\n   Admin:');
        console.log(`   Phone: ${adminUser.phoneNumber}`);
        console.log(`   Password: admin123`);
        console.log('\n   Editor:');
        console.log(`   Phone: ${editorUser.phoneNumber}`);
        console.log(`   Password: editor123`);
        
        console.log('\n');

        // Close connection
        await mongoose.connection.close();
        console.log('✅ Database connection closed');
        process.exit(0);

    } catch (error) {
        console.error('❌ Seeding error:', error);
        process.exit(1);
    }
};

// Run seeding
seedDatabase();
