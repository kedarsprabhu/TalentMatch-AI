# TalentMatch AI

*Precision Matching for Your Perfect Hire*
<img width="917" alt="image" src="https://github.com/user-attachments/assets/018d743f-06d8-42f1-8fdc-9364e50d29bb" />

## Overview

TalentMatch AI is an advanced resume scanning and candidate matching platform that leverages artificial intelligence to identify the best candidates for your job openings. The system analyzes resumes against job descriptions to provide percentage-based matching scores and detailed candidate assessments.
Try the platform at [TalentMatch AI](https://talentmatchai.streamlit.app/).

## Features

- **AI-Powered Resume Analysis**: Automatically extract and analyze information from candidate resumes
- **Intelligent Job Matching**: Match candidates to job descriptions with percentage-based scoring
- **Candidate Ranking**: View top candidates sorted by match percentage
- **Detailed Summaries**: Get AI-generated summaries explaining why each candidate is a good match
- **Database Integration**: Store job descriptions, candidate information, and match results
- **Performance Monitoring**: Integrated with Langfuse for LLM observability and monitoring
- **User-Friendly Interface**: Simple Streamlit interface for easy navigation and use

## Getting Started

### Prerequisites

- Python 3.10+ (Using Python 3.10.11)
- PostgreSQL database
- Groq API key (for AI analysis)
- Langfuse account (for monitoring)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/talentmatch-ai.git
   cd talentmatch-ai
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```
   # API Keys
   export GROQ_API_KEY="your_groq_api_key"
   
   # Database Configuration
   export DB_HOST="your_db_host"
   export DB_NAME="your_db_name"
   export DB_USER="your_db_user"
   export DB_PASSWORD="your_db_password"
   export DB_PORT="your_db_port"
   
   # Langfuse Monitoring
   export LANGFUSE_HOST="your_langfuse_host"
   export LANGFUSE_PUBLIC_KEY="your_langfuse_public_key"
   export LANGFUSE_SECRET_KEY="your_langfuse_secret_key"
   ```

4. Run the application:
   ```
   streamlit run main.py
   ```

## Usage

### Home Page
Navigate through the main application pages:
- Upload candidate resumes
- Post job descriptions
- Find candidate matches for specific job IDs

### Post a Job Description
- Given a link from careers page, scrapes all job requirement details on the page
- Also manually enter job details including title, description, and requirements
- System will generate a unique job ID for future reference

### Find Candidates
- Enter a job ID to retrieve the associated job description
- Set the number of top candidates to display
- View match percentages and detailed analysis for each candidate
- Save match results to the database for future reference

## Database Schema

The application uses the following main tables:
- `candidate_reumes`: Stores candidate information and resume text
- `job_descriptions`: Stores job descriptions and requirements
- `job_candidate_match`: Records matching scores and summaries

## Monitoring

TalentMatch AI uses Langfuse for monitoring and observability of LLM interactions:
- Track performance metrics of AI analysis operations
- Monitor latency and response times
- Analyze cost and usage patterns
- Debug and optimize AI prompt engineering

## Technologies Used

- **Streamlit**: For the web application interface
- **Groq API**: For AI-powered resume analysis and matching
- **PostgreSQL**: Database for storing all application data
- **psycopg**: PostgreSQL adapter for Python
- **Langfuse**: For LLM observability and monitoring

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or support, please open an issue on GitHub or contact: kedarprabhu2000@gmail.com.
