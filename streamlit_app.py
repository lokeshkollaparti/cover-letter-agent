import os
import streamlit as st
import google.generativeai as genai
import PyPDF2

# --- This is the "Engine" we perfected in the Jupyter Notebook ---
def draft_cover_letter_with_gemini(resume, job_desc, template):
    """Constructs a much more forceful and explicit prompt for Gemini."""
    prompt = f"""
    You are an expert career coach and professional resume writer. Your task is to draft a world-class cover letter.

    **CONTEXT:**

    ---RESUME START---
    {resume}
    ---RESUME END---

    ---JOB DESCRIPTION START---
    {job_desc}
    ---JOB DESCRIPTION END---
    
    ---COVER LETTER TEMPLATE START---
    {template}
    ---COVER LETTER TEMPLATE END---

    **CRITICAL INSTRUCTIONS:**

    1.  **ADHERE TO THE TEMPLATE:** You MUST follow the structure of the provided cover letter template exactly. Use all the specified subheadings and bullet points as formatted in the template.

    2.  **SYNTHESIZE, DON'T HALLUCINATE:** Populate the template by extracting and synthesizing information ONLY from the provided resume and job description. Do NOT invent skills or experiences.

    3.  **FILL ALL PLACEHOLDERS:** You must fill every placeholder like `[Company Name]` or `[Exact Position Title]`.

    4.  **HANDLE MISSING INFORMATION INTELLIGENTLY:**
        * If the job description does not mention a specific company mission for the `[Company Mission or Value]` placeholder, you MUST infer a plausible one based on the industry (e.g., "data-driven decision-making," "technological innovation," "enhancing customer experiences").
        * DO NOT, under any circumstances, output the placeholder text itself.

    5.  **POPULATE BULLET POINTS:** For the "Relevant Skills & Alignment" and "Selected Achievements" sections, you MUST populate the bullet points with specific, concise examples and metrics from the resume.

    6.  **FINAL OUTPUT:** The final output should be ONLY the completed cover letter text. Do not include any of your own commentary.
    """
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

# --- This is the "Car Body" - The Streamlit User Interface ---

st.set_page_config(page_title="AI Cover Letter Assistant", page_icon="✍️", layout="wide")
st.title("✍️ AI Cover Letter Assistant")

# IMPORTANT: Configure the API key using Streamlit's secrets management
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("API Key not configured. The app owner needs to set it in the Streamlit secrets.")
    st.stop()

# Use columns for a cleaner layout
col1, col2 = st.columns(2)

with col1:
    st.header("1. Your Information")
    uploaded_resume = st.file_uploader("Upload Your Resume (PDF)", type=['pdf'])
    
    default_template = """[Your Name]
[Your Street Address]
[Your City, State, Zip Code] | [Your Phone Number]
[Your Email Address] | [LinkedIn URL]

[Date]

[Hiring Manager Name]
[Hiring Manager Title]
[Company Name]
[Company Address]

Dear [Mr./Ms./Mx. Last Name or Hiring Manager],

**Introduction**
I am writing to express my interest in the [Exact Position Title] role at [Company Name], as advertised on [Job Board/Company Careers Page]. As a [Your Role, e.g., Master's student in Business Analytics], I bring a blend of technical expertise, business insight, and a passion for [specific company focus or industry]. I am drawn to [Company Name] because of its commitment to [Company Mission or Value].

**Professional Snapshot & Value Proposition**
[1-2 sentence summary of your value]

**Relevant Skills & Alignment with Role**
* **Skill 1 Name** – [Description of how you used this skill with examples from your resume].
* **Skill 2 Name** – [Description of how you used this skill with examples from your resume].
* **Skill 3 Name** – [Description of how you used this skill with examples from your resume].

**Selected Achievements**
* **Achievement 1** – [Quantifiable achievement from your resume].
* **Achievement 2** – [Quantifiable achievement from your resume].

**Closing & Call to Action**
I am excited about the opportunity to bring my analytical expertise and collaborative approach to [Company Name]. I am confident my blend of technical skills, business acumen, and drive to deliver measurable results align with your team’s goals. Thank you for considering my application, and I look forward to the opportunity to discuss how I can contribute to your success.

Sincerely,
[Your Full Name]
"""
    cover_letter_template = st.text_area("Your Cover Letter Template (Edit if needed)", value=default_template, height=300)

with col2:
    st.header("2. The Job You Want")
    job_description = st.text_area("Paste the Full Job Description Here", height=435)

if st.button("Generate My Cover Letter", type="primary", use_container_width=True):
    if uploaded_resume and job_description:
        with st.spinner("Reading your resume..."):
            try:
                # Read the uploaded PDF file
                pdf_reader = PyPDF2.PdfReader(uploaded_resume)
                resume_text = ""
                for page in pdf_reader.pages:
                    resume_text += page.extract_text()
            except Exception as e:
                st.error(f"Failed to read PDF: {e}")
                st.stop()
        
        with st.spinner("🧠 AI is drafting your cover letter... This may take a moment."):
            draft = draft_cover_letter_with_gemini(resume_text, job_description, cover_letter_template)
        
        st.header("✅ Your Draft Is Ready!")
        st.text_area("Review and copy your letter below", value=draft, height=500)
    else:
        st.warning("Please upload your resume and paste the job description first.")
