import streamlit as st
import requests
import json
import time
import uuid

AGENTS = ["Health Companion", "Financial Agent", "Orchestrator"]

# ========= ARK CONFIGURATION =========
ARK_API_KEY = ""  # Add your API key here
ARK_API_BASE_URL = "http://localhost:3274/api/v1"  # Your local Ark API endpoint

# Map UI agent names to Ark agent IDs
ARK_AGENT_IDS = {
    "Health Companion": "health-companion-agent",
    "Financial Agent": "financial-coach-agent",
    "Orchestrator": "orchestrator-agent",
}

def call_ark_agent(agent_type: str, message: str, conversation_history: list = None):
    """
    Call an Ark agent via the correct API format.
    
    Args:
        agent_type: The type of agent (from AGENTS list)
        message: The user's message
        conversation_history: Previous messages in the conversation
    
    Returns:
        The agent's response text, or None if there's an error
    """
    if not ARK_API_KEY or ARK_API_KEY == "":
        # If no API key, skip authentication (for local dev)
        headers = {"Content-Type": "application/json"}
    else:
        headers = {
            "Authorization": f"Bearer {ARK_API_KEY}",
            "Content-Type": "application/json",
        }
    
    agent_id = ARK_AGENT_IDS.get(agent_type)
    if not agent_id:
        return None
    
    try:
        # Generate a unique query ID
        query_id = f"chat-query-{str(uuid.uuid4())}"
        
        # Generate or use existing session ID
        if "session_id" not in st.session_state:
            st.session_state.session_id = f"session-{int(time.time() * 1000)}"
        
        # Prepare the input messages in Ark format
        input_messages = []
        
        # Add conversation history if available
        if conversation_history:
            input_messages.extend(conversation_history)
        
        # Add the current message
        input_messages.append({"role": "user", "content": message})
        
        # Create the Ark query payload
        payload = {
            "name": query_id,
            "namespace": "default",
            "type": "messages",
            "input": input_messages,
            "sessionId": st.session_state.session_id,
            "targets": [
                {
                    "name": agent_id,
                    "type": "agent"
                }
            ],
            "timeout": "5m0s"
        }
        
        # Create the query
        response = requests.post(
            f"{ARK_API_BASE_URL}/queries",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code in [200, 201]:
            # Poll for the result
            max_attempts = 30
            for attempt in range(max_attempts):
                time.sleep(1)  # Wait 1 second between polls
                
                result_response = requests.get(
                    f"{ARK_API_BASE_URL}/queries/{query_id}",
                    headers=headers,
                    timeout=10
                )
                
                if result_response.status_code == 200:
                    data = result_response.json()
                    
                    # Check if the query is complete
                    if data.get("status", {}).get("phase") == "done":
                        # Extract the response content
                        responses = data.get("status", {}).get("responses", [])
                        if responses and len(responses) > 0:
                            return responses[0].get("content", "")
                        else:
                            st.error("No response content from agent")
                            return None
                    elif data.get("status", {}).get("phase") == "failed":
                        st.error(f"Query failed: {data.get('status', {}).get('message', 'Unknown error')}")
                        return None
            
            st.error("Query timed out waiting for response")
            return None
        else:
            st.error(f"Ark API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error calling Ark agent: {str(e)}")
        return None

# ========= END ARK CONFIGURATION =========


# --- PAGE CONFIG ---
st.set_page_config(
    page_title="GreenCare",
    layout="wide",
    page_icon="💚"
)

# --- GLOBAL CUSTOM CSS ---
custom_css = """
<style>
/* Overall app background */
.stApp {
    background-color: #050608;
    color: #F9FAFB;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #065f46, #022c22);
    color: #ECFDF5;
    border-right: 1px solid #064e3b;
    min-width: 320px !important;
    max-width: 320px !important;
}
[data-testid="stSidebar"] * {
    color: #ECFDF5 !important;
}

/* New Chat button styling */
.sidebar-button .stButton > button {
    width: 100%;
    border-radius: 999px;
    background-color: #22c55e;
    color: #022c22;
    border: 1px solid #bbf7d0;
    font-weight: 600;
    padding: 0.6rem 1rem;
}
.sidebar-button .stButton > button:hover {
    background-color: #16a34a;
}

/* Agent select label */
.sidebar-select label {
    font-weight: 600;
}

/* Main header area */
.main-header {
    padding-top: 0.75rem;
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -0.03em;
}
.hero-sub {
    font-size: 1.4rem;
    font-weight: 600;
    color: #6ee7b7;
    margin-bottom: 1.2rem;
}

/* Cards row */
.card-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.8rem;
    margin-top: 0.5rem;
}
.feature-card {
    background: #0b1120;
    border-radius: 1.25rem;
    padding: 1.2rem 1.35rem;
    box-shadow: 0 18px 40px rgba(0,0,0,0.55);
    flex: 1;
    border: 1px solid #1f2937;
}
.card-title {
    font-weight: 700;
    margin-bottom: 0.2rem;
}
.card-sub {
    font-weight: 600;
    font-size: 0.9rem;
    color: #a7f3d0;
    margin-bottom: 0.5rem;
}
.card-body {
    font-size: 0.86rem;
    line-height: 1.4;
    color: #d1d5db;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background-color: #020617;
    border-radius: 1rem;
    padding: 0.75rem 1rem;
    margin-bottom: 0.75rem;
    border: 1px solid #111827;
}
[data-testid="stChatMessage"] p {
    font-size: 0.95rem;
}

/* Chat input area */
[data-testid="stChatInput"] {
    background-color: #050608;
    border-top: 1px solid #111827;
}
[data-testid="stChatInput"] textarea {
    border-radius: 999px !important;
    background-color: #020617 !important;
    color: #F9FAFB !important;
    border: 1px solid #1f2937 !important;
    padding: 0.8rem 1rem !important;
}
[data-testid="stChatInput"] label {
    color: #9ca3af !important;
}

/* Hide Streamlit branding footer */
footer, #MainMenu {
    visibility: hidden;
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# --- SESSION STATE SETUP ---
if "conversations" not in st.session_state:
    st.session_state.conversations = {agent: [] for agent in AGENTS}

if "current_agent" not in st.session_state:
    st.session_state.current_agent = AGENTS[0]

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 💚 AI Health Companion")

    # New chat button
    st.markdown('<div class="sidebar-button">', unsafe_allow_html=True)
    if st.button("✨ New chat"):
        st.session_state.conversations[st.session_state.current_agent] = []
        # Reset session ID for new chat
        if "session_id" in st.session_state:
            del st.session_state.session_id
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Agent selector
    st.markdown('<div class="sidebar-select">', unsafe_allow_html=True)
    agent_choice = st.selectbox(
        "Select an Agent:",
        AGENTS,
        index=AGENTS.index(st.session_state.current_agent)
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Update current agent
    st.session_state.current_agent = agent_choice

    st.markdown("---")
    st.caption("Tip: switch agents to change how the assistant responds.")

    # Recent chats summary
    st.markdown("#### Recent chats")
    for agent in AGENTS:
        conv = st.session_state.conversations.get(agent, [])
        user_msgs = [m["content"] for m in conv if m["role"] == "user"]
        if not user_msgs:
            continue
        st.markdown(f"**{agent}**")
        for text in user_msgs[-3:]:
            st.caption(f"• {text[:50]}...")

# --- MAIN CONTENT HEADER ---
st.markdown(
    """
    <div class="main-header">
        <div class="hero-title">AI health chat</div>
        <div class="hero-sub">for patients, professionals, and their finances.</div>
        <div class="card-row">
            <div class="feature-card">
                <div class="card-title">Health Companion</div>
                <div class="card-sub">Daily wellbeing support.</div>
                <div class="card-body">
                    Check in on symptoms, mood, habits, and routines. 
                    Get gentle, personalised nudges to stay on top of your health.
                </div>
            </div>
            <div class="feature-card">
                <div class="card-title">Financial Agent</div>
                <div class="card-sub">Money and medical costs.</div>
                <div class="card-body">
                    Talk through treatment expenses, budgeting, and saving goals 
                    while keeping your health journey sustainable.
                </div>
            </div>
            <div class="feature-card">
                <div class="card-title">Orchestrator</div>
                <div class="card-sub">One brain for many agents.</div>
                <div class="card-body">
                    Coordinates different specialised agents so you get one
                    coherent conversation instead of scattered advice.
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

current_agent = st.session_state.current_agent

# --- CHAT TITLE ---
st.subheader(f"💬 Chat with your **{current_agent}**")

# --- CHAT DISPLAY ---
messages = st.session_state.conversations[current_agent]

for msg in messages:
    st.chat_message(msg["role"]).write(msg["content"])

# --- REPLY GENERATION ---
def generate_reply(message: str, agent_type: str, history: list) -> str:
    """Generate a reply using Ark agents with fallback."""
    
    # Try Ark agent first
    ark_reply = call_ark_agent(agent_type, message, history)
    if ark_reply:
        return ark_reply
    
    # Fallback to local responses if Ark is unavailable
    if agent_type == "Health Companion":
        return "💚 I'm here to support your wellbeing. How are you feeling today?"
    elif agent_type == "Financial Agent":
        return "💸 Let's talk money. What's on your mind financially?"
    elif agent_type == "Orchestrator":
        return "🧠 I coordinate your agents. Describe what you need and I'll route it."
    return "How can I assist you?"

# --- CHAT INPUT ---
if user_input := st.chat_input("Type a message or start with how you're feeling today..."):
    # Add user message
    st.session_state.conversations[current_agent].append(
        {"role": "user", "content": user_input}
    )
    st.chat_message("user").write(user_input)

    # Generate assistant reply with conversation history
    with st.spinner("Thinking..."):
        reply = generate_reply(
            user_input, 
            current_agent, 
            st.session_state.conversations[current_agent][:-1]
        )
    
    st.session_state.conversations[current_agent].append(
        {"role": "assistant", "content": reply}
    )
    st.chat_message("assistant").write(reply)