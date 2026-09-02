import os
import sys
import uuid
import textwrap
import streamlit as st


# =========================================================
# PROJECT PATH
# =========================================================

ROOT_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


# =========================================================
# STREAMLIT SECRETS
# =========================================================

def load_streamlit_secrets():

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

                os.environ[name] = str(
                    st.secrets[name]
                )

        except Exception:
            pass


load_streamlit_secrets()


# =========================================================
# IMPORT HEALTHCARE AGENT
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
# LOAD AGENT
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
# SESSION STATE
# =========================================================

if "session_id" not in st.session_state:

    st.session_state.session_id = str(
        uuid.uuid4()
    )


if "messages" not in st.session_state:

    st.session_state.messages = []


if "quick_message" not in st.session_state:

    st.session_state.quick_message = None


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL
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
       HERO
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

        line-height: 1.6;
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
       CHAT INPUT
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


    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] div {

        background-color: transparent !important;
    }


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
       ALERTS
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
       JSON
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


    #MainMenu {

        visibility: hidden;
    }


    footer {

        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("🏥 CareConnect")

    st.caption("AI Healthcare Platform")

    st.divider()


    # Agent status

    if agent_online:

        st.success("🟢 AI Agent Online")

    else:

        st.error("🔴 AI Agent Error")

        if agent_error:

            with st.expander("View Error"):

                st.code(agent_error)


    # Capabilities

    st.markdown(
        """
        <div class="sidebar-card">

            <h3>🤖 AI Capabilities</h3>

            <p>✓ Clinic Knowledge Assistant</p>

            <p>✓ Appointment Requests</p>

            <p>✓ Patient Type Detection</p>

            <p>✓ Salesforce Lead Integration</p>

            <p>✓ Hot / Warm / Cold Lead Scoring</p>

            <p>✓ Conversation Task Creation</p>

        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown("### ⚡ Quick Actions")


    # Appointment

    if st.button(
        "📅 Request Appointment",
        key="sidebar_appointment"
    ):

        st.session_state.quick_message = (
            "I want to book an appointment"
        )

        st.rerun()


    # Services

    if st.button(
        "🏥 Clinic Services",
        key="sidebar_services"
    ):

        st.session_state.quick_message = (
            "What services does the clinic provide?"
        )

        st.rerun()


    # Timings

    if st.button(
        "🕒 Clinic Timings",
        key="sidebar_timings"
    ):

        st.session_state.quick_message = (
            "What are the clinic timings?"
        )

        st.rerun()


    st.divider()


    # Clear

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

if agent_online:

    status_text = "🟢 AI Assistant Ready"

else:

    status_text = "🔴 AI Agent Initialization Failed"


st.markdown(
    textwrap.dedent(
        f"""
        <div class="hero">

            <h1>🏥 CareConnect AI</h1>

            <p>
                Your intelligent healthcare assistant for
                clinic information and appointment support.
            </p>

            <div class="status-online">
                {status_text}
            </div>

        </div>
        """
    ),
    unsafe_allow_html=True
)


# =========================================================
# FEATURE CARDS
# =========================================================

col1, col2, col3 = st.columns(3)


# =========================================================
# ASK QUESTIONS
# =========================================================

with col1:

    st.markdown(
        textwrap.dedent(
            """
            <div class="feature-card">

                <h3>💬 Ask Questions</h3>

                <p>
                    Get instant answers about clinic services,
                    locations, timings and more.
                </p>

            </div>
            """
        ),
        unsafe_allow_html=True
    )


    if st.button(
        "💬 Ask a Question",
        key="ask_question"
    ):

        st.session_state.quick_message = (
            "What services does the clinic provide?"
        )

        st.rerun()


# =========================================================
# BOOK APPOINTMENT
# =========================================================

with col2:

    st.markdown(
        textwrap.dedent(
            """
            <div class="feature-card">

                <h3>📅 Book Appointments</h3>

                <p>
                    Request an appointment directly through
                    our AI assistant.
                </p>

            </div>
            """
        ),
        unsafe_allow_html=True
    )


    if st.button(
        "📅 Book Now",
        key="book_appointment"
    ):

        st.session_state.quick_message = (
            "I want to book an appointment"
        )

        st.rerun()


# =========================================================
# PATIENT SUPPORT
# =========================================================

with col3:

    st.markdown(
        textwrap.dedent(
            """
            <div class="feature-card">

                <h3>🧠 Smart Patient Support</h3>

                <p>
                    Our AI understands whether you're a new
                    or existing patient.
                </p>

            </div>
            """
        ),
        unsafe_allow_html=True
    )


    if st.button(
        "🧠 Get Patient Support",
        key="patient_support"
    ):

        st.session_state.quick_message = (
            "I need help as a patient. "
            "How do you support new and existing patients?"
        )

        st.rerun()


# =========================================================
# CHAT HEADER
# =========================================================

st.markdown(
    '<div class="chat-header">💬 Chat with CareConnect AI</div>',
    unsafe_allow_html=True
)


# =========================================================
# WELCOME MESSAGE
# =========================================================

if len(st.session_state.messages) == 0:

    st.info(
        """
        👋 **Hello! I'm CareConnect AI.**

        I can help you with:

        - 🏥 Clinic services and locations
        - 🕒 Opening hours
        - 📅 Appointment requests
        - 🧠 New and existing patient support

        How can I help you today?
        """
    )


# =========================================================
# DISPLAY CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.write(
            message["content"]
        )


# =========================================================
# USER INPUT
# =========================================================

user_input = None


# Quick action

if st.session_state.quick_message:

    user_input = (
        st.session_state.quick_message
    )

    st.session_state.quick_message = None


# Normal chat

chat_input = st.chat_input(
    "Ask about our clinic or request an appointment..."
)


if chat_input:

    user_input = chat_input


# =========================================================
# PROCESS USER MESSAGE
# =========================================================

if user_input:

    # -----------------------------------------------------
    # Save user message
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )


    # -----------------------------------------------------
    # Display user
    # -----------------------------------------------------

    with st.chat_message("user"):

        st.write(user_input)


    # -----------------------------------------------------
    # Assistant
    # -----------------------------------------------------

    with st.chat_message("assistant"):

        if not agent_online:

            st.error(
                "The CareConnect AI agent could not start. "
                "Please check the Streamlit deployment logs."
            )

        else:

            with st.spinner(
                "CareConnect AI is thinking..."
            ):

                try:

                    # -----------------------------------------
                    # DIRECT AGENT CALL
                    # -----------------------------------------

                    data = agent.chat(

                        session_id=
                            st.session_state.session_id,

                        message=user_input
                    )


                    # -----------------------------------------
                    # RESPONSE
                    # -----------------------------------------

                    answer = data.get(

                        "response",

                        "Sorry, I couldn't generate a response."

                    )


                    st.write(answer)


                    # -----------------------------------------
                    # AGENT DETAILS
                    # -----------------------------------------

                    with st.expander(
                        "🧠 Agent Decision Details"
                    ):

                        metric1, metric2, metric3 = (
                            st.columns(3)
                        )


                        # Intent

                        with metric1:

                            st.metric(

                                "Intent",

                                data.get(
                                    "intent",
                                    "Unknown"
                                )
                            )


                        # Patient type

                        with metric2:

                            patient_type = (
                                data.get(
                                    "patient_type"
                                )
                            )


                            st.metric(

                                "Patient Type",

                                patient_type
                                if patient_type
                                else "Not Detected"
                            )


                        # Lead temperature

                        with metric3:

                            temperature = (
                                data.get(
                                    "lead_temperature"
                                )
                            )


                            st.metric(

                                "Lead Temperature",

                                temperature
                                if temperature
                                else "Not Applicable"
                            )


                        # Appointment information

                        appointment_data = (
                            data.get(
                                "appointment_data"
                            )
                        )


                        if appointment_data:

                            st.markdown(
                                "### 📋 Appointment Information"
                            )


                            st.json(
                                appointment_data
                            )


                        # Salesforce information

                        lead_id = data.get(
                            "lead_id"
                        )


                        task_created = data.get(
                            "task_created"
                        )


                        if lead_id:

                            st.success(
                                f"Salesforce Lead Created: {lead_id}"
                            )


                        if task_created:

                            st.success(
                                "Salesforce conversation Task created successfully."
                            )


                    # -----------------------------------------
                    # SAVE ASSISTANT MESSAGE
                    # -----------------------------------------

                    st.session_state.messages.append(

                        {
                            "role": "assistant",

                            "content": answer
                        }

                    )


                except Exception as error:

                    st.error(
                        f"❌ Agent Error: {error}"
                    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    textwrap.dedent(
        """
        <div class="footer">

            <b>CareConnect AI</b>
            • Intelligent Healthcare Assistant

            <br><br>

            Powered by RAG • AI Agents • Salesforce

        </div>
        """
    ),
    unsafe_allow_html=True
)