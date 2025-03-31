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
        groq_api_key=groq_api_key, 
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

# Streamlit UI
# def run_standalone_ui():
#     st.title("Candidate Matching for Job")

#     with st.form("job_form"):
#         job_id = st.text_input("Enter Job ID")
#         num_candidates = st.slider("Number of top candidates to display", 1, 20, 5)
#         submit_button = st.form_submit_button("Analyze")

#     if submit_button:
#         job_description = get_job_description(job_id)
#         if not job_description:
#             st.error(f"No job description found for Job ID {job_id}")
#         else:
#             st.subheader(f"Job Description for {job_id}")
#             st.write(job_description)
            
#             # Get all candidates
#             all_candidates = get_all_candidates()
            
#             if all_candidates:
#                 # Show progress
#                 progress_bar = st.progress(0)
#                 status_text = st.empty()
                
#                 # Process candidates and calculate match
#                 candidate_matches = []
#                 for i, (candidate_id, resume_text) in enumerate(all_candidates):
#                     status_text.text(f"Analyzing candidate {i+1} of {len(all_candidates)}...")
#                     progress_bar.progress((i+1) / len(all_candidates))
                    
#                     try:
#                         match_result = summarize_candidate(resume_text, job_description, groq_api_key)
#                         candidate_matches.append({
#                             "candidate_id": candidate_id,
#                             "resume_text": resume_text,
#                             "match_percentage": match_result.match_percentage,
#                             "summary": match_result.summary
#                         })
#                     except Exception as e:
#                         st.warning(f"Error analyzing candidate {candidate_id}: {str(e)}")
                
#                 # Sort by match percentage (descending)
#                 sorted_matches = sorted(candidate_matches, key=lambda x: x["match_percentage"], reverse=True)
                
#                 # Display top candidates
#                 st.subheader(f"Top {num_candidates} Candidates for Job ID: {job_id}")
                
#                 for i, match in enumerate(sorted_matches[:num_candidates]):
#                     with st.expander(f"Candidate {i+1}: {match['candidate_id']} - Match: {match['match_percentage']:.1f}%"):
#                         st.write(f"**Match Percentage:** {match['match_percentage']:.1f}%")
#                         st.write(f"**Analysis Summary:** {match['summary']}")
#                         st.write("**Resume Text:**")
#                         st.text_area("", match['resume_text'], height=150, key=f"resume_{i}")
                
#                 # Option to save results
#                 if st.button("Save Match Results to Database"):
#                     # Add code here to save the results back to the database
#                     conn_string = f"host={DB_HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} port={DB_PORT}"
                    
#                     with psycopg.connect(conn_string) as conn:
#                         with conn.cursor() as cursor:
#                             for match in candidate_matches:
#                                 cursor.execute("""
#                                 INSERT INTO job_candidate_match (job_id, candidate_id, match_score, match_summary) 
#                                 VALUES (%s, %s, %s, %s)
#                                 ON CONFLICT (job_id, candidate_id) 
#                                 DO UPDATE SET match_score = %s, match_summary = %s
#                                 """, 
#                                 (
#                                     job_id, 
#                                     match["candidate_id"], 
#                                     match["match_percentage"], 
#                                     match["summary"],
#                                     match["match_percentage"],
#                                     match["summary"]
#                                 ))
                    
#                     st.success("Match results saved to database!")
                    
#             else:
#                 st.warning("No candidate resumes found in the database.")


def save_match_results(job_id, candidate_matches):
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
                    VALUES (%s, %s, %s, %s, %s);
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