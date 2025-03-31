import logging
from uuid import uuid4
import streamlit as st
import resume_upload_streamlit
import resume_scanner, os

groq_api_key = os.environ['GROQ_API_KEY']
# At the top of your main file
if "initialized" not in st.session_state:
    st.session_state.initialized = True

# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "main"

# Initialize session state for candidate matches
if "candidate_matches" not in st.session_state:
    st.session_state.candidate_matches = None
if "job_id" not in st.session_state:
    st.session_state.job_id = None

# Function to navigate pages
def switch_page(page_name):
    if st.session_state.page != page_name:
        st.session_state.page = page_name
        st.rerun()


def home_page():
    st.title("TalentMatch AI - AI Candidate Matching")
    resume_upload_streamlit.main_page()
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("If you are recruiting, click here to post a job description", key="post_job_button"):
            switch_page("post_job")
    with col2:
        if st.button("Find Candidates for a Job ID", key="view_candidates_button"):
            switch_page("view_candidates")


def post_job_description_page():
    st.title("Post a Job Description")
    resume_upload_streamlit.post_job_description_page()

    # Create a truly unique key for this button
    back_key = f"back_from_post_job_{str(uuid4())}"
    if st.button("Back to Home Page", key=back_key):
        switch_page("main")

def view_candidates_page():
    st.title("Find Candidates for a Job")

    # Use a form for the initial job ID input
    with st.form("job_form"):
        job_id = st.text_input("Enter Job ID")
        num_candidates = st.slider("Number of top candidates to display", 1, 20, 5)
        submit_button = st.form_submit_button("Analyze")

    # If form is submitted, store job_id and process candidates
    if submit_button and job_id:
        st.session_state.job_id = job_id
        st.session_state.num_candidates = num_candidates
        
        try:
            job_description = resume_scanner.get_job_description(job_id)
            st.write("Job description fetch attempt completed")
        except Exception as e:
            st.error(f"Error fetching job description: {e}")
            st.stop()
        
        if not job_description:
            st.error(f"No job description found for Job ID {job_id}")
            st.session_state.candidate_matches = None
        else:
            st.subheader(f"Job Description for {job_id}")
            st.write(job_description)
            
            # Get all candidates
            try:
                all_candidates = resume_scanner.get_all_candidates()
                if not all_candidates:
                    st.warning("No candidate resumes found in the database.")
                    st.session_state.candidate_matches = None
                    st.stop()
            except Exception as e:
                st.error(f"Error fetching candidates: {e}")
                st.session_state.candidate_matches = None
                st.stop()
            
            if all_candidates:
                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Process candidates and calculate match
                candidate_matches = []
                for i, (candidate_id, resume_text) in enumerate(all_candidates):
                    status_text.text(f"Analyzing candidate {i+1} of {len(all_candidates)}...")
                    progress_bar.progress((i+1) / len(all_candidates))
                    
                    try:
                        match_result = resume_scanner.summarize_candidate(resume_text, job_description, groq_api_key=groq_api_key)
                        candidate_name = resume_upload_streamlit.extract_candidate_name(resume_text)
        
                        candidate_matches.append({
                            "candidate_id": candidate_id,
                            "candidate_name": candidate_name,
                            "resume_text": resume_text,
                            "match_percentage": match_result.match_percentage,
                            "summary": match_result.summary
                        })
                    except Exception as e:
                        print(f"Detailed error: {str(e)}")
                        st.warning(f"Error analyzing candidate {candidate_id}: {str(e)}")
                
                # Store candidate matches in session state
                st.session_state.candidate_matches = candidate_matches

    # Display candidates if they've been processed (either from new analysis or from session state)
    if st.session_state.candidate_matches and st.session_state.job_id:
        job_id = st.session_state.job_id
        candidate_matches = st.session_state.candidate_matches
        
        # Sort by match percentage (descending)
        sorted_matches = sorted(candidate_matches, key=lambda x: x["match_percentage"], reverse=True)
        
        # Get number of candidates to display (default to 5 if not set)
        num_candidates = st.session_state.get("num_candidates", 5)

        # Display top candidates
        st.subheader(f"Top {num_candidates} Candidates for Job ID: {job_id}")

        for i, match in enumerate(sorted_matches[:num_candidates]):
            with st.expander(f"Candidate {i+1}: {match['candidate_name']} - Match: {match['match_percentage']:.1f}%"):
                st.write(f"**Match Percentage:** {match['match_percentage']:.1f}%")
                st.write(f"**Analysis Summary:** {match['summary']}")
                st.write("**Resume Text:**")
                st.text_area("", match['resume_text'], height=150, key=f"resume_{i}")
        
        # Option to save results - Use a separate key for this form
        with st.form(key="save_results_form"):
            st.write("Save these match results to the database?")
            save_submit = st.form_submit_button("Save Match Results")
            
            if save_submit:
                try:
                    # Debug the data being passed
                    st.write(f"Attempting to save data for {len(candidate_matches)} candidates")
                    
                    # Save the results back to the database
                    saved = resume_scanner.save_match_results(job_id, candidate_matches)
                    
                    if saved:
                        st.success("Match results saved to database!")
                    else:
                        st.error("Failed to save match results to database.")
                except Exception as e:
                    st.error(f"Error saving to database: {str(e)}")
                    st.write("Error details:", str(e))

    # Back to Main Page with a unique key
    if st.button("Back to Home Page", key="back_from_view_candidates"):
        # Clear session state when going back
        st.session_state.candidate_matches = None
        st.session_state.job_id = None
        switch_page("main")

# Display the appropriate page based on session state
if st.session_state.page == "main":
    home_page()
elif st.session_state.page == "post_job":
    post_job_description_page()
elif st.session_state.page == "view_candidates":
    view_candidates_page()