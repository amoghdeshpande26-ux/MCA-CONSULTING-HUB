import os
import random
import datetime
import pandas as pd
import streamlit as st
import pyrebase

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import openai
except ImportError:
    openai = None

st.set_page_config(
    page_title="Rotman MCA Consulting Hub 2026",
    page_icon="💼",
    layout="wide"
)

# --- FIREBASE CONFIGURATION ---
firebaseConfig = {
    "apiKey": "AIzaSyBIVbpt63AVrvh9z2sZcP7F6_Zs8LrFG6Y",
    "authDomain": "mca-consulting-web-app.firebaseapp.com",
    "databaseURL": "https://mca-consulting-web-app-default-rtdb.firebaseio.com",
    "projectId": "mca-consulting-web-app",
    "storageBucket": "mca-consulting-web-app.firebasestorage.app",
    "messagingSenderId": "424165199600",
    "appId": "1:424165199600:web:005cb9b48cf775a1373c35",
    "measurementId": "G-Q7D2P5EPZB"
}

# Initialize Firebase safely
try:
    firebase = pyrebase.initialize_app(firebaseConfig)
    auth = firebase.auth()
    db = firebase.database()
except Exception as e:
    auth = None
    db = None

# --- SESSION STATE INITIALIZATION ---
if "user" not in st.session_state:
    st.session_state.user = None
if "localId" not in st.session_state:
    st.session_state.localId = None
if "active_question" not in st.session_state:
    st.session_state.active_question = "Tell me about a time when you managed conflict within a high-pressure team."
if "job_applications" not in st.session_state:
    st.session_state.job_applications = []
if "case_catalog" not in st.session_state:
    if os.path.exists("case_catalog.csv"):
        st.session_state.case_catalog = pd.read_csv("case_catalog.csv")
    else:
        st.session_state.case_catalog = pd.DataFrame([
            {
                "Case_Title": "Gassy Convenience",
                "Source": "NYU Stern MCA / Bain Power Round",
                "Case_Type": "Opportunity Assessment / Digital",
                "Difficulty": "Advanced",
                "File_Name": "gassy_convenience.pdf",
                "Start_Page": 139,
                "End_Page": 142,
                "Prompt": "Our client is a large U.S. retail chain that owns convenience stores located in gas stations across California. With the rise of just-walk-out (JWO) stores, they are interested in piloting JWO technology in one of their existing gas station stores over 3 years. How should our client evaluate this opportunity?",
                "Exhibits": "Exhibit 1: Competitor landscape & gas station characteristics. Exhibit 2: 3-year discounted cash flow projections and Mekko chart breakdown."
            },
            {
                "Case_Title": "Canadian Mobile Banking",
                "Source": "Management Consulted",
                "Case_Type": "Market Entry / Digital",
                "Difficulty": "Intermediate",
                "File_Name": "Management_Consulted.pdf",
                "Start_Page": 246,
                "End_Page": 250,
                "Prompt": "Your client is the leading major bank in Canada, serving 2M customers nationwide. A tech provider proposes a white-label mobile app. Determine whether this is a good idea.",
                "Exhibits": "Exhibit 1: Projected app adoption curves, server infrastructure costs ($1.2M initial, $300k/yr maintenance), and customer churn sensitivity tables."
            },
            {
                "Case_Title": "Radiator Co. Acquisition",
                "Source": "Wharton Consulting Club",
                "Case_Type": "M&A / Growth Strategy",
                "Difficulty": "Advanced",
                "File_Name": "Wharton_2019.pdf",
                "Start_Page": 22,
                "End_Page": 28,
                "Prompt": "The European division of Radiator Co. wants to select a target startup to acquire in the smart-thermostat space and estimate deal value.",
                "Exhibits": "Exhibit 1: Target shortlist technical capability matrix and European market share percentages."
            },
            {
                "Case_Title": "European Beauty Company",
                "Source": "McKinsey Practice",
                "Case_Type": "Profitability & Digital",
                "Difficulty": "Intermediate",
                "File_Name": "McKinsey_Cases.pdf",
                "Start_Page": 5,
                "End_Page": 12,
                "Prompt": "The client employs in-store beauty advisors and is considering launching a smartphone-based digital beauty advisor. What is the payback period of this investment?",
                "Exhibits": "Exhibit 1: Revenue breakdown by channel (€120M total), advisor cost percentages, and app development cap-ex (€4.5M)."
            },
            {
                "Case_Title": "Swipe Right for Canoodle",
                "Source": "Duke Fuqua Consulting",
                "Case_Type": "New Product / Pricing",
                "Difficulty": "Foundational",
                "File_Name": "Duke_Fuqua.pdf",
                "Start_Page": 145,
                "End_Page": 150,
                "Prompt": "Client wants to introduce a premium subscription tier. Development costs are $500,000 over 6 months. Evaluate strategic fit and LTV.",
                "Exhibits": "Exhibit 1: Competitor pricing tiers and projected customer LTV models."
            },
            {
                "Case_Title": "Dark Sky",
                "Source": "Kellogg Consulting Club",
                "Case_Type": "Growth / Opportunity Assessment",
                "Difficulty": "Intermediate",
                "File_Name": "Kellogg_2023.pdf",
                "Start_Page": 157,
                "End_Page": 162,
                "Prompt": "Assess the opportunity for Dark Sky to maximize short-term growth in the defense aircraft sector.",
                "Exhibits": "Exhibit 1: Historical unit sales and growth (2006-2014). Exhibit 2: Aircraft revenue projections."
            }
        ])

# --- HELPER FUNCTIONS ---
def validate_email(email: str) -> bool:
    return email.endswith("@rotman.utoronto.ca") or email.endswith("@mail.utoronto.ca")

def validate_password(password: str) -> bool:
    has_cap = any(c.isupper() for c in password)
    has_low = any(c.islower() for c in password)
    has_num = any(c.isdigit() for c in password)
    has_spec = any(not c.isalnum() for c in password)
    return len(password) >= 8 and has_cap and has_low and has_num and has_spec

def render_pdf_slice(file_name: str, start_page: int, end_page: int):
    pdf_path = os.path.join("casebooks", file_name)
    if not os.path.exists(pdf_path):
        st.warning(f"📄 Waiting for PDF upload: '{file_name}' not found in the 'casebooks/' directory.")
        return
    if fitz is None:
        st.error("PyMuPDF is missing. Check requirements.txt.")
        return
    
    try:
        doc = fitz.open(pdf_path)
        total = len(doc)
        start_idx = max(0, start_page - 1)
        end_idx = min(total, end_page)
        
        for page_num in range(start_idx, end_idx):
            page = doc[page_num]
            pix = page.get_pixmap(dpi=150)
            img_bytes = pix.tobytes("png")
            st.image(img_bytes, caption=f"Page {page_num + 1} of {total}", use_container_width=True)
        doc.close()
    except Exception as e:
        st.error(f"Error reading PDF: {e}")

def update_job_tracker_in_db():
    if st.session_state.localId and db:
        try:
            db.child("users").child(st.session_state.localId).update({"job_applications": st.session_state.job_applications})
        except Exception:
            pass

# --- AUTHENTICATION & ONBOARDING ---
if not st.session_state.user:
    st.title("Rotman MCA Consulting Hub 2026 💼")
    st.markdown("Secure internal case preparation platform for Section 3 cohort recruitment.")
    
    auth_mode = st.radio("Access Portal", ["Log In", "Sign Up (New Student)"], horizontal=True)
    
    if auth_mode == "Log In":
        with st.form("login_form"):
            email_input = st.text_input("Rotman Email ID", placeholder="name@rotman.utoronto.ca")
            password_input = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Log In")
            
            if submit_login:
                if auth and db:
                    try:
                        user_auth = auth.sign_in_with_email_and_password(email_input, password_input)
                        local_id = user_auth['localId']
                        profile_data = db.child("users").child(local_id).get().val()
                        
                        if profile_data:
                            st.session_state.user = profile_data
                            st.session_state.localId = local_id
                            st.session_state.job_applications = profile_data.get("job_applications", [])
                            st.rerun()
                        else:
                            st.error("Profile not found in database. Please contact the administrator.")
                    except Exception as e:
                        st.error("Login failed. If credentials do not match, please reach out to the administrator and do not attempt unauthorized access.")
                else:
                    if validate_email(email_input):
                        st.session_state.user = {"email": email_input, "cluster": "Cluster-0Cases-MBB"}
                        st.rerun()
                    else:
                        st.error("Invalid Rotman email.")

    else:
        st.info("Registration requires your official @rotman.utoronto.ca or @mail.utoronto.ca email.")
        with st.form("signup_form"):
            email_signup = st.text_input("Rotman Email ID", placeholder="name@rotman.utoronto.ca")
            password_signup = st.text_input("Secure Password", type="password", help="Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special character")
            
            st.markdown("### Profile Setup & Recruiting Survey")
            exp = st.selectbox("1. Approximately how many live, full-length mock case interviews have you completed as the interviewee?", ["0 Cases", "1–5 Cases", "6–15 Cases", "16+ Cases"])
            track = st.selectbox("2. Which firm archetypes are your primary recruitment priority?", ["MBB (McKinsey, BCG, Bain)", "Big 4 Strategy (Deloitte S&O, EY-P)", "Tier 2 Strategy (Oliver Wyman, Kearney)", "Boutique Strategy", "Internal Corporate Strategy"])
            focus = st.selectbox("3. Which dimension of casing is currently your primary focus for active improvement?", ["Structuring & Issue Trees", "Quantitative Analysis & Math", "Chart & Data Interpretation", "Brainstorming & Business Intuition", "Synthesis & Recommendation"])
            freq = st.selectbox("4. What is your weekly live-practice bandwidth commitment?", ["1 Case/Week", "2 Cases/Week", "3+ Cases/Week"])
            time_slot = st.selectbox("5. Select your preferred weekly practice time blocks:", ["Weekday Mornings", "Weekday Evenings", "Weekend Slots"])
            readiness = st.selectbox("6. Administration comfort level:", ["Comfortable Giving & Receiving Cases", "Prefer Receiving Only (Beginner)"])
            
            submit_signup = st.form_submit_button("Complete Profile & Enter Hub")
            
            if submit_signup:
                if not validate_email(email_signup):
                    st.error("Please use a valid Rotman email ID.")
                elif not validate_password(password_signup):
                    st.error("Password must contain at least 8 characters, 1 uppercase, 1 lowercase, 1 number, and 1 special character.")
                else:
                    try:
                        local_id = "local_user_" + str(random.randint(10000, 99999))
                        if auth and db:
                            new_user = auth.create_user_with_email_and_password(email_signup, password_signup)
                            local_id = new_user['localId']
                        
                        cluster_id = f"Cluster-{exp.replace(' ', '')}-{track.split()[0]}"
                        new_profile = {
                            "email": email_signup,
                            "survey": {
                                "experienceBaseline": exp,
                                "targetTrack": track,
                                "coreFocus": focus,
                                "practiceFrequency": freq,
                                "timeBlocks": time_slot,
                                "giverReadiness": readiness
                            },
                            "cluster": cluster_id,
                            "created_at": str(datetime.datetime.now()),
                            "job_applications": []
                        }
                        
                        if db:
                            db.child("users").child(local_id).set(new_profile)
                        
                        st.session_state.user = new_profile
                        st.session_state.localId = local_id
                        st.session_state.job_applications = []
                        st.success("Profile successfully created! Entering Portal...")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Registration failed: {e}")
    st.stop()

# --- MAIN DASHBOARD INTERFACE ---
st.sidebar.title("MCA Hub 2026 🎓")
st.sidebar.write(f"**User:** {st.session_state.user['email']}")
st.sidebar.caption(f"**Cohort:** {st.session_state.user['cluster']}")

if st.sidebar.button("Log Out"):
    st.session_state.user = None
    st.session_state.localId = None
    st.session_state.job_applications = []
    st.rerun()

main_tab = st.sidebar.radio(
    "Navigation Hubs",
    ["Hub 1: Interview Prep", "Hub 2: Behavioral & Fit", "Hub 3: Master Case Bank", "Job Search Tracker", "Admin Control Center"]
)

# --- HUB 1: INTERVIEW PREP GUIDE ---
if main_tab == "Hub 1: Interview Prep":
    st.title("Hub 1: Comprehensive Interview Preparation Guide 📘")
    st.write("Review the complete preparation study document covering consulting workstreams, standard case flow mechanics, and official Rotman 2026 scoring rubrics.")
    
    if st.button("Load Full Study Document"):
        render_pdf_slice("CIA_4.pdf", 1, 100)
        
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("1. Standard Case Flow")
        st.markdown("""
        * **Intro & Fit (5–10 min):** Career narrative & resume walkthrough.
        * **Structuring (5 min):** Clarifying questions & MECE issue tree.
        * **Deep Dive / Math (15 min):** Vocalized calculations & exhibit analysis.
        * **Synthesis (5 min):** Recommendation-first closing with risks.
        """)
    with col2:
        st.subheader("2. Everyday Consultant Tasks")
        st.markdown("""
        * **Information Gathering:** Primary interviews and client data requests.
        * **Problem Structuring:** Deconstructing complex challenges into testable workstreams.
        * **Quantitative Modeling:** Financial, operational, and valuation scenario analysis.
        * **Client Communication:** Executive slide decks and stakeholder alignment.
        """)
    with col3:
        st.subheader("3. Rotman 2026 Rubric")
        st.markdown("""
        * **Clarification & Goal (5 pts):** Metric targets and objective validation.
        * **Framework & Structure (10 pts):** Tailored MECE issue trees.
        * **Analytical Rigor (10 pts):** Vocalized, error-free mental math.
        * **Business Intuition (10 pts):** Pragmatic trade-offs and creative ideas.
        * **Synthesis (5 pts):** Clear recommendation-first closing.
        """)

# --- HUB 2: BEHAVIORAL & FIT HUB ---
elif main_tab == "Hub 2: Behavioral & Fit":
    st.title("Hub 2: Behavioral & Fit Hub 🎯")
    st.write("Master personal experience interviews using the P.A.R.T. (Problem, Action, Result, Takeaway) framework and test your responses against our live AI evaluator.")
    
    st.subheader("Question Bank")
    q_options = [
        "Tell me about a time when you managed conflict within a high-pressure team.",
        "Describe a situation where a project failed and your recovery strategy.",
        "Give an example of driving results under extremely tight deadlines.",
        "Tell me about a time you convinced a skeptical stakeholder to adopt your recommendation.",
        "Describe how you handled ambiguous instructions while leading a cross-functional workstream.",
        "Tell me about a time you used data to change someone's mind.",
        "Describe a time when you had to adapt to a major change in a project's scope.",
        "Structure your career narrative and transition logic (Why Consulting / Why Firm?)."
    ]
    
    for q in q_options:
        c1, c2 = st.columns([4, 1])
        c1.write(f"• *\"{q}\"*")
        if c2.button("Select Question", key=f"btn_{q}"):
            st.session_state.active_question = q
            st.rerun()

    st.markdown("---")
    st.subheader("AI Behavioral Answer Evaluator")
    
    st.info(f"**Active Question:** {st.session_state.active_question}")
    
    api_key_input = st.text_input("OpenAI API Key (Connect your ChatGPT account for live feedback):", type="password")
    user_response = st.text_area("Draft your response (P.A.R.T. Framework: Problem, Action, Result, Takeaway):", height=200)
    
    if st.button("Evaluate Response via AI"):
        if api_key_input and openai:
            try:
                client = openai.OpenAI(api_key=api_key_input)
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a senior MBB consultant interviewer evaluating a behavioral interview answer. Score out of 5 and provide concise strengths and areas for refinement using the P.A.R.T. framework."},
                        {"role": "user", "content": f"Question: {st.session_state.active_question}\nResponse: {user_response}"}
                    ]
                )
                st.success("AI Feedback Generated!")
                st.write(completion.choices[0].message.content)
            except Exception as e:
                st.error(f"OpenAI API Error: {e}")
        else:
            st.warning("Please enter your OpenAI API key above to generate live feedback.")

# --- HUB 3: MASTER CASE BANK ---
elif main_tab == "Hub 3: Master Case Bank":
    st.title("Hub 3: Master Case Bank Repository 📁")
    st.write("Browse multiple cases-source casebooks.")
    
    catalog_df = st.session_state.case_catalog
    
    col_f1, col_f2 = st.columns(2)
    diff_filter = col_f1.selectbox("Filter by Difficulty:", ["All"] + list(catalog_df["Difficulty"].unique()))
    type_filter = col_f2.selectbox("Filter by Case Type:", ["All"] + list(catalog_df["Case_Type"].unique()))
    
    filtered_df = catalog_df.copy()
    if diff_filter != "All":
        filtered_df = filtered_df[filtered_df["Difficulty"] == diff_filter]
    if type_filter != "All":
        filtered_df = filtered_df[filtered_df["Case_Type"] == type_filter]
        
    for _, row in filtered_df.iterrows():
        with st.expander(f"📌 {row['Case_Title']} | {row['Source']} ({row['Difficulty']})"):
            st.write(f"**Type:** {row['Case_Type']}")
            st.write(f"**Prompt:** {row['Prompt']}")
            st.write(f"**Exhibits & Data Details:** {row.get('Exhibits', 'See PDF for full exhibits.')}")
            
            if st.button("Open Full Case Pages & Exhibits", key=f"view_{row['Case_Title']}"):
                if "File_Name" in row and pd.notna(row["File_Name"]):
                    st.markdown(f"### Viewing Complete Case from {row['File_Name']}")
                    render_pdf_slice(row["File_Name"], int(row["Start_Page"]), int(row["End_Page"]))
                else:
                    st.error("File mapping missing for this case.")

# --- JOB SEARCH TRACKER ---
elif main_tab == "Job Search Tracker":
    st.title("Job Search & Networking Tracker 📈")
    st.write("Manage your recruitment pipeline and network tracking records securely tied to your profile.")
    
    with st.form("job_form"):
        col1, col2, col3, col4 = st.columns(4)
        firm = col1.text_input("Firm Name", placeholder="e.g. McKinsey")
        role = col2.text_input("Role", placeholder="e.g. Summer Associate")
        status = col3.selectbox("Status", ["Networking", "Applied", "Interviewing", "Offer"])
        deadline = col4.date_input("Deadline", datetime.date.today())
        
        submit_job = st.form_submit_button("Add Record")
        if submit_job and firm:
            new_id = 1
            if len(st.session_state.job_applications) > 0:
                new_id = max(j["id"] for j in st.session_state.job_applications) + 1
                
            new_entry = {
                "id": new_id,
                "Firm": firm,
                "Role": role,
                "Status": status,
                "Deadline": str(deadline)
            }
            st.session_state.job_applications.append(new_entry)
            update_job_tracker_in_db()
            st.success(f"Added {firm} record!")

    if st.session_state.job_applications:
        df_jobs = pd.DataFrame(st.session_state.job_applications)
        st.dataframe(df_jobs, use_container_width=True)
        
        del_id = st.number_input("Enter ID of record to delete:", min_value=1, step=1)
        if st.button("Delete Record"):
            st.session_state.job_applications = [j for j in st.session_state.job_applications if j["id"] != del_id]
            update_job_tracker_in_db()
            st.rerun()
    else:
        st.info("No applications logged yet.")

# --- ADMIN CONTROL CENTER ---
elif main_tab == "Admin Control Center":
    st.title("Admin Control Center 🔒")
    st.write("Restricted administrator oversight. Enter the secure password to manage cohorts and execute Sunday peer matching.")
    
    admin_pwd = st.text_input("Enter Administrator Password:", type="password")
    
    if admin_pwd == "RotmanAdmin2026!":
        st.success("Admin Access Granted!")
        
        st.subheader("Automated Pairing Engine")
        st.write("Match cohort members within clusters based on overlapping availability.")
        
        if st.button("Execute Matching"):
            try:
                users = db.child("users").get().val() if db else None
                if users:
                    profiles = list(users.values())
                    if len(profiles) < 2:
                        st.warning("At least 2 profiles are required to generate peer pairings.")
                    else:
                        random.shuffle(profiles)
                        pairs = []
                        for i in range(0, len(profiles) - 1, 2):
                            pairs.append((profiles[i]["email"], profiles[i+1]["email"]))
                        st.markdown("### Generated Pairings for Next Week:")
                        for idx, p in enumerate(pairs, 1):
                            st.write(f"**Pair {idx}:** {p[0]} ↔️ {p[1]}")
                else:
                    st.info("No registered users found in the database.")
            except Exception as e:
                st.error(f"Error fetching database: {e}")
                    
        st.markdown("---")
        st.subheader("Registered Student Roster")
        try:
            users = db.child("users").get().val() if db else None
            if users:
                roster_data = []
                for p in users.values():
                    if "email" in p and "survey" in p:
                        roster_data.append({
                            "Email": p["email"],
                            "Cluster": p["cluster"],
                            "Target Track": p["survey"]["targetTrack"],
                            "Experience": p["survey"]["experienceBaseline"],
                            "Practice Freq": p["survey"]["practiceFrequency"]
                        })
                if roster_data:
                    st.dataframe(pd.DataFrame(roster_data), use_container_width=True)
            else:
                st.info("No student profiles registered yet.")
        except Exception as e:
            st.error(f"Error reading database: {e}")
            
    elif admin_pwd:
        st.error("Incorrect administrator password.")
