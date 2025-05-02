from datetime import datetime
import uuid
import streamlit as st
import psycopg
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langfuse.callback import CallbackHandler
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser

# Load environment variables
load_dotenv(".env")

# Database credentials
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

# LLM Configuration
groq_api_key = os.environ['GROQ_API_KEY']
langfuse_handler = CallbackHandler(
    secret_key=os.environ.get("LANGFUSE_SECRET_KEY"),
    public_key=os.environ.get("LANGFUSE_PUBLIC_KEY"),
    host=os.environ.get("LANGFUSE_HOST"),
)
langfuse_handler.auth_check()


class CandidateMatch(BaseModel):
    """Model for candidate match analysis."""
    summary: str = Field(description="5-6 sentence summary of how well the candidate matches the job")
    match_percentage: float = Field(description="A percentage (0-100) indicating how well the candidate matches the job")

def summarize_candidate(resume_text, job_description, groq_api_key=None):
    if groq_api_key is None:
        groq_api_key = os.environ['GROQ_API_KEY']
        if not groq_api_key:
            raise ValueError("GROQ API key not found")
    # Create a parser for the Pydantic model
    parser = PydanticOutputParser(pydantic_object=CandidateMatch)
    
    # Create a prompt template
    prompt = ChatPromptTemplate.from_template("""
    As a Talent Acquisition AI, analyze how well this candidate matches the given job description.

    **Candidate Resume:**  
    {resume_text}

    **Job Description:**  
    {job_description}

    Based on the candidate's skills, experience, and qualifications compared to the job requirements,
    provide a concise summary (3-5 sentences) and calculate a match percentage (0-100%).

    {format_instructions}
    """)
    
    # Set up the model
    model = ChatGroq(
        temperature=0.2, 
        api_key=groq_api_key, 
        model_name="llama-3.1-8b-instant"
    )
    
    # Create the chain with the Pydantic parser
    chain = prompt | model | parser
    
    # Invoke the chain
    result = chain.invoke({
        "resume_text": resume_text,
        "job_description": job_description,
        "format_instructions": parser.get_format_instructions()
    }, config={"callbacks": [langfuse_handler]})
    return result

# Get all candidate resumes
def get_all_candidates():
    conn_string = f"host={DB_HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} port={DB_PORT}"
    
    with psycopg.connect(conn_string) as conn:
        with conn.cursor() as cursor:
            query = """
            SELECT candidate_id, resume_text
            FROM candidate_resumes;
            """
            cursor.execute(query)
            return cursor.fetchall()

# Fetch job description
def get_job_description(job_id):
    """Fetch job description by job_id."""
    conn_string = f"host={DB_HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} port={DB_PORT}"
    
    try:
        job_id = uuid.UUID(job_id)
    except ValueError:
        st.error("Invalid Job ID format. Please enter a valid UUID.")
        return None

    with psycopg.connect(conn_string) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT job_description FROM job_descriptions WHERE job_id = %s", (job_id,))
            result = cursor.fetchone()
            return result[0] if result else None


def save_match_results(job_id, candidate_matches):
    conn=None
    try:
        # Connect to the database
        conn_string = f"host={DB_HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} port={DB_PORT}"
        
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cursor:
                # For each candidate match, insert a record
                for match in candidate_matches:
                    query = """
                    INSERT INTO job_candidate_match
                    (job_id, candidate_id, match_score, match_summary, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (job_id, candidate_id)
                    DO UPDATE SET
                        match_score = EXCLUDED.match_score,
                        match_summary = EXCLUDED.match_summary,
                        created_at = EXCLUDED.created_at;
                    """
                    created_at = datetime.now()
                    cursor.execute(query, (
                        job_id, 
                        match['candidate_id'],
                        match['match_percentage'],
                        match['summary'],
                        created_at
                    ))
                
                # Commit the transaction
                conn.commit()
                return True
    except Exception as e:
        print(f"Database error: {str(e)}")
        return False
    
def get_all_jobs():
    """
    Retrieves all job IDs and descriptions from the database.
    
    Returns:
        list: A list of tuples containing (job_id, job_description)
    """
    conn = None
    try:
        # Connect to the database
        conn_string = f"host={DB_HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} port={DB_PORT}"
        conn = psycopg.connect(conn_string)

        # Create a cursor
        cursor = conn.cursor()
        # conn = get_db_connection()
        # cursor = conn.cursor()
        
        # Query to get all jobs
        cursor.execute("SELECT job_id, job_description FROM job_descriptions ORDER BY job_id DESC")
        
        # Fetch all results
        all_jobs = cursor.fetchall()
        
        # Close connection
        cursor.close()
        conn.close()
        
        return all_jobs
    except Exception as e:
        print(f"Error fetching all jobs: {str(e)}")
        raise e