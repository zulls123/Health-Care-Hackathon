# app.py - FINAL FIXED VERSION (Submit Button + No Numeric Errors)
import streamlit as st
import os
import uuid
import requests
import json
import time
from datetime import datetime, date
from dotenv import load_dotenv
from database import SQLiteDBManager

load_dotenv()

# ==================== CONFIG ====================
ARK_API_BASE_URL = "http://localhost:3274/api/v1"
ARK_TEAM_NAME = "greencare-team"

DB_DIR = os.path.join(os.path.expanduser("~"), "AppData", "Local", "GreenCare")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "greencare.db")
db = SQLiteDBManager(DB_PATH)

# ==================== ARK TEAM CALLER ====================
def call_greencare_team(prompt: str, session_id: str) -> str:
    query_id = f"chat-{uuid.uuid4()}"
    payload = {
        "name": query_id,
        "namespace": "default",
        "type": "messages",
        "input": [{"role": "user", "content": prompt}],
        "sessionId": session_id or f"session-{int(time.time()*1000)}",
        "targets": [{"name": ARK_TEAM_NAME, "type": "team"}],
        "timeout": "5m0s",
        "ttl": "720h0m0s"
    }

    try:
        resp = requests.post(f"{ARK_API_BASE_URL}/queries/", json=payload, timeout=90)
        if resp.status_code != 200 and resp.status_code != 201:
            return f"Ark error {resp.status_code}"

        for i in range(60):
            time.sleep(1.3 if i < 10 else 2.0)
            poll = requests.get(f"{ARK_API_BASE_URL}/queries/{query_id}", timeout=30)
            if poll.status_code != 200:
                continue
            data = poll.json().get("status", {})
            if data.get("phase") == "done":
                raw = data.get("responses", [{}])[0].get("raw") or data.get("responses", [{}])[0].get("content", "")
                try:
                    for msg in json.loads(raw):
                        if msg.get("role") == "assistant":
                            return msg.get("content", "").strip()
                except:
                    return str(raw).strip()
        return "The team is thinking..."
    except Exception as e:
        return f"Connection issue: {str(e)}"

# ==================== PROFILE EDITOR - FIXED ====================
def show_profile_editor():
    st.subheader("My Health & Financial Profile")
    user_id = st.session_state.user["user_id"]
    profile = db.get_user_profile(user_id) or {}

    medical_aid = profile.get("medical_aid") or {}
    medical_history = profile.get("medical_history") or []
    medications = profile.get("medications") or []
    financial = (profile.get("financial_accounts") or [{}])[0]

    with st.form("profile_form", clear_on_submit=False):
        st.markdown("#### Medical Aid")
        scheme = st.text_input("Medical Aid Scheme", value=medical_aid.get("scheme_name", "") or "")
        member_number = st.text_input("Member Number", value=medical_aid.get("membership_number", "") or "")

        st.markdown("#### Active Medical Conditions")
        conditions_input = st.text_area(
            "List your active conditions (one per line)",
            value="\n".join([c["condition"] for c in medical_history if c.get("status") == "Active"]),
            height=120
        )

        st.markdown("#### Current Medicines")
        meds_input = st.text_area(
            "List your regular medicines (one per line)",
            value="\n".join([m["name"] for m in medications]),
            height=120
        )

        st.markdown("#### Financial Details")
        # FIXED: Use float 0.0 instead of int 0
        income = st.number_input("Monthly Income (R)", min_value=0.0, value=float(financial.get("monthly_income") or 0.0))
        expenses = st.number_input("Monthly Expenses (R)", min_value=0.0, value=float(financial.get("monthly_budget") or 0.0))

        # SUBMIT BUTTON NOW INSIDE THE FORM
        submitted = st.form_submit_button("Save Profile", use_container_width=True, type="primary")

        if submitted:
            db.update_medical_aid(user_id, scheme.strip() or None, member_number.strip() or None)

            conditions = [c.strip() for c in conditions_input.split("\n") if c.strip()]
            db.update_medical_history(user_id, conditions)

            medicines = [m.strip() for m in meds_input.split("\n") if m.strip()]
            db.update_medications(user_id, medicines)

            db.update_financial_account(user_id, float(income), float(expenses))

            st.success("Profile saved successfully!")
            st.balloons()
            st.rerun()

# ==================== LOGIN / REGISTER (unchanged) ====================
def show_login_page():
    st.markdown("""
    <div style="text-align:center;padding:4rem 0;">
        <h1 style="font-size:3.5rem;font-weight:800;">GreenCare AI</h1>
        <p style="font-size:1.8rem;color:#6ee7b7;">Your Private Health & Financial Companion</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        with st.form("login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login", use_container_width=True):
                user = db.authenticate_user(username, password)
                if user:
                    st.session_state.user = user
                    st.session_state.authenticated = True
                    st.session_state.db_session_id = f"session-{uuid.uuid4()}"
                    db.create_session(user["user_id"], st.session_state.db_session_id)
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    with tab2:
        with st.form("register"):
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name*")
                last_name = st.text_input("Last Name*")
                email = st.text_input("Email*")
            with col2:
                username = st.text_input("Username*")
                password = st.text_input("Password*", type="password")
                confirm = st.text_input("Confirm Password*", type="password")
            phone = st.text_input("Phone")
            dob = st.date_input("Date of Birth", value=None)
            province = st.selectbox("Province", ["", "Gauteng", "Western Cape", "KwaZulu-Natal", "Eastern Cape",
                                                "Free State", "Limpopo", "Mpumalanga", "North West", "Northern Cape"])
            city = st.text_input("City/Town")

            if st.form_submit_button("Create Account", use_container_width=True):
                if password != confirm:
                    st.error("Passwords do not match")
                elif len(password) < 8:
                    st.error("Password too short")
                elif not all([first_name, last_name, username, email]):
                    st.error("Fill required fields")
                else:
                    user_id = db.create_user(
                        username=username, email=email, password=password,
                        first_name=first_name, last_name=last_name,
                        phone=phone or None,
                        date_of_birth=dob.isoformat() if dob else None,
                        gender=None, province=province if province else None,
                        city=city if city else None
                    )
                    if user_id:
                        st.success("Account created! Login now.")
                        st.balloons()
                    else:
                        st.error("Username/email taken")

# ==================== MAIN APP ====================
st.set_page_config(page_title="GreenCare AI", page_icon="Leaf", layout="centered")

st.markdown("""
<style>
    .stApp {background:#050608;color:#f1f5f9;}
    [data-testid="stSidebar"] {background:linear-gradient(180deg,#065f46,#022c22);color:#ecfdf5;}
    [data-testid="stSidebar"] * {color:#ecfdf5 !important;}
    .stButton>button {background:#22c55e;color:#022c22;border:none;border-radius:999px;font-weight:600;}
    .legal-notice {background:#1e293b;border-left:5px solid #f59e0b;padding:1.2rem;border-radius:8px;margin:2rem 0;}
    footer,#MainMenu {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "show_profile" not in st.session_state:
    st.session_state.show_profile = False

if not st.session_state.authenticated:
    show_login_page()
else:
    user = st.session_state.user

    with st.sidebar:
        st.markdown(f"### {user['first_name']} {user['last_name']}")
        st.caption(user['email'])
        if user.get('city'):
            st.caption(f"{user.get('city')}, {user.get('province', '')}")

        chat_tab, profile_tab = st.tabs(["Chat", "Profile"])

        with chat_tab:
            if st.button("New Chat", use_container_width=True):
                st.session_state.conversation = []
                st.rerun()

        with profile_tab:
            if st.button("Edit My Profile", use_container_width=True):
                st.session_state.show_profile = True
                st.rerun()

        if st.button("Logout", use_container_width=True):
            if "db_session_id" in st.session_state:
                db.end_session(st.session_state.db_session_id)
            st.session_state.clear()
            st.rerun()

        st.markdown("---")
        st.caption("GreenCare Team Active")

    if st.session_state.show_profile:
        show_profile_editor()
        if st.button("Back to Chat"):
            st.session_state.show_profile = False
            st.rerun()
    else:
        st.markdown("<h1 style='text-align:center;padding:2rem 0;'>GreenCare AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#6ee7b7;font-size:1.5rem;'>Your trusted companion</p>", unsafe_allow_html=True)

        st.markdown("""
        <div class="legal-notice">
            <strong>Legal:</strong> Not a doctor or financial advisor. Always consult professionals.
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.conversation:
            history = db.get_chat_history(user['user_id'], "GreenCare Team", limit=50)
            st.session_state.conversation = [{"role": h["role"], "content": h["content"]} for h in history]

        for msg in st.session_state.conversation:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("How can the GreenCare Team help you today?"):
            st.session_state.conversation.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            profile = db.get_user_profile(user['user_id']) or {}
            med = profile.get("medical_aid") or {}
            hist = profile.get("medical_history") or []
            meds = profile.get("medications") or []
            acc = (profile.get("financial_accounts") or [{}])[0]

            dob = user.get("date_of_birth")
            age = None
            if dob and isinstance(dob, date):
                today = date.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

            context = f"""USER PROFILE
Name: {user['first_name']} {user['last_name']}
Age: {age or 'Not given'}
Location: {user.get('city','')} {user.get('province','')}, South Africa
Medical Aid: {med.get('scheme_name', 'None')}
Conditions: {', '.join([c.get('condition','') for c in hist if c.get('status')=='Active']) or 'None'}
Medicines: {', '.join([m.get('name','') for m in meds]) or 'None'}
Income: R{acc.get('monthly_income', 'Not set')}
"""

            full_prompt = f"{context}\n\nUSER: {prompt}\n\nAnswer kindly in British English."

            db.save_chat_message(user['user_id'], "GreenCare Team", "user", prompt, st.session_state.db_session_id)

            with st.spinner("Thinking..."):
                reply = call_greencare_team(full_prompt, st.session_state.db_session_id)

            st.session_state.conversation.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.markdown(reply)

            db.save_chat_message(user['user_id'], "GreenCare Team", "assistant", reply, st.session_state.db_session_id)