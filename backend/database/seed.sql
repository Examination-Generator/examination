-- PostgreSQL Seed Data for Examination System
-- Created: November 6, 2025

-- Clear existing data (in reverse order of dependencies)
DELETE FROM question_images;
DELETE FROM questions;
DELETE FROM sections;
DELETE FROM topics;
DELETE FROM papers;
DELETE FROM subjects;
DELETE FROM otp_logs;
DELETE FROM users WHERE phone_number NOT IN ('+254700000000', '+254700000001');

-- Seed Admin and Editor users (if not already exists)
INSERT INTO users (id, phone_number, full_name, password, role, otp_verified)
VALUES 
    ('a0000000-0000-0000-0000-000000000001', '+254700000000', 'System Administrator', '$2a$10$YourHashedPasswordHere', 'admin', true),
    ('a0000000-0000-0000-0000-000000000002', '+254700000001', 'Question Editor', '$2a$10$YourHashedPasswordHere', 'editor', true)
ON CONFLICT (phone_number) DO NOTHING;

-- Seed Subjects
INSERT INTO subjects (id, name, description, created_by)
VALUES 
    ('b0000000-0000-0000-0000-000000000001', 'Mathematics', 'Mathematics and Numerical Skills', 'a0000000-0000-0000-0000-000000000002'),
    ('b0000000-0000-0000-0000-000000000002', 'English', 'English Language and Literature', 'a0000000-0000-0000-0000-000000000002'),
    ('b0000000-0000-0000-0000-000000000003', 'Physics', 'Physical Sciences', 'a0000000-0000-0000-0000-000000000002')
ON CONFLICT (name) DO NOTHING;

-- Seed Papers for Mathematics
INSERT INTO papers (id, name, subject_id, description, created_by)
VALUES 
    ('c0000000-0000-0000-0000-000000000001', 'Paper 1', 'b0000000-0000-0000-0000-000000000001', 'Algebra and Geometry', 'a0000000-0000-0000-0000-000000000002'),
    ('c0000000-0000-0000-0000-000000000002', 'Paper 2', 'b0000000-0000-0000-0000-000000000001', 'Statistics and Probability', 'a0000000-0000-0000-0000-000000000002'),
    ('c0000000-0000-0000-0000-000000000003', 'Paper 3', 'b0000000-0000-0000-0000-000000000001', 'Calculus and Advanced Math', 'a0000000-0000-0000-0000-000000000002')
ON CONFLICT (subject_id, name) DO NOTHING;

-- Seed Papers for English
INSERT INTO papers (id, name, subject_id, description, created_by)
VALUES 
    ('c0000000-0000-0000-0000-000000000004', 'Paper 1', 'b0000000-0000-0000-0000-000000000002', 'Grammar and Composition', 'a0000000-0000-0000-0000-000000000002'),
    ('c0000000-0000-0000-0000-000000000005', 'Paper 2', 'b0000000-0000-0000-0000-000000000002', 'Literature and Poetry', 'a0000000-0000-0000-0000-000000000002')
ON CONFLICT (subject_id, name) DO NOTHING;

-- Seed Topics for Mathematics Paper 1
INSERT INTO topics (id, name, paper_id, created_by)
VALUES 
    ('d0000000-0000-0000-0000-000000000001', 'Algebra', 'c0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000002'),
    ('d0000000-0000-0000-0000-000000000002', 'Geometry', 'c0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000002'),
    ('d0000000-0000-0000-0000-000000000003', 'Trigonometry', 'c0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000002')
ON CONFLICT (paper_id, name) DO NOTHING;

-- Seed Topics for Mathematics Paper 2
INSERT INTO topics (id, name, paper_id, created_by)
VALUES 
    ('d0000000-0000-0000-0000-000000000004', 'Statistics', 'c0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000002'),
    ('d0000000-0000-0000-0000-000000000005', 'Probability', 'c0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000002')
ON CONFLICT (paper_id, name) DO NOTHING;

-- Seed Sections for Mathematics Paper 1
INSERT INTO sections (id, name, paper_id, created_by)
VALUES 
    ('e0000000-0000-0000-0000-000000000001', 'Section A', 'c0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000002'),
    ('e0000000-0000-0000-0000-000000000002', 'Section B', 'c0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000002')
ON CONFLICT (paper_id, name) DO NOTHING;

-- Seed Sample Questions
INSERT INTO questions (
    id, subject_id, paper_id, topic_id, section_id, 
    question_text, question_type, difficulty, marks, 
    correct_answer, answer_explanation, options, created_by
)
VALUES 
    (
        'f0000000-0000-0000-0000-000000000001',
        'b0000000-0000-0000-0000-000000000001',
        'c0000000-0000-0000-0000-000000000001',
        'd0000000-0000-0000-0000-000000000001',
        'e0000000-0000-0000-0000-000000000001',
        'Solve for x: 2x + 5 = 13',
        'short_answer',
        'easy',
        2,
        'x = 4',
        '2x + 5 = 13, subtract 5 from both sides: 2x = 8, divide by 2: x = 4',
        NULL,
        'a0000000-0000-0000-0000-000000000002'
    ),
    (
        'f0000000-0000-0000-0000-000000000002',
        'b0000000-0000-0000-0000-000000000001',
        'c0000000-0000-0000-0000-000000000001',
        'd0000000-0000-0000-0000-000000000002',
        'e0000000-0000-0000-0000-000000000001',
        'Calculate the area of a circle with radius 7cm (use π = 22/7)',
        'short_answer',
        'medium',
        3,
        '154 cm²',
        'Area = πr² = (22/7) × 7² = (22/7) × 49 = 154 cm²',
        NULL,
        'a0000000-0000-0000-0000-000000000002'
    ),
    (
        'f0000000-0000-0000-0000-000000000003',
        'b0000000-0000-0000-0000-000000000001',
        'c0000000-0000-0000-0000-000000000001',
        'd0000000-0000-0000-0000-000000000001',
        'e0000000-0000-0000-0000-000000000002',
        'What is the value of x² when x = 5?',
        'multiple_choice',
        'easy',
        1,
        '25',
        'x² = 5² = 5 × 5 = 25',
        '["10", "15", "20", "25"]'::jsonb,
        'a0000000-0000-0000-0000-000000000002'
    );

-- Verify data insertion
SELECT 'Users: ' || COUNT(*) FROM users;
SELECT 'Subjects: ' || COUNT(*) FROM subjects;
SELECT 'Papers: ' || COUNT(*) FROM papers;
SELECT 'Topics: ' || COUNT(*) FROM topics;
SELECT 'Sections: ' || COUNT(*) FROM sections;
SELECT 'Questions: ' || COUNT(*) FROM questions;
