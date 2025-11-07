-- PostgreSQL Database Schema for Examination System
-- Created: November 6, 2025

-- Drop existing tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS question_images CASCADE;
DROP TABLE IF EXISTS questions CASCADE;
DROP TABLE IF EXISTS sections CASCADE;
DROP TABLE IF EXISTS topics CASCADE;
DROP TABLE IF EXISTS papers CASCADE;
DROP TABLE IF EXISTS subjects CASCADE;
DROP TABLE IF EXISTS otp_logs CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'editor', 'admin')),
    is_active BOOLEAN DEFAULT true,
    otp_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- OTP Logs Table
CREATE TABLE otp_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number VARCHAR(20) NOT NULL,
    otp VARCHAR(10) NOT NULL,
    purpose VARCHAR(50) NOT NULL CHECK (purpose IN ('registration', 'login', 'password_reset')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'verified', 'expired', 'failed')),
    expires_at TIMESTAMP NOT NULL,
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_otp_user FOREIGN KEY (phone_number) REFERENCES users(phone_number) ON DELETE CASCADE
);

-- Subjects Table
CREATE TABLE subjects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_by UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_subject_creator FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Papers Table
CREATE TABLE papers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    subject_id UUID NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_by UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_paper_subject FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    CONSTRAINT fk_paper_creator FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT unique_paper_per_subject UNIQUE (subject_id, name)
);

-- Topics Table
CREATE TABLE topics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    paper_id UUID NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_by UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_topic_paper FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE,
    CONSTRAINT fk_topic_creator FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT unique_topic_per_paper UNIQUE (paper_id, name)
);

-- Sections Table
CREATE TABLE sections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    paper_id UUID NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_by UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_section_paper FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE,
    CONSTRAINT fk_section_creator FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT unique_section_per_paper UNIQUE (paper_id, name)
);

-- Questions Table
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subject_id UUID NOT NULL,
    paper_id UUID NOT NULL,
    topic_id UUID NOT NULL,
    section_id UUID,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) DEFAULT 'multiple_choice' CHECK (question_type IN ('multiple_choice', 'true_false', 'short_answer', 'essay', 'structured')),
    difficulty VARCHAR(20) DEFAULT 'medium' CHECK (difficulty IN ('easy', 'medium', 'hard')),
    marks INTEGER DEFAULT 1,
    
    -- Answer fields
    correct_answer TEXT,
    answer_explanation TEXT,
    
    -- Multiple choice options (stored as JSON)
    options JSONB,
    
    -- Metadata
    is_active BOOLEAN DEFAULT true,
    times_used INTEGER DEFAULT 0,
    last_used TIMESTAMP,
    created_by UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_question_subject FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    CONSTRAINT fk_question_paper FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE,
    CONSTRAINT fk_question_topic FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    CONSTRAINT fk_question_section FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE SET NULL,
    CONSTRAINT fk_question_creator FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Question Images Table
CREATE TABLE question_images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    question_id UUID NOT NULL,
    image_type VARCHAR(20) CHECK (image_type IN ('question', 'answer')),
    image_url TEXT NOT NULL,
    image_name VARCHAR(255),
    position INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_image_question FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_users_phone ON users(phone_number);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_otp_phone_status ON otp_logs(phone_number, status);
CREATE INDEX idx_subjects_active ON subjects(is_active);
CREATE INDEX idx_papers_subject ON papers(subject_id);
CREATE INDEX idx_topics_paper ON topics(paper_id);
CREATE INDEX idx_sections_paper ON sections(paper_id);
CREATE INDEX idx_questions_subject ON questions(subject_id);
CREATE INDEX idx_questions_paper ON questions(paper_id);
CREATE INDEX idx_questions_topic ON questions(topic_id);
CREATE INDEX idx_questions_active ON questions(is_active);
CREATE INDEX idx_question_images_question ON question_images(question_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to all tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subjects_updated_at BEFORE UPDATE ON subjects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_papers_updated_at BEFORE UPDATE ON papers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_topics_updated_at BEFORE UPDATE ON topics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sections_updated_at BEFORE UPDATE ON sections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_questions_updated_at BEFORE UPDATE ON questions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (password: admin123)
-- Note: This is a bcrypt hash of "admin123" - change in production!
INSERT INTO users (phone_number, full_name, password, role, otp_verified)
VALUES (
    '+254700000000',
    'System Administrator',
    '$2a$10$rQ3K3Y8JYKz8Z0gY5Z0Z0eu5Z0Z0Z0Z0Z0Z0Z0Z0Z0Z0Z0Z0Z0Z0',
    'admin',
    true
);

-- Insert default editor user (password: editor123)
INSERT INTO users (phone_number, full_name, password, role, otp_verified)
VALUES (
    '+254700000001',
    'Question Editor',
    '$2a$10$rQ3K3Y8JYKz8Z0gY5Z0Z0eu5Z0Z0Z0Z0Z0Z0Z0Z0Z0Z0Z0Z0Z0Z0',
    'editor',
    true
);

-- Comments for documentation
COMMENT ON TABLE users IS 'Stores user account information';
COMMENT ON TABLE otp_logs IS 'Logs OTP verification attempts';
COMMENT ON TABLE subjects IS 'Academic subjects (e.g., Mathematics, English)';
COMMENT ON TABLE papers IS 'Exam papers within subjects (e.g., Paper 1, Paper 2)';
COMMENT ON TABLE topics IS 'Topics within papers (e.g., Algebra, Geometry)';
COMMENT ON TABLE sections IS 'Exam paper sections (e.g., Section A, Section B)';
COMMENT ON TABLE questions IS 'Question bank with answers and metadata';
COMMENT ON TABLE question_images IS 'Images associated with questions or answers';
