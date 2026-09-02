import streamlit as st
import requests
import uuid


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
# CONFIG
# =========================================================

BACKEND_URL = "http://127.0.0.1:8000"


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

/* =====================================================
   GLOBAL APP
===================================================== */

html,
body,
[data-testid="stAppViewContainer"] {
    background-color: #f4f7fb !important;
    color: #1f2937 !important;
}

.stApp {
    background-color: #f4f7fb !important;
    color: #1f2937 !important;
}

[data-testid="stMain"] {
    background-color: #f4f7fb !important;
}

.block-container {
    max-width: 1350px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}


/* =====================================================
   HERO SECTION
===================================================== */

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
    color: #ffffff !important;
    font-size: 46px;
    font-weight: 700;
    margin: 0;
}

.hero p {
    color: #e6fffb !important;
    font-size: 19px;
    margin-top: 14px;
}


/* =====================================================
   STATUS BADGE
===================================================== */

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


/* =====================================================
   FEATURE CARDS
===================================================== */

.feature-card {
    background-color: #ffffff !important;

    border: 1px solid #dce3eb;

    border-radius: 20px;

    padding: 28px 24px;

    min-height: 180px;

    box-shadow:
        0px 8px 22px
        rgba(0, 0, 0, 0.06);

    margin-bottom: 12px;
}

.feature-card h3 {
    color: #245b63 !important;

    font-size: 27px;

    font-weight: 700;

    margin-bottom: 18px;
}

.feature-card p {
    color: #596579 !important;

    font-size: 16px;

    line-height: 1.6;
}


/* =====================================================
   BUTTONS
===================================================== */

.stButton > button {
    width: 100% !important;

    background-color: #176b68 !important;

    color: #ffffff !important;

    border: none !important;

    border-radius: 12px !important;

    padding: 11px 15px !important;

    font-size: 15px !important;

    font-weight: 600 !important;

    transition: 0.2s;
}

.stButton > button:hover {
    background-color: #115754 !important;

    color: #ffffff !important;

    transform: translateY(-1px);
}


/* =====================================================
   CHAT HEADER
===================================================== */

.chat-header {
    color: #1f2937 !important;

    font-size: 27px;

    font-weight: 700;

    margin-top: 35px;

    margin-bottom: 18px;
}


/* =====================================================
   CHAT MESSAGES
===================================================== */

[data-testid="stChatMessage"] {
    background-color: #ffffff !important;

    border: 1px solid #e2e8f0 !important;

    border-radius: 16px !important;

    padding: 16px !important;

    margin-bottom: 14px !important;

    box-shadow:
        0px 3px 10px
        rgba(0, 0, 0, 0.04);
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div {
    color: #1f2937 !important;
}


/* =====================================================
   CHAT INPUT - IMPORTANT VISIBILITY FIX
===================================================== */

[data-testid="stChatInput"] {
    background-color: #ffffff !important;

    border: 2px solid #cbd5e1 !important;

    border-radius: 16px !important;

    padding: 5px !important;

    box-shadow:
        0px 4px 15px
        rgba(0, 0, 0, 0.08);
}

[data-testid="stChatInput"] textarea {
    background-color: #ffffff !important;

    color: #111827 !important;

    caret-color: #111827 !important;

    opacity: 1 !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #64748b !important;

    opacity: 1 !important;
}


/* Chat input internal containers */

[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] div {
    background-color: transparent !important;
}


/* Send button */

[data-testid="stChatInput"] button {
    background-color: #176b68 !important;

    color: #ffffff !important;

    border-radius: 10px !important;
}

[data-testid="stChatInput"] button svg {
    fill: #ffffff !important;

    color: #ffffff !important;
}


/* =====================================================
   ALERTS / INFO
===================================================== */

[data-testid="stAlert"] {
    background-color: #eff6ff !important;

    color: #1e3a5f !important;

    border-radius: 12px !important;
}

[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
[data-testid="stAlert"] div {
    color: #1e3a5f !important;
}


/* =====================================================
   EXPANDER
===================================================== */

[data-testid="stExpander"] {
    background-color: #ffffff !important;

    border: 1px solid #dce3eb !important;

    border-radius: 12px !important;
}

[data-testid="stExpander"] p,
[data-testid="stExpander"] span {
    color: #1f2937 !important;
}


/* =====================================================
   METRICS
===================================================== */

[data-testid="stMetricLabel"] {
    color: #64748b !important;
}

[data-testid="stMetricValue"] {
    color: #176b68 !important;
}


/* =====================================================
   JSON DISPLAY
===================================================== */

[data-testid="stJson"] {
    background-color: #f8fafc !important;

    color: #111827 !important;

    border-radius: 10px !important;

    border: 1px solid #d1d5db !important;
}


/* =====================================================
   SIDEBAR
===================================================== */

[data-testid="stSidebar"] {
    background-color: #0f172a !important;
}

[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

[data-testid="stSidebar"] .stButton button {
    background-color: #176b68 !important;

    color: #ffffff !important;
}


/* =====================================================
   SIDEBAR CARD
===================================================== */

.sidebar-card {
    background-color: #1e293b !important;

    padding: 18px;

    border-radius: 15px;

    margin-top: 15px;

    margin-bottom: 20px;

    border: 1px solid #334155;
}

.sidebar-card h3 {
    color: #ffffff !important;
}

.sidebar-card p {
    color: #cbd5e1 !important;
}


/* =====================================================
   FOOTER
===================================================== */

.footer {
    text-align: center;

    color: #64748b !important;

    margin-top: 50px;

    font-size: 14px;

    padding-bottom: 20px;
}


/* =====================================================
   HIDE DEFAULT STREAMLIT ELEMENTS
===================================================== */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION INITIALIZATION
# =========================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())


if "messages" not in st.session_state:
    st.session_state.messages = []


if "quick_message" not in st.session_state:
    st.session_state.quick_message = None


# =========================================================
# BACKEND STATUS
# =========================================================

def check_backend():
    try:
        response = requests.get(
            f"{BACKEND_URL}/health",
            timeout=3
        )

        return response.status_code == 200

    except Exception:
        return False


backend_online = check_backend()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("🏥 CareConnect")

    st.caption("AI Healthcare Platform")

    st.divider()


    # Backend Status

    if backend_online:
        st.success("🟢 AI Agent Online")
    else:
        st.error("🔴 Backend Offline")


    # Capabilities

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


    if st.button(
        "📅 Request Appointment",
        key="sidebar_appointment"
    ):
        st.session_state.quick_message = (
            "I want to book an appointment"
        )
        st.rerun()


    if st.button(
        "🏥 Clinic Services",
        key="sidebar_services"
    ):
        st.session_state.quick_message = (
            "What services does the clinic provide?"
        )
        st.rerun()


    if st.button(
        "🕒 Clinic Timings",
        key="sidebar_timings"
    ):
        st.session_state.quick_message = (
            "What are the clinic timings?"
        )
        st.rerun()


    st.divider()


    if st.button(
        "🗑️ Clear Conversation",
        key="clear_chat"
    ):

        st.session_state.messages = []

        st.session_state.session_id = str(
            uuid.uuid4()
        )

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

st.markdown("""
<div class="hero">

<h1>🏥 CareConnect AI</h1>

<p>
Your intelligent healthcare assistant for clinic information
and appointment support.
</p>

<div class="status-online">
🟢 AI Assistant Ready
</div>

</div>
""", unsafe_allow_html=True)


# =========================================================
# FEATURE CARDS
# =========================================================

col1, col2, col3 = st.columns(3)


# ASK QUESTIONS

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

    if st.button(
        "💬 Ask a Question",
        key="ask_question"
    ):

        st.session_state.quick_message = (
            "What services does the clinic provide?"
        )

        st.rerun()


# BOOK APPOINTMENT

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

    if st.button(
        "📅 Book Now",
        key="book_appointment"
    ):

        st.session_state.quick_message = (
            "I want to book an appointment"
        )

        st.rerun()


# PATIENT SUPPORT

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

    if st.button(
        "🧠 Get Patient Support",
        key="patient_support"
    ):

        st.session_state.quick_message = (
            "I need help as a patient. "
            "How do you support new and existing patients?"
        )

        st.rerun()


st.markdown("<br>", unsafe_allow_html=True)


# =========================================================
# CHAT SECTION
# =========================================================

st.markdown(
    '<div class="chat-header">💬 Chat with CareConnect AI</div>',
    unsafe_allow_html=True
)


# =========================================================
# WELCOME MESSAGE
# =========================================================

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
# DISPLAY CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.write(message["content"])


# =========================================================
# GET USER INPUT
# =========================================================

user_input = None


# Handle quick action

if st.session_state.quick_message:

    user_input = st.session_state.quick_message

    st.session_state.quick_message = None


# Normal chat input

chat_input = st.chat_input(
    "Ask about our clinic or request an appointment..."
)


if chat_input:

    user_input = chat_input


# =========================================================
# PROCESS MESSAGE
# =========================================================

if user_input:

    # Add user message

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })


    # Display user message

    with st.chat_message("user"):

        st.write(user_input)


    # AI response

    with st.chat_message("assistant"):

        with st.spinner("CareConnect AI is thinking..."):

            try:

                response = requests.post(

                    f"{BACKEND_URL}/chat",

                    json={
                        "session_id":
                            st.session_state.session_id,

                        "message":
                            user_input
                    },

                    timeout=60
                )


                # =============================================
                # SUCCESS
                # =============================================

                if response.status_code == 200:

                    data = response.json()


                    answer = data.get(
                        "response",
                        "Sorry, I couldn't generate a response."
                    )


                    st.write(answer)


                    # Agent details

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


                    # Save AI message

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })


                # =============================================
                # BACKEND ERROR
                # =============================================

                else:

                    st.error(
                        f"Backend Error: "
                        f"{response.status_code}"
                    )

                    st.code(
                        response.text
                    )


            # =============================================
            # CONNECTION ERROR
            # =============================================

            except requests.exceptions.ConnectionError:

                st.error(
                    "❌ Cannot connect to backend. "
                    "Make sure FastAPI is running."
                )


            # =============================================
            # TIMEOUT
            # =============================================

            except requests.exceptions.Timeout:

                st.error(
                    "⏳ The AI response took too long. "
                    "Please try again."
                )


            # =============================================
            # OTHER ERROR
            # =============================================

            except Exception as error:

                st.error(
                    f"❌ Unexpected error: {error}"
                )


# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div class="footer">

<b>CareConnect AI</b> • Intelligent Healthcare Assistant

<br><br>

Powered by RAG • AI Agents • FastAPI • Salesforce

</div>
""", unsafe_allow_html=True)