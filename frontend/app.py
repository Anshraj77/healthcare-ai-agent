import os
import sys
import uuid
import streamlit as st

# =========================================================
# PROJECT PATH
# =========================================================

ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


# =========================================================
# STREAMLIT SECRETS → ENVIRONMENT VARIABLES
# =========================================================

def load_secrets():

    secret_names = [
        "OPENAI_API_KEY",
        "OPENAI_MODEL",
        "SALESFORCE_ENABLED",
        "SALESFORCE_USERNAME",
        "SALESFORCE_PASSWORD",
        "SALESFORCE_SECURITY_TOKEN",
        "SALESFORCE_DOMAIN",
    ]

    for name in secret_names:
        try:
            if name in st.secrets:
                os.environ[name] = str(st.secrets[name])
        except Exception:
            pass


load_secrets()


# =========================================================
# IMPORT AGENT
# =========================================================

from backend.agent import HealthcareAgent


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="CareConnect AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# LOAD AGENT ONCE
# =========================================================

@st.cache_resource
def get_agent():
    return HealthcareAgent()


try:
    agent = get_agent()
    agent_online = True
    agent_error = None

except Exception as error:
    agent = None
    agent_online = False
    agent_error = str(error)


# =========================================================
# SESSION
# =========================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "quick_message" not in st.session_state:
    st.session_state.quick_message = None


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

html, body {
    background-color: #f4f7fb !important;
}

[data-testid="stAppViewContainer"] {
    background-color: #f4f7fb !important;
}

[data-testid="stMain"] {
    background-color: #f4f7fb !important;
}

.block-container {
    max-width: 1350px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}


/* HERO */

.hero {
    background: linear-gradient(
        135deg,
        #176b68,
        #2bb5aa
    );

    padding: 38px 42px;
    border-radius: 24px;
    margin-bottom: 30px;

    box-shadow:
        0px 12px 35px
        rgba(22, 107, 104, 0.25);
}

.hero h1 {
    color: white !important;
    font-size: 46px;
    font-weight: 700;
    margin: 0;
}

.hero p {
    color: #e6fffb !important;
    font-size: 19px;
    margin-top: 14px;
}

.status-online {
    display: inline-block;
    margin-top: 18px;
    background-color: #d9f7eb;
    color: #176b45 !important;
    padding: 9px 18px;
    border-radius: 30px;
    font-size: 14px;
    font-weight: 600;
}


/* CARDS */

.feature-card {
    background-color: white !important;
    border: 1px solid #dce3eb;
    border-radius: 20px;
    padding: 28px 24px;
    min-height: 180px;

    box-shadow:
        0px 8px 22px
        rgba(0, 0, 0, 0.06);
}

.feature-card h3 {
    color: #245b63 !important;
    font-size: 27px;
    font-weight: 700;
}

.feature-card p {
    color: #596579 !important;
    font-size: 16px;
    line-height: 1.6;
}


/* BUTTONS */

.stButton > button {
    width: 100% !important;
    background-color: #176b68 !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 11px 15px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}

.stButton > button:hover {
    background-color: #115754 !important;
}


/* CHAT */

[data-testid="stChatMessage"] {
    background-color: white !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 16px !important;
    padding: 16px !important;
    margin-bottom: 14px !important;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div {
    color: #1f2937 !important;
}


/* CHAT INPUT */

[data-testid="stChatInput"] {
    background-color: white !important;
    border: 2px solid #cbd5e1 !important;
    border-radius: 16px !important;
    padding: 5px !important;
}

[data-testid="stChatInput"] textarea {
    background-color: white !important;
    color: #111827 !important;
    caret-color: #111827 !important;
    opacity: 1 !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #64748b !important;
    opacity: 1 !important;
}


/* SIDEBAR */

[data-testid="stSidebar"] {
    background-color: #0f172a !important;
}

[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

.sidebar-card {
    background-color: #1e293b !important;
    padding: 18px;
    border-radius: 15px;
    margin-top: 15px;
    margin-bottom: 20px;
    border: 1px solid #334155;
}


/* FOOTER */

.footer {
    text-align: center;
    color: #64748b !important;
    margin-top: 50px;
    font-size: 14px;
    padding-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("🏥 CareConnect")
    st.caption("AI Healthcare Platform")

    st.divider()

    if agent_online:
        st.success("🟢 AI Agent Online")
    else:
        st.error("🔴 AI Agent Error")

        if agent_error:
            with st.expander("View error"):
                st.code(agent_error)

    st.markdown("""
    <div class="sidebar-card">

    <h3>🤖 AI Capabilities</h3>

    <p>✓ Clinic Knowledge Assistant</p>
    <p>✓ Appointment Requests</p>
    <p>✓ Patient Type Detection</p>
    <p>✓ Salesforce Lead Integration</p>

    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ⚡ Quick Actions")

    if st.button("📅 Request Appointment"):
        st.session_state.quick_message = (
            "I want to book an appointment"
        )
        st.rerun()

    if st.button("🏥 Clinic Services"):
        st.session_state.quick_message = (
            "What services does the clinic provide?"
        )
        st.rerun()

    if st.button("🕒 Clinic Timings"):
        st.session_state.quick_message = (
            "What are the clinic timings?"
        )
        st.rerun()

    st.divider()

    if st.button("🗑️ Clear Conversation"):

        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.quick_message = None

        st.rerun()

    st.divider()

    st.caption(
        "CareConnect AI provides clinic information "
        "and appointment assistance."
    )


# =========================================================
# HERO
# =========================================================

status_text = (
    "🟢 AI Assistant Ready"
    if agent_online
    else "🔴 AI Agent Initialization Failed"
)

st.markdown(
    f"""
    <div class="hero">

        <h1>🏥 CareConnect AI</h1>

        <p>
        Your intelligent healthcare assistant for clinic
        information and appointment support.
        </p>

        <div class="status-online">
        {status_text}
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# FEATURE CARDS
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown("""
    <div class="feature-card">

    <h3>💬 Ask Questions</h3>

    <p>
    Get instant answers about clinic services,
    locations, timings and more.
    </p>

    </div>
    """, unsafe_allow_html=True)

    if st.button("💬 Ask a Question", key="ask"):

        st.session_state.quick_message = (
            "What services does the clinic provide?"
        )

        st.rerun()


with col2:

    st.markdown("""
    <div class="feature-card">

    <h3>📅 Book Appointments</h3>

    <p>
    Request an appointment directly through
    our AI assistant.
    </p>

    </div>
    """, unsafe_allow_html=True)

    if st.button("📅 Book Now", key="book"):

        st.session_state.quick_message = (
            "I want to book an appointment"
        )

        st.rerun()


with col3:

    st.markdown("""
    <div class="feature-card">

    <h3>🧠 Smart Patient Support</h3>

    <p>
    Our AI understands whether you're a new
    or existing patient.
    </p>

    </div>
    """, unsafe_allow_html=True)

    if st.button("🧠 Patient Support", key="support"):

        st.session_state.quick_message = (
            "I need help as a patient. "
            "How do you support new and existing patients?"
        )

        st.rerun()


# =========================================================
# CHAT
# =========================================================

st.markdown(
    '<h2 style="color:#1f2937;">💬 Chat with CareConnect AI</h2>',
    unsafe_allow_html=True
)


if len(st.session_state.messages) == 0:

    st.info("""
    👋 **Hello! I'm CareConnect AI.**

    I can help you with:

    - 🏥 Clinic services and locations
    - 🕒 Opening hours
    - 📅 Appointment requests
    - 🧠 New and existing patient support

    How can I help you today?
    """)


# =========================================================
# DISPLAY HISTORY
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.write(message["content"])


# =========================================================
# INPUT
# =========================================================

user_input = None

if st.session_state.quick_message:

    user_input = st.session_state.quick_message
    st.session_state.quick_message = None

chat_input = st.chat_input(
    "Ask about our clinic or request an appointment..."
)

if chat_input:
    user_input = chat_input


# =========================================================
# PROCESS
# =========================================================

if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):

        if not agent_online:

            st.error(
                "The AI agent could not start. "
                "Please check the Streamlit Secrets and deployment logs."
            )

        else:

            with st.spinner(
                "CareConnect AI is thinking..."
            ):

                try:

                    data = agent.chat(
                        session_id=st.session_state.session_id,
                        message=user_input
                    )

                    answer = data.get(
                        "response",
                        "Sorry, I couldn't generate a response."
                    )

                    st.write(answer)

                    # ---------------------------------------------
                    # AGENT DETAILS
                    # ---------------------------------------------

                    with st.expander(
                        "🧠 Agent Decision Details"
                    ):

                        metric1, metric2 = st.columns(2)

                        with metric1:

                            st.metric(
                                "Intent",
                                data.get(
                                    "intent",
                                    "Unknown"
                                )
                            )

                        with metric2:

                            patient_type = data.get(
                                "patient_type"
                            )

                            st.metric(
                                "Patient Type",
                                patient_type
                                if patient_type
                                else "Not Detected"
                            )

                        appointment_data = data.get(
                            "appointment_data"
                        )

                        if appointment_data:

                            st.markdown(
                                "### 📋 Appointment Information"
                            )

                            st.json(
                                appointment_data
                            )

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                except Exception as error:

                    st.error(
                        f"❌ Agent Error: {error}"
                    )


# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div class="footer">

<b>CareConnect AI</b> • Intelligent Healthcare Assistant

<br><br>

Powered by RAG • AI Agents • Salesforce

</div>
""", unsafe_allow_html=True)