import streamlit as st
from pypdf import PdfReader
import docx
import psycopg
from uuid import uuid4
from datetime import datetime
from dotenv import load_dotenv
import os
import uuid
import requests
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv(".env")

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

# Function to extract text from PDF
def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to extract text from DOCX
def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_candidate_name(resume_text):
    # Get the first line of the resume which often contains the name
    first_line = resume_text.strip().split('\n')[0]
    # Split by common separators and take the first 1-3 words
    words = first_line.split()
    # Take first 1-3 words depending on what's available
    if len(words) >= 3:
        return ' '.join(words[:3]).upper()
    elif len(words) >= 1:
        return ' '.join(words[:len(words)]).upper()
    else:
        return "UNNAMED CANDIDATE"

# Function to insert resume into the database
def insert_resume_into_db(resume_text):
    conn = None
    try:
        # Connect to the database
        conn_string = f"host={DB_HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} port={DB_PORT}"
        
        with psycopg.connect(conn_string) as conn:
            # Create a cursor
            with conn.cursor() as cursor:
            # Insert the resume text into the database
                query = """
                INSERT INTO candidate_resumes (candidate_id, resume_text, created_at)
                VALUES (%s, %s, %s);
                """
                candidate_id = str(uuid4())  # Generate a unique UUID
                created_at = datetime.now()  # Current timestamp
                cursor.execute(query, (candidate_id, resume_text, created_at))

                # Commit the transaction
                conn.commit()
                st.success("Resume uploaded and stored successfully!")

    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        # Close the database connection
        if conn:
            cursor.close()
            conn.close()

# Function to insert job description into the database
def insert_job_description_into_db(job_description):
    conn = None
    try:
        # Connect to the database
        conn_string = f"host={DB_HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} port={DB_PORT}"
        conn = psycopg.connect(conn_string)

        # Create a cursor
        cursor = conn.cursor()

        # Insert the job description into the database
        job_id = str(uuid.uuid4()) 
        created_at = datetime.now()
        st.write(f"Job description entered successfully. Generated Job ID: {job_id}")

        query = """
        INSERT INTO job_descriptions (job_id, job_description, position_fulfilled, created_at)
        VALUES (%s, %s, %s, %s);
        """
        cursor.execute(query, (job_id, job_description, False, created_at))

        # Commit the transaction
        conn.commit()

        st.success("Job description uploaded and stored in the database successfully!")

    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        # Close the database connection
        if conn:
            cursor.close()
            conn.close()

# Function to scrape job description from a URL
def scrape_job_description(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            job_description = soup.get_text(separator="\n", strip=True)
            
            st.session_state.scraped_job_description = job_description
            return job_description
        else:
            print(f"Failed to fetch page. Status code: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error scraping job description: {e} Try manually submitting.")
        return None


# Main page
def main_page():
    if "resume_uploader_key" not in st.session_state:
        st.session_state.resume_uploader_key = str(uuid4())  # Store a unique key

    uploaded_file = st.file_uploader(
        "Upload resume (PDF/DOCX)",
        type=["pdf", "docx"],
        key=st.session_state.resume_uploader_key
    )

    # Process the file if available
    if uploaded_file:
        try:
            if uploaded_file.type == "application/pdf":
                resume_text = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                resume_text = extract_text_from_docx(uploaded_file)
            else:
                st.error("Unsupported file format. Please upload a PDF or DOCX file.")
                resume_text = None
        except Exception as e:
            st.error(f"Failed to process the file: {e}")
            resume_text = None

        # Display the extracted text
        st.subheader("Extracted Text from Resume")
        st.text_area("Resume Text", resume_text, height=300)

        # Store the extracted text in the database
        if st.button("Save to Database"):
            insert_resume_into_db(resume_text)

# Job description posting page
def post_job_description_page():
    st.title("Post a Job Description")

    st.subheader("Option 1: Enter Job Description Manually")
    job_description = st.text_area("Enter Job Description")
    if st.button("Submit Manual Job Description"):
        if job_description.strip():
            insert_job_description_into_db(job_description)
        else:
            st.error("Please enter a job description.")

    # Option to provide a link to scrape the job description
    st.subheader("Option 2: Provide a Link to Scrape Job Description")
    url = st.text_input("Enter Job Posting URL")
    if st.button("Scrape Job Description"):
        if url.strip():
            job_description = scrape_job_description(url)
            if job_description:
                st.session_state.scraped_job_description = job_description

    # Persist scraped text across rerenders
    if "scraped_job_description" in st.session_state:
        st.text_area("Scraped Job Description", st.session_state.scraped_job_description, height=300, key="scraped_text_area")

    # Ensure submission button works
    if st.button("Submit Scraped Job Description"):
        if "scraped_job_description" in st.session_state and st.session_state.scraped_job_description.strip():
            insert_job_description_into_db(st.session_state.scraped_job_description)
        else:
            st.error("No job description found. Please scrape one first.")