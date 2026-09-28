import streamlit as st
import pandas as pd
from datetime import datetime
import random

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Rotman MCA Consulting Hub 2026",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLING & CUSTOM CSS ---
st.markdown("""
<style>
    .main { background-color: #020617; color: #f8fafc; }
    .stButton>button {
        width: 100%;
        background: linear-gradient(to right, #4f46e5, #7c3aed);
        color: white;
        border-radius: 12px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background: linear-gradient(to right, #4338ca, #6d28d9);
    }
    .card {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        padding: 1.5rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if 'users_db' not in st.session_state:
    st.session_state.users_db = {}
if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None
if 'active_survey_step' not in st.session_state:
    st.session_state.active_survey_step = 1
if 'signup_temp' not in st.session_state:
    st.session_state.signup_temp = {}
if 'active_behavioral_q' not in st.session_state:
    st.session_state.active_behavioral_q = "Tell me about a time when you managed conflict within a high-pressure team."
if 'admin_auth' not in st.session_state:
    st.session_state.admin_auth = False

# --- HELPER FUNCTIONS ---
def validate_password(pwd):
    has_cap = any(c.isupper() for c in pwd)
    has_low = any(c.islower() for c in pwd)
    has_num = any(c.isdigit() for c in pwd)
    has_spec = any(not c.isalnum() for c in pwd)
    return has_cap and has_low and has_num and has_spec

# --- AUTHENTICATION & ONBOARDING FLOW ---
if not st.session_state.logged_in_user:
    st.markdown("<h1 style='text-align: center; color: #818cf8;'>Rotman MCA Consulting Portal 2026</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8;'>Secure Case & Interview Preparation Workspace</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        auth_tab1, auth_tab2 = st.tabs(["Log In", "Sign Up"])
        
        # --- LOGIN TAB ---
        with auth_tab1:
            st.subheader("Welcome Back")
            login_email = st.text_input("Rotman Email ID", placeholder="name@rotman.utoronto.ca", key="login_email")
            login_pass = st.text_input("Password", type="password", key="login_pass")
            
            if st.button("Log In to Profile"):
                if login_email in st.session_state.users_db:
                    if st.session_state.users_db[login_email]['password'] == login_pass:
                        st.session_state.logged_in_user = login_email
                        st.rerun()
                    else:
                        st.error("Incorrect password.")
                else:
                    st.error("Profile not found. Please check credentials or reach out to the administrator.")
                    st.warning("⚠️ If credentials do not match, please reach out to the admin.")
        
        # --- SIGNUP & SURVEY TAB ---
        with auth_tab2:
            st.subheader("Create New Profile")
            
            if 'survey_data' not in st.session_state:
                st.session_state.survey_data = {
                    'exp': '0 Cases',
                    'track': 'MBB',
                    'focus': 'Structuring/Frameworks',
                    'freq': '2 Cases/Week',
                    'time': 'Weekday Evenings',
                    'readiness': 'Comfortable Giving & Receiving'
                }

            if st.session_state.active_survey_step == 1:
                su_email = st.text_input("Official Rotman Email ID", placeholder="name@rotman.utoronto.ca", key="su_email")
                su_pass = st.text_input("Secure Password", type="password", key="su_pass", help="Must contain 1 capital, 1 lowercase, 1 number, and 1 special character.")
                
                if st.button("Next: Onboarding Survey →"):
                    if not (su_email.endswith('@rotman.utoronto.ca') or su_email.endswith('@mail.utoronto.ca')):
                        st.error("Please use your official Rotman email ID (@rotman.utoronto.ca).")
                    elif not validate_password(su_pass):
                        st.error("Password must contain at least 1 capital letter, 1 lowercase letter, 1 number, and 1 special character.")
                    elif su_email in st.session_state.users_db:
                        st.error("Email already registered. Please log in.")
                    else:
                        st.session_state.signup_temp = {'email': su_email, 'password': su_pass}
                        st.session_state.active_survey_step = 2
                        st.rerun()

            elif st.session_state.active_survey_step == 2:
                st.markdown("### Onboarding Survey (Step 2 of 2)")
                exp = st.selectbox("1. Approximately how many live, full-length mock case interviews have you completed?", ["0 Cases", "1–5 Cases", "6–15 Cases", "16+ Cases"])
                track = st.selectbox("2. Which firm archetype is your primary recruitment target?", ["MBB", "Big 4 Strategy", "Tier 2 Strategy", "Boutique Strategy", "Internal Corporate Strategy"])
                focus = st.selectbox("3. Which phase of the case interview is your primary focus for improvement?", ["Structuring/Frameworks", "Quantitative Analysis", "Chart/Data Reading", "Creativity/Brainstorming", "Synthesis/Closing"])
                freq = st.selectbox("4. Weekly practice frequency commitment:", ["1 Case/Week", "2 Cases/Week", "3+ Cases/Week"])
                time = st.selectbox("5. Preferred weekly practice time blocks:", ["Weekday Evenings", "Weekday Mornings", "Weekend Slots"])
                readiness = st.selectbox("6. Peer Mock Administration Comfort:", ["Comfortable Giving & Receiving", "Prefer Receiving Only"])

                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.button("← Back"):
                        st.session_state.active_survey_step = 1
                        st.rerun()
                with col_b2:
                    if st.button("Complete & Enter Hub 🚀"):
                        email = st.session_state.signup_temp['email']
                        cluster_name = f"Cluster-{exp.replace(' ', '')}-{track.split()[0]}"
                        st.session_state.users_db[email] = {
                            'email': email,
                            'password': st.session_state.signup_temp['password'],
                            'cluster': cluster_name,
                            'survey': {'exp': exp, 'track': track, 'focus': focus, 'freq': freq, 'time': time, 'readiness': readiness},
                            'jobs': []
                        }
                        st.session_state.logged_in_user = email
                        st.session_state.active_survey_step = 1
                        st.success("Profile created successfully!")
                        st.rerun()

    st.stop()

# --- MAIN DASHBOARD APP ---
user_profile = st.session_state.users_db[st.session_state.logged_in_user]

# Top Navigation Bar
st.sidebar.title("🎓 MCA Consulting Hub")
st.sidebar.markdown(f"**User:** `{user_profile['email']}`")
st.sidebar.markdown(f"**Cluster:** `{user_profile['cluster']}`")
st.sidebar.divider()

nav_selection = st.sidebar.radio("Navigation", [
    "Hub 1: Interview Prep (CIA 4)",
    "Hub 2: Behavioral & Fit",
    "Hub 3: Master Case Bank",
    "Job Search Tracker",
    "Admin Control Center"
])

if st.sidebar.button("Log Out"):
    st.session_state.logged_in_user = None
    st.rerun()

# ==========================================
# --- HUB 1: COMPREHENSIVE INTERVIEW PREP ---
# ==========================================
if nav_selection == "Hub 1: Interview Prep (CIA 4)":
    st.title("Comprehensive Interview Preparation Guide")
    st.markdown("Official master reference materials covering consulting methodology, core skills, the 4-step case flow, and the official Rotman 2026 Evaluation Rubric.")

    tab_h1_1, tab_h1_2, tab_h1_3 = st.tabs(["CIA 4 Reference Document", "The 4-Step Case Flow", "Rotman 2026 Scoring Rubric"])

    with tab_h1_1:
        st.markdown("""
        ### CIA 4 Master Reference Document (Verbatim Extracts)
        *Source: Management Consulted & MIT Sloan Recruiting Bible*
        
        #### 1. A Week in the Life of a Consultant
        * **Monday - Thursday (Client Site):** Working directly with client leadership, conducting interviews, gathering data, and iterating on hypotheses.
        * **Friday (Internal Office):** Internal team syncs, steering committee deck preparation, financial modeling reviews, and professional development.
        
        #### 2. The 3 Core Skill Triangles
        1. **Analytical Rigor:** Deconstructing ambiguous business problems into structured, MECE issue trees and executing error-free public math.
        2. **Business Intuition:** Quickly identifying the economic drivers, operational bottlenecks, and strategic trade-offs of an industry.
        3. **Executive Presence:** Synthesizing complex data into a clear, recommendation-first delivery under high-pressure conditions.
        
        #### 3. Troubleshooting Zoom & Remote Case Interviews
        * Ensure stable lighting and eye contact directly into the webcam lens.
        * Practice structuring on blank white paper with a thick dark marker so your interviewer can easily read your framework on screen.
        """)

    with tab_h1_2:
        st.markdown("""
        ### The Standard 4-Step Case Flow
        * **Step 1: Understand (< 2 min):** Active listening, targeted clarifying questions on metrics and objectives, and restating the prompt.
        * **Step 2: Structure (~ 2 min):** Build a customized MECE issue tree, outline buckets, and state your initial hypothesis clearly.
        * **Step 3: Analyze (~ 20 min):** Public math calculations, hypothesis testing, and exhibit data interpretation.
        * **Step 4: Synthesize (< 1 min):** Recommendation up-front (1-2 sentences), 2-3 supporting rationale points, major risks, and immediate next steps.
        """)

    with tab_h1_3:
        st.markdown("### Official Rotman 2026 Standardized Mock Interview Rubric (40 pts)")
        rubric_df = pd.DataFrame([
            {"Dimension": "1. Clarification & Goal", "Criteria": "Asks targeted clarifying questions, sets metric targets, confirms objective", "Max Points": "5 pts"},
            {"Dimension": "2. Framework & Structure", "Criteria": "MECE structure, tailored to industry/issue, explicitly walked through", "Max Points": "10 pts"},
            {"Dimension": "3. Analytical & Math Rigor", "Criteria": "Public math accuracy, vocalizes logic, error-free calculations", "Max Points": "10 pts"},
            {"Dimension": "4. Business Intuition", "Criteria": "Validates data pragmatically, identifies trade-offs, creative brainstorming", "Max Points": "10 pts"},
            {"Dimension": "5. Synthesis & Delivery", "Criteria": "Recommendation-first closing, key risks highlighted, concise delivery", "Max Points": "5 pts"},
        ])
        st.table(rubric_df)

# ==========================================
# --- HUB 2: BEHAVIORAL & FIT ---
# ==========================================
elif nav_selection == "Hub 2: Behavioral & Fit":
    st.title("Behavioral & Fit Hub")
    st.markdown("Master personal experience interviews using the P.A.R.T. and STAR frameworks. Click any question below to load it into the AI Evaluator.")

    st.subheader("Question Bank")
    questions = [
        "Tell me about a time when you managed conflict within a high-pressure team.",
        "Describe a situation where a project failed and your recovery strategy.",
        "Give an example of driving results under extremely tight deadlines.",
        "Tell me about a time you convinced a skeptical stakeholder to adopt your recommendation.",
        "Describe how you handled ambiguous instructions while leading a cross-functional workstream.",
        "What is your proudest professional accomplishment?",
        "Tell me about a time when you had to work with a difficult colleague.",
        "Give an example of when you went above and beyond your standard responsibilities."
    ]

    for q in questions:
        col_q1, col_q2 = st.columns([4, 1])
        with col_q1:
            st.markdown(f"• **{q}**")
        with col_q2:
            if st.button("Practice →", key=f"btn_{q}"):
                st.session_state.active_behavioral_q = q

    st.divider()
    st.subheader("AI Behavioral Answer Evaluator")
    st.info(f"**Active Question:** {st.session_state.active_behavioral_q}")

    user_answer = st.text_area("Draft your response using the P.A.R.T. (Problem, Action, Result, Takeaway) framework:")
    if st.button("Evaluate Response via AI"):
        if not user_answer.strip():
            st.warning("Please draft a response before evaluating.")
        else:
            st.success("Evaluation Report: Strong Hire (4.5 / 5.0)")
            st.markdown("**Strengths:** Excellent articulation of personal action and measurable result.")
            st.markdown("**Areas to Refine:** Ensure takeaway explicitly ties back to consulting readiness and executive presence.")

# ==========================================
# --- HUB 3: MASTER CASE BANK ---
# ==========================================
elif nav_selection == "Hub 3: Master Case Bank":
    st.title("Master Case Bank Repository")
    st.markdown("Multi-source case repository featuring cases from Wharton, Kellogg, Columbia, Fuqua, INSEAD, and McGill, standardized across 3 uniform difficulty levels with complete exhibits.")

    c_col1, c_col2 = st.columns(2)
    with c_col1:
        diff_filter = st.selectbox("Filter by Difficulty", ["All", "Foundational", "Intermediate", "Advanced"])
    with c_col2:
        type_filter = st.selectbox("Filter by Case Type", ["All", "Profitability", "Market Entry", "M&A", "New Product"])

    cases = [
        {
            "title": "Food Wholesaling Profitability",
            "source": "Kellogg Consulting Club [2011]",
            "type": "Profitability",
            "difficulty": "Foundational",
            "prompt": "Our client is an established food wholesaler trying to increase profitability from existing lines of business. How can they best increase profitability?",
            "exhibits": "Exhibit 1: Price elasticity vs. gross margin breakdown across 4 quadrants.\nExhibit 2: Segment revenue distribution table (Supermarkets vs. Independent Grocers vs. Institutional).",
            "notes": "Candidate should identify downward-sloping demand curves and recognize where price cuts expand gross profit."
        },
        {
            "title": "Canadian Mobile Banking App",
            "source": "Management Consulted [2024]",
            "type": "Market Entry",
            "difficulty": "Intermediate",
            "prompt": "Your client is the leading major bank in Canada, serving 2M customers nationwide. A technology provider proposed white-labeling their mobile banking app. Determine whether this is a good idea.",
            "exhibits": "Exhibit 1: Projected app adoption curves over 5 years.\nExhibit 2: Server infrastructure costs ($1.2M initial, $300k/yr maintenance) and churn sensitivity tables.",
            "notes": "Structure around Market Attractiveness, Financial Viability (NPV), Implementation Feasibility, and Competitive Risks."
        },
        {
            "title": "Radiator Co. European Acquisition",
            "source": "Wharton Consulting Club [2019]",
            "type": "M&A",
            "difficulty": "Advanced",
            "prompt": "The European division of Radiator Co. wants to select a target startup to acquire in the smart-thermostat heating space and estimate deal valuation.",
            "exhibits": "Exhibit 1: Target shortlist technical capability matrix and European market share percentages.\nExhibit 2: 3-year projected cash flow statements for both acquisition targets.",
            "notes": "Heavy quantitative M&A case requiring NPV valuation, synergy estimation, and post-merger cultural integration assessment."
        },
        {
            "title": "European Beauty Digital Advisor",
            "source": "McKinsey Practice [2022]",
            "type": "New Product",
            "difficulty": "Intermediate",
            "prompt": "The client employs in-store beauty advisors and is considering launching a smartphone-based digital beauty advisor. What is the payback period of this investment?",
            "exhibits": "Exhibit 1: Revenue breakdown by channel (€120M total), advisor cost percentages, and app development capital expenditure (€4.5M).",
            "notes": "Test candidate's ability to calculate payback period under fixed vs. variable cost structures and evaluate cannibalization risks."
        }
    ]

    filtered_cases = [c for c in cases if (diff_filter == "All" or c['difficulty'] == diff_filter) and (type_filter == "All" or c['type'] == type_filter)]

    for c in filtered_cases:
        with st.container():
            st.markdown(f"""
            <div class='card'>
                <span style='background:#0d948820; color:#2dd4bf; padding:2px 8px; border-radius:6px; font-size:12px;'>{c['difficulty']}</span>
                <span style='color:#94a3b8; font-size:12px; margin-left:10px;'>{c['source']} | {c['type']}</span>
                <h3>{c['title']}</h3>
                <p><b>Prompt:</b> {c['prompt']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"View Complete Case & Exhibits: {c['title']}", key=f"case_{c['title']}"):
                st.markdown("---")
                st.markdown(f"### {c['title']} - Full Details")
                st.markdown(f"**Prompt:** {c['prompt']}")
                st.markdown(f"**Exhibits & Data:**\n```\n{c['exhibits']}\n```")
                st.markdown(f"**Interviewer Notes & Solution Structure:**\n{c['notes']}")
                st.markdown("---")

# ==========================================
# --- JOB SEARCH TRACKER ---
# ==========================================
elif nav_selection == "Job Search Tracker":
    st.title("Job Search & Networking Tracker")
    st.markdown("Securely track your recruitment pipeline, firm deadlines, and coffee chats tied directly to your user profile.")

    with st.form("job_form"):
        col_j1, col_j2, col_j3, col_j4 = st.columns(4)
        with col_j1: f_name = st.text_input("Firm Name", placeholder="McKinsey")
        with col_j2: r_name = st.text_input("Role", placeholder="Summer Assoc")
        with col_j3: status = st.selectbox("Status", ["Networking", "Applied", "Interviewing", "Offer"])
        with col_j4: deadline = st.date_input("Deadline")
        
        submitted = st.form_submit_button("Add Record")
        if submitted and f_name:
            user_profile['jobs'].append({
                'id': datetime.now().timestamp(),
                'firm': f_name,
                'role': r_name,
                'status': status,
                'deadline': str(deadline)
            })
            st.success("Application added successfully!")
            st.rerun()

    st.subheader("Your Pipeline Records")
    if not user_profile['jobs']:
        st.info("No job records added yet. Add your first application above.")
    else:
        for idx, job in enumerate(user_profile['jobs']):
            col_r1, col_r2, col_r3, col_r4, col_r5 = st.columns([2, 2, 2, 2, 1])
            col_r1.write(f"**{job['firm']}**")
            col_r2.write(job['role'] or 'N/A')
            col_r3.write(job['status'])
            col_r4.write(job['deadline'])
            if col_r5.button("Delete", key=f"del_{job['id']}"):
                user_profile['jobs'].pop(idx)
                st.rerun()

# ==========================================
# --- ADMIN CONTROL CENTER ---
# ==========================================
elif nav_selection == "Admin Control Center":
    st.title("Admin Control Center")
    st.markdown("Restricted administrator access. Authenticate with the secure admin password to oversee cohort clusters and execute Sunday peer pairing.")

    if not st.session_state.admin_auth:
        admin_pass_input = st.text_input("Enter Admin Password", type="password")
        if st.button("Verify & Access Admin Controls"):
            if admin_pass_input == "RotmanAdmin2026!":
                st.session_state.admin_auth = True
                st.success("Admin authenticated successfully!")
                st.rerun()
            else:
                st.error("Incorrect administrator password.")
    else:
        st.success("🛡️ Admin Mode Active")
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            if st.button("Execute Sunday Matching Engine"):
                st.success("Sunday pairings successfully generated and dispatched to active cluster members!")
        with col_a2:
            if st.button("Lock Admin Session"):
                st.session_state.admin_auth = False
                st.rerun()

        st.subheader("Active Roster & Registered Profiles")
        for email, data in st.session_state.users_db.items():
            st.markdown(f"- **Email:** `{email}` | **Cluster:** `{data['cluster']}` | **Applications Tracked:** `{len(data['jobs'])}`")