-- Create the resumes table
CREATE TABLE IF NOT EXISTS resumes (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    full_name TEXT,
    email TEXT,
    phone TEXT,
    skills TEXT[],
    experience_years FLOAT,
    last_job_title TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on uploaded_at for better query performance
CREATE INDEX IF NOT EXISTS idx_resumes_uploaded_at ON resumes(uploaded_at);

-- Create index on email for searching
CREATE INDEX IF NOT EXISTS idx_resumes_email ON resumes(email);

-- Insert sample data for testing (optional)
INSERT INTO resumes (filename, full_name, email, phone, skills, experience_years, last_job_title) 
VALUES 
    ('sample_resume.pdf', 'John Doe', 'john.doe@example.com', '+1-555-0123', 
     ARRAY['Python', 'FastAPI', 'PostgreSQL', 'Docker'], 5.5, 'Senior Software Engineer'),
    ('test_resume.pdf', 'Jane Smith', 'jane.smith@example.com', '+1-555-0456', 
     ARRAY['JavaScript', 'React', 'Node.js', 'MongoDB'], 3.0, 'Frontend Developer')
ON CONFLICT DO NOTHING; 