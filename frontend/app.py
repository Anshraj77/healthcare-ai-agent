import os
import sys
import uuid

import streamlit as st


# ============================================================
# PROJECT PATH
# ============================================================

ROOT_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


# ============================================================
# LOAD STREAMLIT SECRETS
# ============================================================

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

                os.environ[name] = str(
                    st.secrets[name]
                )

        except Exception:
            pass


load_secrets()


# ============================================================
# IMPORT AGENT
# ============================================================

try:

    from backend.agent import HealthcareAgent

except Exception as error:

    HealthcareAgent = None

    IMPORT_ERROR = str(error)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CareConnect AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SIMPLE CSS
# No HTML UI is used anywhere below.
# ============================================================

st.markdown(
    """
    <style>

    /* Main application */

    .stApp {
        background-color: #f5f7fb;
    }

    /* Sidebar */

    section[data-testid="stSidebar"] {
        background-color: #0f172a;
    }

    section[data-testid="stSidebar"] * {
        color: #e5edf7;
    }

    /* Main headings */

    h1 {
        color: #164e63 !important;
    }

    h2 {
        color: #164e63 !important;
    }

    h3 {
        color: #155e75 !important;
    }

    /* Normal text */

    p {
        color: #334155;
    }

    /* Buttons */

    .stButton > button {
        width: 100%;
        border-radius: 10px;
        min-height: 44px;
        background-color: #0f766e;
        color: white;
        border: 1px solid #0f766e;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #115e59;
        border-color: #115e59;
        color: white;
    }

    /* Chat input */

    [data-testid="stChatInput"] {
        background-color: white;
        border: 2px solid #cbd5e1;
        border-radius: 14px;
    }

    [data-testid="stChatInput"] textarea {
        color: #111827 !important;
        background-color: white !important;
        -webkit-text-fill-color: #111827 !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #64748b !important;
        opacity: 1 !important;
    }

    /* Chat messages */

    [data-testid="stChatMessage"] {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 15px;
        margin-bottom: 10px;
    }

    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] span {
        color: #1e293b !important;
    }

    /* Metrics */

    [data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 10px;
    }

    [data-testid="stMetricValue"] {
        color: #0f766e !important;
    }

    /* Expanders */

    [data-testid="stExpander"] {
        background-color: white;
        border: 1px solid #dbe3ec;
        border-radius: 12px;
    }

    /* Alerts */

    [data-testid="stAlert"] {
        border-radius: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD AGENT
# ============================================================

@st.cache_resource
def load_agent():

    if HealthcareAgent is None:

        raise RuntimeError(
            IMPORT_ERROR
        )

    return HealthcareAgent()


try:

    agent = load_agent()

    agent_online = True

    agent_error = None

except Exception as error:

    agent = None

    agent_online = False

    agent_error = str(error)


# ============================================================
# SESSION STATE
# ============================================================

if "session_id" not in st.session_state:

    st.session_state.session_id = str(
        uuid.uuid4()
    )


if "messages" not in st.session_state:

    st.session_state.messages = []


if "quick_message" not in st.session_state:

    st.session_state.quick_message = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # BRAND
    # --------------------------------------------------------

    st.title("🏥 CareConnect")

    st.caption(
        "AI Healthcare Platform"
    )

    st.divider()


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if agent_online:

        st.success(
            "🟢 AI Agent Online"
        )

    else:

        st.error(
            "🔴 AI Agent Offline"
        )

        if agent_error:

            with st.expander(
                "Technical Error"
            ):

                st.code(
                    agent_error
                )


    # --------------------------------------------------------
    # CAPABILITIES
    # --------------------------------------------------------

    st.subheader(
        "🤖 AI Capabilities"
    )

    st.write(
        "✓ Clinic Knowledge Assistant"
    )

    st.write(
        "✓ Doctors & Specialties"
    )

    st.write(
        "✓ Appointment Requests"
    )

    st.write(
        "✓ New / Existing Patient Detection"
    )

    st.write(
        "✓ Salesforce Lead Integration"
    )

    st.write(
        "✓ Hot / Warm / Cold Lead Scoring"
    )

    st.write(
        "✓ Conversation Task Creation"
    )


    st.divider()


    # --------------------------------------------------------
    # QUICK ACTIONS
    # --------------------------------------------------------

    st.subheader(
        "⚡ Quick Actions"
    )


    if st.button(
        "📅 Request Appointment",
        key="sidebar_appointment"
    ):

        st.session_state.quick_message = (
            "I want to book an appointment"
        )

        st.rerun()


    if st.button(
        "👨‍⚕️ Doctors & Specialties",
        key="sidebar_doctors"
    ):

        st.session_state.quick_message = (
            "What doctors and medical specialties "
            "are available at the clinic?"
        )

        st.rerun()


    if st.button(
        "🏥 Clinic Services",
        key="sidebar_services"
    ):

        st.session_state.quick_message = (
            "What services and medical specialties "
            "are available at the clinic?"
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
        key="sidebar_clear"
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


# ============================================================
# MAIN HEADER
# ============================================================

st.title(
    "🏥 CareConnect AI"
)

st.subheader(
    "Your intelligent healthcare assistant"
)

st.write(
    "Get information about clinic services, doctors, "
    "medical specialties, timings, and appointment support."
)


# ============================================================
# STATUS
# ============================================================

if agent_online:

    st.success(
        "🟢 AI Assistant Ready"
    )

else:

    st.error(
        "🔴 AI Assistant could not be initialized."
    )


# ============================================================
# FEATURE SECTION
# ============================================================

st.markdown(
    "## How can I help you today?"
)


col1, col2, col3 = st.columns(3)


# ============================================================
# ASK QUESTIONS
# ============================================================

with col1:

    st.markdown(
        "### 💬 Ask Questions"
    )

    st.write(
        "Get quick answers about clinic services, "
        "doctors, specialties, locations and timings."
    )

    if st.button(
        "Ask the AI",
        key="ask_ai"
    ):

        st.session_state.quick_message = (
            "What doctors and medical specialties "
            "are available at the clinic?"
        )

        st.rerun()


# ============================================================
# APPOINTMENTS
# ============================================================

with col2:

    st.markdown(
        "### 📅 Book Appointment"
    )

    st.write(
        "Request a consultation and provide your "
        "details for the clinic team."
    )

    if st.button(
        "Start Appointment",
        key="start_appointment"
    ):

        st.session_state.quick_message = (
            "I want to book an appointment"
        )

        st.rerun()


# ============================================================
# PATIENT SUPPORT
# ============================================================

with col3:

    st.markdown(
        "### 🧠 Smart Patient Support"
    )

    st.write(
        "The assistant distinguishes new and existing "
        "patients and guides them accordingly."
    )

    if st.button(
        "Get Support",
        key="get_support"
    ):

        st.session_state.quick_message = (
            "How do you support new and existing patients?"
        )

        st.rerun()


# ============================================================
# DOCTOR / SPECIALTY SHORTCUTS
# ============================================================

st.markdown(
    "## 👨‍⚕️ Find a Doctor or Specialty"
)

st.write(
    "Ask CareConnect about the specialties available "
    "at your clinic."
)


specialty1, specialty2, specialty3, specialty4 = (
    st.columns(4)
)


with specialty1:

    if st.button(
        "🦷 Dentistry",
        key="dentistry"
    ):

        st.session_state.quick_message = (
            "Do you have a dentist or dentistry service?"
        )

        st.rerun()


with specialty2:

    if st.button(
        "❤️ Cardiology",
        key="cardiology"
    ):

        st.session_state.quick_message = (
            "Do you have a cardiologist or cardiology service?"
        )

        st.rerun()


with specialty3:

    if st.button(
        "🦴 Orthopedics",
        key="orthopedics"
    ):

        st.session_state.quick_message = (
            "Do you have an orthopedic doctor or orthopedics service?"
        )

        st.rerun()


with specialty4:

    if st.button(
        "🩺 General Medicine",
        key="general_medicine"
    ):

        st.session_state.quick_message = (
            "Do you have a general medicine doctor?"
        )

        st.rerun()


# ============================================================
# CHAT
# ============================================================

st.markdown(
    "## 💬 Chat with CareConnect AI"
)


if len(st.session_state.messages) == 0:

    st.info(
        """
        👋 **Welcome to CareConnect AI!**

        I can help you with:

        • 👨‍⚕️ Doctors and medical specialties

        • 🏥 Clinic services

        • 🕒 Clinic timings

        • 📅 Appointment requests

        • 🧠 New and existing patient support

        **Try asking:**
        "What doctors are available?"
        """
    )


# ============================================================
# DISPLAY HISTORY
# ============================================================

for message in st.session_state.messages:

    role = message.get(
        "role",
        "assistant"
    )

    content = message.get(
        "content",
        ""
    )

    with st.chat_message(role):

        st.markdown(
            content
        )


# ============================================================
# INPUT
# ============================================================

user_input = None


# ------------------------------------------------------------
# QUICK ACTION
# ------------------------------------------------------------

if st.session_state.quick_message:

    user_input = (
        st.session_state.quick_message
    )

    st.session_state.quick_message = None


# ------------------------------------------------------------
# CHAT INPUT
# ------------------------------------------------------------

chat_input = st.chat_input(
    "Ask about doctors, specialties, services or appointments..."
)


if chat_input:

    user_input = chat_input


# ============================================================
# PROCESS CHAT
# ============================================================

if user_input:

    # --------------------------------------------------------
    # SAVE USER
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )


    # --------------------------------------------------------
    # DISPLAY USER
    # --------------------------------------------------------

    with st.chat_message(
        "user"
    ):

        st.markdown(
            user_input
        )


    # --------------------------------------------------------
    # AI
    # --------------------------------------------------------

    with st.chat_message(
        "assistant"
    ):

        if not agent_online:

            error_message = (
                "The CareConnect AI agent is currently "
                "unavailable. Please check the deployment logs."
            )

            st.error(
                error_message
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message
                }
            )

        else:

            try:

                with st.spinner(
                    "CareConnect AI is thinking..."
                ):

                    result = agent.chat(

                        session_id=(
                            st.session_state.session_id
                        ),

                        message=user_input
                    )


                # ------------------------------------------------
                # RESPONSE
                # ------------------------------------------------

                answer = result.get(
                    "response",
                    "I couldn't generate a response."
                )


                # ------------------------------------------------
                # DISPLAY RESPONSE
                # ------------------------------------------------

                st.markdown(
                    answer
                )


                # ------------------------------------------------
                # SAVE RESPONSE
                # ------------------------------------------------

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )


                # ------------------------------------------------
                # AGENT DETAILS
                # ------------------------------------------------

                with st.expander(
                    "🧠 Agent Decision Details"
                ):

                    detail1, detail2, detail3 = (
                        st.columns(3)
                    )


                    # Intent

                    with detail1:

                        st.metric(
                            "Intent",
                            result.get(
                                "intent",
                                "Unknown"
                            )
                        )


                    # Patient type

                    with detail2:

                        patient_type = result.get(
                            "patient_type"
                        )

                        st.metric(
                            "Patient Type",
                            patient_type
                            if patient_type
                            else "Not Detected"
                        )


                    # Temperature

                    with detail3:

                        temperature = result.get(
                            "lead_temperature"
                        )

                        st.metric(
                            "Lead Temperature",
                            temperature
                            if temperature
                            else "Not Applicable"
                        )


                    # ------------------------------------------------
                    # APPOINTMENT DATA
                    # ------------------------------------------------

                    appointment_data = result.get(
                        "appointment_data"
                    )


                    if appointment_data:

                        st.markdown(
                            "### 📋 Appointment Details"
                        )

                        st.json(
                            appointment_data
                        )


                    # ------------------------------------------------
                    # SALESFORCE LEAD
                    # ------------------------------------------------

                    lead_id = result.get(
                        "lead_id"
                    )


                    if lead_id:

                        st.success(
                            "Salesforce Lead Created: "
                            + str(lead_id)
                        )


                    # ------------------------------------------------
                    # SALESFORCE TASK
                    # ------------------------------------------------

                    task_created = result.get(
                        "task_created"
                    )


                    if task_created:

                        st.success(
                            "Salesforce conversation Task "
                            "created successfully."
                        )


            except Exception as error:

                error_message = (
                    f"Agent Error: {error}"
                )

                st.error(
                    error_message
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message
                    }
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🏥 CareConnect AI • Intelligent Healthcare Assistant"
)

st.caption(
    "Powered by RAG • AI Agents • Salesforce"
)