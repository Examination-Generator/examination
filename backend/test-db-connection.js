/**
 * Database Connection Test Script
 * Run this to verify MongoDB connection and test CRUD operations
 */

// Load environment variables
require('dotenv').config();

const mongoose = require('mongoose');
const { User, Subject, Paper, Topic, Section } = require('./models/schema');
const connectDB = require('./config/database');

const testDatabaseConnection = async () => {
    try {
        console.log('\n🧪 Starting Database Connection Test...\n');

        // 1. Test MongoDB Connection
        console.log('1️⃣ Testing MongoDB Connection...');
        await connectDB();
        console.log('   ✅ MongoDB connection successful\n');

        // 2. Test User Collection
        console.log('2️⃣ Testing User Collection...');
        const userCount = await User.countDocuments();
        console.log(`   📊 Users in database: ${userCount}`);
        
        if (userCount > 0) {
            const sampleUser = await User.findOne().select('fullName phoneNumber role');
            console.log('   👤 Sample user:', {
                name: sampleUser.fullName,
                phone: sampleUser.phoneNumber,
                role: sampleUser.role
            });
        } else {
            console.log('   ⚠️  No users found. Run: npm run seed');
        }
        console.log('   ✅ User collection accessible\n');

        // 3. Test Subject Collection
        console.log('3️⃣ Testing Subject Collection...');
        const subjectCount = await Subject.countDocuments();
        console.log(`   📚 Subjects in database: ${subjectCount}`);
        
        if (subjectCount > 0) {
            const subjects = await Subject.find()
                .populate({
                    path: 'papers',
                    populate: [
                        { path: 'sections' },
                        { path: 'topics' }
                    ]
                })
                .select('name papers');
            
            console.log('   📋 Subjects list:');
            subjects.forEach(subject => {
                const paperCount = subject.papers?.length || 0;
                let totalTopics = 0;
                let totalSections = 0;
                
                subject.papers?.forEach(paper => {
                    totalTopics += paper.topics?.length || 0;
                    totalSections += paper.sections?.length || 0;
                });
                
                console.log(`      • ${subject.name}: ${paperCount} papers, ${totalTopics} topics, ${totalSections} sections`);
            });
        } else {
            console.log('   ⚠️  No subjects found. Add subjects via EditorDashboard');
        }
        console.log('   ✅ Subject collection accessible\n');

        // 4. Test Paper Collection
        console.log('4️⃣ Testing Paper Collection...');
        const paperCount = await Paper.countDocuments();
        console.log(`   📄 Papers in database: ${paperCount}`);
        console.log('   ✅ Paper collection accessible\n');

        // 5. Test Topic Collection
        console.log('5️⃣ Testing Topic Collection...');
        const topicCount = await Topic.countDocuments();
        console.log(`   🏷️  Topics in database: ${topicCount}`);
        console.log('   ✅ Topic collection accessible\n');

        // 6. Test Section Collection
        console.log('6️⃣ Testing Section Collection...');
        const sectionCount = await Section.countDocuments();
        console.log(`   📑 Sections in database: ${sectionCount}`);
        console.log('   ✅ Section collection accessible\n');

        // 7. Test Write Operation
        console.log('7️⃣ Testing Write Operation...');
        const testSubject = await Subject.create({
            name: 'TEST_SUBJECT_DELETE_ME',
            description: 'This is a test subject for connection verification',
            createdBy: new mongoose.Types.ObjectId()
        });
        console.log('   ✅ Write operation successful (created test subject)\n');

        // 8. Test Read Operation
        console.log('8️⃣ Testing Read Operation...');
        const foundSubject = await Subject.findById(testSubject._id);
        if (foundSubject && foundSubject.name === 'TEST_SUBJECT_DELETE_ME') {
            console.log('   ✅ Read operation successful\n');
        } else {
            throw new Error('Failed to read created test subject');
        }

        // 9. Test Update Operation
        console.log('9️⃣ Testing Update Operation...');
        foundSubject.description = 'Updated test description';
        await foundSubject.save();
        const updatedSubject = await Subject.findById(testSubject._id);
        if (updatedSubject.description === 'Updated test description') {
            console.log('   ✅ Update operation successful\n');
        } else {
            throw new Error('Failed to update test subject');
        }

        // 10. Test Delete Operation
        console.log('🔟 Testing Delete Operation...');
        await Subject.findByIdAndDelete(testSubject._id);
        const deletedSubject = await Subject.findById(testSubject._id);
        if (!deletedSubject) {
            console.log('   ✅ Delete operation successful\n');
        } else {
            throw new Error('Failed to delete test subject');
        }

        // Success summary
        console.log('═══════════════════════════════════════════════════');
        console.log('🎉 ALL DATABASE TESTS PASSED! 🎉');
        console.log('═══════════════════════════════════════════════════');
        console.log('\n✅ Database is ready for use!');
        console.log('✅ All collections are accessible');
        console.log('✅ CRUD operations working correctly\n');

        // Database statistics
        console.log('📊 DATABASE STATISTICS:');
        console.log(`   • Users: ${userCount}`);
        console.log(`   • Subjects: ${subjectCount}`);
        console.log(`   • Papers: ${paperCount}`);
        console.log(`   • Topics: ${topicCount}`);
        console.log(`   • Sections: ${sectionCount}`);
        console.log('\n');

    } catch (error) {
        console.error('\n❌ DATABASE TEST FAILED!\n');
        console.error('Error:', error.message);
        console.error('\nStack trace:');
        console.error(error.stack);
        console.error('\n');
        process.exit(1);
    } finally {
        // Close connection
        await mongoose.connection.close();
        console.log('👋 Database connection closed\n');
        process.exit(0);
    }
};

// Run the test
testDatabaseConnection();
