-- Create Job Descriptions Table
CREATE TABLE job_descriptions (
    job_id SERIAL PRIMARY KEY,  -- Auto-incrementing primary key (automatically indexed)
    job_description TEXT NOT NULL,  -- Combined job description text
    position_fulfilled BOOLEAN NOT NULL DEFAULT FALSE,  -- Is the position filled?
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- Timestamp of creation
    updated_at TIMESTAMP  -- Timestamp of last update
);

-- Create Candidate Resumes Table
CREATE TABLE candidate_resumes (
    candidate_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),  -- UUID as primary key (automatically indexed)
    resume_text TEXT NOT NULL,  -- Combined resume text
    percentage_match NUMERIC(5, 2) CHECK (percentage_match >= 0 AND percentage_match <= 100),  -- Percentage match (0-100)
    rating NUMERIC(3, 1) CHECK (rating >= 0 AND rating <= 5),  -- Rating (0-5)
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- Timestamp of creation
    updated_at TIMESTAMP,  -- Timestamp of last update
    status VARCHAR(20) CHECK (status IN ('New', 'In Review', 'Rejected', 'Hired'))  -- Candidate status
);

-- Indexes for faster queries
CREATE INDEX idx_candidate_resumes_percentage_match ON candidate_resumes (percentage_match DESC);
CREATE INDEX idx_candidate_resumes_rating ON candidate_resumes (rating DESC);