# app.py - GreenCare AI - FULLY FIXED & WORKING (Local SQLite + Local ARK)
import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
from database import AzureDBManager  # This is SQLite under the hood
from orchestrator import create_orchestrator
import uuid
from datetime import datetime  # ← THIS WAS MISSING!

load_dotenv()

# ==================== CONFIGURATION ====================
USE_LOCAL_ARK = os.getenv('USE_LOCAL_ARK', 'True').lower() == 'true'

ARK_API_KEY = os.getenv('ARK_API_KEY', '')
ARK_API_BASE_URL = os.getenv('ARK_API_BASE_URL',
    "http://localhost:3274/api/v1" if USE_LOCAL_ARK else
    "https://openai.prod.ai-gateway.quantumblack.com/YOUR_GATEWAY_ID/v1")

ARK_AGENT_IDS = {
    "health": "health-companion-agent",
    "financial": "financial-coach-agent",
    "legal": "legal-compliance-agent",
    "critic": "language-critic-agent",
    "orchestrator": "orchestrator-agent"
}

# ==================== SAFE SQLITE PATH (Works on OneDrive!) ====================
if os.path.expanduser("~").endswith("OneDrive"):
    DB_DIR = os.path.join(os.path.expanduser("~"), "AppData", "Local", "GreenCare")
    os.makedirs(DB_DIR, exist_ok=True)
    DB_PATH = os.path.join(DB_DIR, "greencare.db")
else:
    DB_PATH = os.getenv('SQLITE_DB_PATH', "greencare.db")

# Initialize DB & Orchestrator
db = AzureDBManager(DB_PATH)
orchestrator = create_orchestrator(
    db_manager=db,
    ark_base_url=ARK_API_BASE_URL,
    ark_api_key=ARK_API_KEY,
    agent_ids=ARK_AGENT_IDS
)

# ==================== AUTH PAGE ====================
def show_login_page():
    st.markdown("""
    <div style="text-align:center;padding:3rem 0;">
        <div style="font-size:3rem;font-weight:800;">GreenCare AI</div>
        <div style="font-size:1.5rem;color:#6ee7b7;margin:1rem 0;">Your Personal Health & Financial Companion</div>
        <p style="color:#9ca3af;">Private • Local • South African Law Compliant</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Register"])

    # ============== LOGIN ==============
    with tab1:
        with st.form("login_form"):
            st.subheader("Welcome Back")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login", use_container_width=True)  # ← FIXED!

            if login_btn:
                if username and password:
                    user_data = db.authenticate_user(username, password)
                    if user_data:
                        st.session_state.user = user_data
                        st.session_state.authenticated = True
                        session_id = f"session-{uuid.uuid4()}"
                        db.create_session(user_data["user_id"], session_id)
                        st.session_state.db_session_id = session_id
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.warning("Please fill in both fields")

    # ============== REGISTER ==============
    with tab2:
        with st.form("register_form"):
            st.subheader("Create Your Account")
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name*")
                email = st.text_input("Email*")
                phone = st.text_input("Phone (optional)", placeholder="+27821234567")
                gender = st.selectbox("Gender", ["", "Male", "Female", "Other", "Prefer not to say"])
            with col2:
                last_name = st.text_input("Last Name*")
                username = st.text_input("Username*")
                dob = st.date_input("Date of Birth", value=None, min_value=datetime(1900, 1, 1))
                province = st.selectbox("Province", [
                    "", "Gauteng", "Western Cape", "KwaZulu-Natal", "Eastern Cape",
                    "Free State", "Limpopo", "Mpumalanga", "North West", "Northern Cape"
                ])
            city = st.text_input("City/Town")
            password = st.text_input("Password*", type="password")
            confirm = st.text_input("Confirm Password*", type="password")

            register_btn = st.form_submit_button("Create Account", use_container_width=True)  # ← FIXED!

            if register_btn:
                if password != confirm:
                    st.error("Passwords do not match")
                elif len(password) < 8:
                    st.error("Password must be at least 8 characters")
                elif not all([first_name, last_name, username, email]):
                    st.error("Please fill all required fields")
                else:
                    user_id = db.create_user(
                        username=username, email=email, password=password,
                        first_name=first_name, last_name=last_name,
                        phone=phone or None,
                        date_of_birth=dob.isoformat() if dob else None,
                        gender=gender if gender else None,
                        province=province if province else None,
                        city=city if city else None
                    )
                    if user_id:
                        st.success("Account created! Please log in.")
                        st.balloons()
                    else:
                        st.error("Username or email already exists")

# ==================== MAIN APP ====================
st.set_page_config(page_title="GreenCare AI", layout="wide", page_icon="GreenCare")

# Styling
st.markdown("""
<style>
.stApp {background:#050608;color:#F9FAFB;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#065f46,#022c22);color:#ECFDF5;}
[data-testid="stSidebar"] * {color:#ECFDF5 !important;}
.sidebar-button .stButton>button {width:100%;border-radius:999px;background:#22c55e;color:#022c22;border:none;font-weight:600;}
.legal-notice {background:#1e293b;border-left:4px solid #f59e0b;padding:1rem;border-radius:0.5rem;margin:1.5rem 0;}
footer,#MainMenu {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# Session init
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "conversation" not in st.session_state:
    st.session_state.conversation = []

if not st.session_state.authenticated:
    show_login_page()
else:
    user = st.session_state.user

    # Sidebar
    with st.sidebar:
        st.markdown(f"### {user['first_name']} {user['last_name']}")
        st.caption(user['email'])
        if user.get('city'): st.caption(f"{user['city']}, {user.get('province', '')}")

        if st.button("Logout", use_container_width=True):
            if "db_session_id" in st.session_state:
                db.end_session(st.session_state.db_session_id)
            st.session_state.clear()
            st.rerun()

        st.markdown("---")
        if st.button("New Chat", use_container_width=True):
            st.session_state.conversation = []
            st.rerun()

        st.markdown("---")
        st.caption("Multi-Agent System")
        st.caption("• Health Guidance")
        st.caption("• Financial Coach")
        st.caption("• Legal Compliance")
        st.caption("• Language Critic")

    # Header
    st.markdown("""
    <div style="text-align:center;padding:1rem 0;">
        <div style="font-size:2.8rem;font-weight:800;">GreenCare AI</div>
        <div style="font-size:1.4rem;color:#6ee7b7;">Your Private Health & Financial Companion</div>
    </div>
    """, unsafe_allow_html=True)

    # Legal Notice
    st.markdown("""
    <div class="legal-notice">
        <strong>Legal Notice:</strong> This system is <strong>not</strong> a registered medical practitioner or financial services provider. 
        All guidance is informational only. Always consult qualified professionals.
    </div>
    """, unsafe_allow_html=True)

    # Load chat history
    if not st.session_state.conversation:
        history = db.get_chat_history(user['user_id'], agent_type="Orchestrator", limit=30)
        st.session_state.conversation = [{"role": h["role"], "content": h["content"]} for h in history]

    for msg in st.session_state.conversation:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Ask about your health, budget, or wellness..."):
        st.session_state.conversation.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        db.save_chat_message(
            user_id=user['user_id'],
            agent_type="Orchestrator",
            role="user",
            content=prompt,
            session_id=st.session_state.get("db_session_id", "")
        )

        with st.spinner("All agents are thinking..."):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(orchestrator.process_user_request(
                    user_id=user['user_id'],
                    user_prompt=prompt,
                    session_id=st.session_state.get("db_session_id", "")
                ))
            finally:
                loop.close()

            reply = result.get("content", "Sorry, I couldn't process that.")
            if result["status"] == "blocked":
                reply = result["message"]
                st.warning(reply)
            elif result["status"] == "error":
                st.error(reply)

            st.session_state.conversation.append({"role": "assistant", "content": reply})
            st.chat_message("assistant").write(reply)