import streamlit as st
import resume_upload_streamlit
import resume_scanner, os
from PIL import Image
import streamlit as st

st.set_page_config(
    page_title="TalentMatch AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css(file_path):
    with open(file_path, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

load_css("styles/styles.css") 

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
    logo_image = Image.open("assets/logo.png")
    col1, col2 = st.columns([1, 6])  # Adjust these values to get the right balance

    with col1:
        st.image(logo_image, width=80, use_container_width=True)
    with col2:
        st.markdown("<h1 class='header-title'>TalentMatch AI</h1>", unsafe_allow_html=True)
        st.markdown("<p class='tagline'>Precision Matching for Your Perfect Hire</p>", unsafe_allow_html=True)
    
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    # App description
    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.markdown("""
            <div class="card">
                <p>TalentMatch AI uses advanced artificial intelligence to match the best candidates for your job openings.
                Upload resumes, post job descriptions, and get AI-powered insights to find your ideal hire.</p>
            </div>
            """, unsafe_allow_html=True)
    
    resume_upload_streamlit.main_page()
    
    # Navigation buttons with improved styling
    st.markdown("<h2 class='sub-header'>What would you like to do?</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📝 Post a Job Description", key="post_job_button", use_container_width=True):
            switch_page("post_job")
    with col2:
        if st.button("🔍 Find Candidates for a Job", key="view_candidates_button", use_container_width=True):
            switch_page("view_candidates")
    with col3:
        if st.button("📋 View All Jobs", key="view_jobs_button", use_container_width=True):
            switch_page("view_jobs")


def post_job_description_page():
    st.markdown("<h1 class='main-header'>Post a Job Description</h1>", unsafe_allow_html=True)
    
    # Job posting instructions
    st.markdown("""
    <div class="card">
        <p>Enter your job details below. The system will analyze the job requirements 
        and generate a unique ID for candidate matching.</p>
    </div>
    """, unsafe_allow_html=True)
    
    resume_upload_streamlit.post_job_description_page()


    if st.button("🏠 Back to Home Page", key="back_from_post_job"):
        switch_page("main")

def view_jobs_page():
    st.markdown("<h1 class='main-header'>View All Jobs</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <p>Here are all the jobs currently in the system. You can view job IDs and brief descriptions, 
        or select a job to find matching candidates.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get all jobs from the database
    try:
        all_jobs = resume_scanner.get_all_jobs()
        
        if not all_jobs or len(all_jobs) == 0:
            st.warning("No jobs found in the database.")
        else:
            # Display jobs in a nice table
            st.markdown("<h2 class='sub-header'>Available Jobs</h2>", unsafe_allow_html=True)
            
            # Create a container for the job cards
            st.markdown("<div class='job-card-container'>", unsafe_allow_html=True)
            
            # Split into columns for better layout
            cols = st.columns(2)
            
            for i, (job_id, full_description) in enumerate(all_jobs):
                # Generate a brief description (first ~50 words)
                brief_description = " ".join(full_description.split()[:10]) + "..."
                
                # Alternate between columns
                col_idx = i % 2
                
                with cols[col_idx]:
                    st.markdown(f"""
                    <div class="job-card">
                        <h3>Job ID: {job_id}</h3>
                        <p>{brief_description}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Add standard Streamlit buttons instead of custom HTML buttons
                    button_cols = st.columns(2)
                    with button_cols[0]:
                        if st.button("View Details", key=f"view_full_{job_id}"):
                            st.session_state.full_job_description = full_description
                            st.session_state.selected_job_id = job_id
                            st.rerun()
                    with button_cols[1]:
                        if st.button("Find Candidates", key=f"find_candidates_{job_id}"):
                            st.session_state.job_id = job_id
                            switch_page("view_candidates")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # If a job is selected, display its full description
            if hasattr(st.session_state, 'full_job_description') and hasattr(st.session_state, 'selected_job_id'):
                st.markdown(f"<h2 class='sub-header'>Job Details for ID: {st.session_state.selected_job_id}</h2>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class="card full-job-description">
                    {st.session_state.full_job_description}
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Find Candidates for This Job", key="find_candidates_for_selected"):
                    st.session_state.job_id = st.session_state.selected_job_id
                    switch_page("view_candidates")
    
    except Exception as e:
        st.markdown(f"""
        <div class="error-alert">
            Error fetching jobs: {e}
        </div>
        """, unsafe_allow_html=True)
    
    # Back to Main Page
    if st.button("🏠 Back to Home Page", key="back_from_view_jobs"):
        if hasattr(st.session_state, 'full_job_description'):
            delattr(st.session_state, 'full_job_description')
        if hasattr(st.session_state, 'selected_job_id'):
            delattr(st.session_state, 'selected_job_id')
        switch_page("main")


def view_candidates_page():
    st.markdown("<h1 class='main-header'>Find Candidates for a Job</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <p>Enter a job ID to analyze potential candidates against the job requirements. 
        The system will rank candidates based on their match percentage.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("job_form"):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            # Pre-populate the job ID if it was selected from the view jobs page
            job_id = st.text_input("Enter Job ID", key="job_id_input", 
                                   value=st.session_state.job_id if st.session_state.job_id else "",
                                   autocomplete="on")
        with col2:
            num_candidates = st.slider("Top candidates to display", 1, 20, 5)
        with col3:
            st.write("")  # Empty space for alignment
    
        submit_button = st.form_submit_button("🔍 Analyze Candidates", use_container_width=True)

    # If form is submitted, store job_id and process candidates
    if submit_button and job_id:
        st.session_state.job_id = job_id
        st.session_state.num_candidates = num_candidates
        
        try:
            job_description = resume_scanner.get_job_description(job_id)
            st.success("Job description fetched successfully")
        except Exception as e:
            st.markdown(f"""
            <div class="error-alert">
                Error fetching job description: {e}
            </div>
            """, unsafe_allow_html=True)
            st.stop()
        
        if not job_description:
            st.markdown(f"""
            <div class="error-alert">
                No job description found for Job ID {job_id}
            </div>
            """, unsafe_allow_html=True)
            st.session_state.candidate_matches = None
        else:
            st.markdown(f"<h2 class='sub-header'>Here is the Job Description: </h2>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="card">
                {job_description}
            </div>
            """, unsafe_allow_html=True)
            
            # Get all candidates
            try:
                all_candidates = resume_scanner.get_all_candidates()
                if not all_candidates:
                    st.warning("No candidate resumes found.")
                    st.session_state.candidate_matches = None
                    st.stop()
            except Exception as e:
                st.markdown(f"""
                <div class="error-alert">
                    Error fetching candidates: {e}
                </div>
                """, unsafe_allow_html=True)
                st.session_state.candidate_matches = None
                st.stop()
            
            if all_candidates:
                # Show progress
                st.markdown("<p class='progress-label'>Analyzing candidates...</p>", unsafe_allow_html=True)
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

    # Display candidates if they've been processed
    if st.session_state.candidate_matches and st.session_state.job_id:
        job_id = st.session_state.job_id
        candidate_matches = st.session_state.candidate_matches
        
        # Sort by match percentage (descending)
        sorted_matches = sorted(candidate_matches, key=lambda x: x["match_percentage"], reverse=True)
        
        # Get number of candidates to display (default to 5 if not set)
        num_candidates = st.session_state.get("num_candidates", 5)

        # Display top candidates
        st.markdown(f"<h2 class='sub-header'>Top {num_candidates} Candidates for Job ID: {job_id}</h2>", unsafe_allow_html=True)

        for i, match in enumerate(sorted_matches[:num_candidates]):
            # Determine match class based on percentage
            match_class = "match-high" if match['match_percentage'] >= 80 else "match-medium" if match['match_percentage'] >= 60 else "match-low"
            
            with st.expander(f"Candidate {i+1}: {match['candidate_name']} - Match: {match['match_percentage']:.1f}%"):
                st.markdown(f"""
                <div class="candidate-match {match_class}">
                    <h3><span class="highlight-text">Match Percentage:</span> {match['match_percentage']:.1f}%</h3>
                    <p><span class="highlight-text">Analysis Summary:</span> {match['summary']}</p>
                </div>
                """, unsafe_allow_html=True)
                st.write("**Resume Text:**")
                st.text_area("", match['resume_text'], height=150, key=f"resume_{i}")
        
        with st.form(key="save_results_form"):
            st.write("Save these match results to the database?")
            save_submit = st.form_submit_button("💾 Save Match Results", use_container_width=True)
            
            if save_submit:
                try:
                    # Save the results back to the database
                    saved = resume_scanner.save_match_results(job_id, candidate_matches)
                    
                    if saved:
                        st.markdown("""
                        <div class="success-alert">
                            Match results saved to database!
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="error-alert">
                            Failed to save match results to database.
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f"""
                    <div class="error-alert">
                        Error saving to database: {str(e)}
                    </div>
                    """, unsafe_allow_html=True)

    # Back to Main Page
    if st.button("🏠 Back to Home Page", key="back_from_view_candidates"):
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
elif st.session_state.page == "view_jobs":
    view_jobs_page()