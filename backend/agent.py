import re
from openai import OpenAI

from backend.config import settings
from backend.rag import RAGSystem
from backend.salesforce_service import SalesforceService


class HealthcareAgent:

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(self):

        self.rag = RAGSystem()
        self.salesforce = SalesforceService()
        self.sessions = {}
        self.client = None

        if settings.OPENAI_API_KEY:

            self.client = OpenAI(
                api_key=settings.OPENAI_API_KEY
            )

    # =========================================================
    # SESSION MANAGEMENT
    # =========================================================

    def get_session(self, session_id):

        if session_id not in self.sessions:

            self.sessions[session_id] = {

                "patient_type": None,

                "intent": None,

                "appointment_data": {
                    "name": None,
                    "email": None,
                    "phone": None,
                    "location": None,
                    "date": None,
                    "reason": None
                },

                "appointment_active": False,

                "conversation": []
            }

        return self.sessions[session_id]

    # =========================================================
    # CONVERSATION
    # =========================================================

    def add_conversation(
        self,
        session,
        role,
        message
    ):

        session["conversation"].append({
            "role": role,
            "message": message
        })

    def get_conversation_text(self, session):

        lines = []

        for item in session["conversation"]:

            lines.append(
                f"{item['role'].upper()}: "
                f"{item['message']}"
            )

        return "\n".join(lines)

    # =========================================================
    # INTENT DETECTION
    # =========================================================

    def detect_intent(self, message):

        message = message.lower()

        appointment_keywords = [

            "appointment",
            "book",
            "booking",
            "schedule",
            "consultation",
            "visit doctor",
            "see doctor",
            "meet doctor"

        ]

        for keyword in appointment_keywords:

            if keyword in message:
                return "appointment"

        return "knowledge_query"

    # =========================================================
    # PATIENT TYPE DETECTION
    # =========================================================

    def detect_patient_type(self, message):

        message = message.lower().strip()

        existing_keywords = [

            "existing patient",
            "already a patient",
            "visited before",
            "previous appointment",
            "my last appointment",
            "i have visited",
            "reschedule",
            "cancel my appointment",
            "old patient"

        ]

        new_keywords = [

            "new patient",
            "first time",
            "first-time",
            "never visited",
            "haven't visited",
            "have not visited",
            "i am new",
            "i'm new"

        ]

        for keyword in existing_keywords:

            if keyword in message:
                return "existing"

        for keyword in new_keywords:

            if keyword in message:
                return "new"

        return None

    # =========================================================
    # EMAIL EXTRACTION
    # =========================================================

    def extract_email(self, message):

        pattern = r'[\w\.-]+@[\w\.-]+\.\w+'

        match = re.search(
            pattern,
            message
        )

        if match:
            return match.group()

        return None

    # =========================================================
    # PHONE EXTRACTION
    # =========================================================

    def extract_phone(self, message):

        pattern = r'(\+?\d[\d\s-]{8,}\d)'

        match = re.search(
            pattern,
            message
        )

        if match:

            phone = re.sub(
                r'\D',
                '',
                match.group()
            )

            return phone

        return None

    # =========================================================
    # LOCATION EXTRACTION
    # =========================================================

    def extract_location(self, message):

        locations = [

            "new delhi",
            "delhi",
            "mumbai",
            "bangalore",
            "bengaluru"

        ]

        message_lower = message.lower()

        for location in locations:

            if location in message_lower:

                if location == "delhi":
                    return "New Delhi"

                if location == "bengaluru":
                    return "Bangalore"

                return location.title()

        return None

    # =========================================================
    # APPOINTMENT DATA UPDATE
    # =========================================================

    def update_appointment_data(
        self,
        session,
        message
    ):

        data = session["appointment_data"]

        email = self.extract_email(message)

        if email:
            data["email"] = email

        phone = self.extract_phone(message)

        if phone:
            data["phone"] = phone

        location = self.extract_location(message)

        if location:
            data["location"] = location

    # =========================================================
    # MISSING FIELD
    # =========================================================

    def get_missing_field(self, data):

        required_fields = [

            "name",
            "email",
            "phone",
            "location",
            "date",
            "reason"

        ]

        for field in required_fields:

            if not data.get(field):
                return field

        return None

    # =========================================================
    # FIELD QUESTIONS
    # =========================================================

    def ask_for_field(self, field):

        questions = {

            "name":
                "Sure! Please provide your full name.",

            "email":
                "Please provide your email address.",

            "phone":
                "Please provide your phone number.",

            "location":
                (
                    "Which clinic location would you prefer: "
                    "New Delhi, Mumbai, or Bangalore?"
                ),

            "date":
                "What is your preferred appointment date?",

            "reason":
                "Please briefly tell me the reason for your visit."

        }

        return questions.get(
            field,
            "Please provide the required information."
        )

    # =========================================================
    # CAPTURE CURRENT FIELD
    # =========================================================

    def capture_current_field(
        self,
        session,
        message
    ):

        data = session["appointment_data"]

        missing = self.get_missing_field(data)

        if missing is None:
            return

        message_clean = message.strip()

        # NAME
        if missing == "name":

            if self.detect_patient_type(message):
                return

            if len(message_clean) >= 2:
                data["name"] = message_clean

        # EMAIL
        elif missing == "email":

            email = self.extract_email(message)

            if email:
                data["email"] = email

        # PHONE
        elif missing == "phone":

            phone = self.extract_phone(message)

            if phone:
                data["phone"] = phone

        # LOCATION
        elif missing == "location":

            location = self.extract_location(message)

            if location:
                data["location"] = location

        # DATE
        elif missing == "date":

            if len(message_clean) >= 3:
                data["date"] = message_clean

        # REASON
        elif missing == "reason":

            if len(message_clean) >= 3:
                data["reason"] = message_clean

    # =========================================================
    # LEAD TEMPERATURE
    # =========================================================

    def calculate_lead_temperature(self, session):

        data = session["appointment_data"]

        conversation = (
            self.get_conversation_text(session)
            .lower()
        )

        score = 0

        hot_keywords = [

            "urgent",
            "emergency",
            "as soon as possible",
            "today",
            "tomorrow",
            "immediately",
            "very soon",
            "need appointment"

        ]

        for keyword in hot_keywords:

            if keyword in conversation:
                score += 2

        # Patient details

        if data.get("name"):
            score += 1

        if data.get("email"):
            score += 1

        if data.get("phone"):
            score += 1

        if data.get("location"):
            score += 1

        if data.get("date"):
            score += 2

        if data.get("reason"):
            score += 1

        # Temperature

        if score >= 8:
            return "Hot"

        if score >= 4:
            return "Warm"

        return "Cold"

    # =========================================================
    # KNOWLEDGE BASE RESPONSE
    # =========================================================

    def answer_from_knowledge_base(self, message):

        results = self.rag.retrieve(message)

        if not results:

            return (
                "I couldn't find that information in our "
                "clinic knowledge base. Please contact "
                "the clinic for assistance."
            )

        context = "\n\n".join(
            [
                result["text"]
                for result in results
            ]
        )

        # No OpenAI key

        if not self.client:

            return (
                "Based on our clinic information:\n\n"
                + results[0]["text"]
            )

        prompt = f"""

You are CareConnect Healthcare's helpful AI assistant.

Answer ONLY using the provided clinic knowledge base.

Do not invent clinic information.

If the answer is not available in the knowledge base,
say that you do not have that information and suggest
contacting the clinic.

Do not diagnose medical conditions.

Knowledge Base:

{context}

Patient Question:

{message}

Give a helpful, concise answer.

"""

        try:

            model_name = getattr(
                settings,
                "OPENAI_MODEL",
                "gpt-4o-mini"
            )

            response = self.client.chat.completions.create(

                model=model_name,

                messages=[

                    {
                        "role": "system",
                        "content": (
                            "You are a helpful healthcare "
                            "clinic assistant. "
                            "Do not provide medical diagnoses. "
                            "For emergencies, advise the patient "
                            "to seek immediate emergency care."
                        )
                    },

                    {
                        "role": "user",
                        "content": prompt
                    }

                ],

                temperature=0.2
            )

            return response.choices[
                0
            ].message.content

        except Exception as error:

            print(
                f"LLM Error: {error}"
            )

            return (
                "I found this information in our "
                "clinic knowledge base:\n\n"
                + results[0]["text"]
            )

    # =========================================================
    # SALESFORCE LEAD + TASK
    # =========================================================

    def create_salesforce_lead(self, session):

        data = session["appointment_data"]

        patient_type = (
            session.get("patient_type")
            or "new"
        )

        lead_temperature = (
            self.calculate_lead_temperature(
                session
            )
        )

        # -----------------------------------------------------
        # CREATE LEAD
        # -----------------------------------------------------

        result = self.salesforce.create_lead(

            name=data.get("name"),

            email=data.get("email"),

            phone=data.get("phone"),

            location=data.get("location"),

            patient_type=patient_type,

            lead_temperature=lead_temperature
        )

        if not result.get("success"):

            return {

                "success": False,

                "lead_temperature":
                    lead_temperature,

                "lead_result":
                    result,

                "task_result":
                    None
            }

        # -----------------------------------------------------
        # CREATE TASK
        # -----------------------------------------------------

        lead_id = result.get(
            "lead_id"
        )

        conversation = (
            self.get_conversation_text(
                session
            )
        )

        task_result = (
            self.salesforce.create_task(

                lead_id=lead_id,

                conversation=conversation,

                lead_temperature=lead_temperature
            )
        )

        return {

            "success": True,

            "lead_id":
                lead_id,

            "lead_temperature":
                lead_temperature,

            "lead_result":
                result,

            "task_result":
                task_result
        }

    # =========================================================
    # MAIN CHAT
    # =========================================================

    def chat(
        self,
        session_id,
        message
    ):

        session = self.get_session(
            session_id
        )

        message = message.strip()

        if not message:

            return {

                "response":
                    "Please enter a message.",

                "intent":
                    "knowledge_query",

                "patient_type":
                    session.get("patient_type"),

                "lead_temperature":
                    None,

                "appointment_data":
                    None
            }

        # Save user message

        self.add_conversation(
            session,
            "user",
            message
        )

        # =====================================================
        # PATIENT TYPE
        # =====================================================

        detected_patient_type = (
            self.detect_patient_type(
                message
            )
        )

        if detected_patient_type:

            session["patient_type"] = (
                detected_patient_type
            )

        # =====================================================
        # APPOINTMENT FLOW ACTIVE
        # =====================================================

        if session["appointment_active"]:

            # -----------------------------------------------
            # Patient type not known
            # -----------------------------------------------

            if not session["patient_type"]:

                response_text = (
                    "Are you a new patient visiting "
                    "our clinic for the first time, "
                    "or are you an existing patient?"
                )

                self.add_conversation(
                    session,
                    "assistant",
                    response_text
                )

                return {

                    "response":
                        response_text,

                    "intent":
                        "appointment",

                    "patient_type":
                        None,

                    "lead_temperature":
                        None,

                    "appointment_data":
                        session["appointment_data"]
                }

            # -----------------------------------------------
            # Update appointment fields
            # -----------------------------------------------

            self.update_appointment_data(
                session,
                message
            )

            self.capture_current_field(
                session,
                message
            )

            data = session[
                "appointment_data"
            ]

            missing_field = (
                self.get_missing_field(
                    data
                )
            )

            # -----------------------------------------------
            # Missing information
            # -----------------------------------------------

            if missing_field:

                response_text = (
                    self.ask_for_field(
                        missing_field
                    )
                )

                self.add_conversation(
                    session,
                    "assistant",
                    response_text
                )

                return {

                    "response":
                        response_text,

                    "intent":
                        "appointment",

                    "patient_type":
                        session["patient_type"],

                    "lead_temperature":
                        self.calculate_lead_temperature(
                            session
                        ),

                    "appointment_data":
                        data
                }

            # =================================================
            # EXISTING PATIENT
            # =================================================

            if session["patient_type"] == "existing":

                session[
                    "appointment_active"
                ] = False

                response_text = (

                    "Thank you. Since you are an existing "
                    "patient, your request has been noted. "
                    "For appointment modifications or "
                    "existing patient support, our clinic "
                    "team will assist you directly."

                )

                self.add_conversation(
                    session,
                    "assistant",
                    response_text
                )

                return {

                    "response":
                        response_text,

                    "intent":
                        "existing_patient_support",

                    "patient_type":
                        "existing",

                    "lead_temperature":
                        None,

                    "appointment_data":
                        data
                }

            # =================================================
            # NEW PATIENT
            # =================================================

            salesforce_result = (
                self.create_salesforce_lead(
                    session
                )
            )

            session[
                "appointment_active"
            ] = False

            if salesforce_result["success"]:

                lead_temperature = (
                    salesforce_result[
                        "lead_temperature"
                    ]
                )

                task_result = (
                    salesforce_result.get(
                        "task_result"
                    )
                )

                response_text = (

                    "Thank you! Your appointment request "
                    "has been submitted successfully. "
                    "Our clinic team will contact you soon."

                )

                self.add_conversation(
                    session,
                    "assistant",
                    response_text
                )

                return {

                    "response":
                        response_text,

                    "intent":
                        "appointment",

                    "patient_type":
                        session["patient_type"]
                        or "new",

                    "lead_temperature":
                        lead_temperature,

                    "lead_id":
                        salesforce_result.get(
                            "lead_id"
                        ),

                    "task_created":
                        bool(
                            task_result
                            and task_result.get(
                                "success"
                            )
                        ),

                    "appointment_data":
                        data
                }

            # =================================================
            # SALESFORCE ERROR
            # =================================================

            response_text = (

                "I collected your details, but there "
                "was an issue submitting the request. "
                "Please try again later or contact "
                "the clinic directly."

            )

            self.add_conversation(
                session,
                "assistant",
                response_text
            )

            return {

                "response":
                    response_text,

                "intent":
                    "appointment",

                "patient_type":
                    session["patient_type"],

                "lead_temperature":
                    salesforce_result.get(
                        "lead_temperature"
                    ),

                "appointment_data":
                    data
            }

        # =====================================================
        # INTENT DETECTION
        # =====================================================

        intent = self.detect_intent(
            message
        )

        session["intent"] = intent

        # =====================================================
        # START APPOINTMENT
        # =====================================================

        if intent == "appointment":

            session[
                "appointment_active"
            ] = True

            # -----------------------------------------------
            # Ask patient type
            # -----------------------------------------------

            if not session["patient_type"]:

                response_text = (

                    "I'd be happy to help with your "
                    "appointment. Before we continue, "
                    "are you a new patient visiting our "
                    "clinic for the first time, or are "
                    "you already an existing patient?"

                )

                self.add_conversation(
                    session,
                    "assistant",
                    response_text
                )

                return {

                    "response":
                        response_text,

                    "intent":
                        "appointment",

                    "patient_type":
                        None,

                    "lead_temperature":
                        None,

                    "appointment_data":
                        session[
                            "appointment_data"
                        ]
                }

            # -----------------------------------------------
            # Patient type already detected
            # -----------------------------------------------

            missing = (
                self.get_missing_field(
                    session[
                        "appointment_data"
                    ]
                )
            )

            response_text = (
                self.ask_for_field(
                    missing
                )
            )

            self.add_conversation(
                session,
                "assistant",
                response_text
            )

            return {

                "response":
                    response_text,

                "intent":
                    "appointment",

                "patient_type":
                    session["patient_type"],

                "lead_temperature":
                    self.calculate_lead_temperature(
                        session
                    ),

                "appointment_data":
                    session[
                        "appointment_data"
                    ]
            }

        # =====================================================
        # KNOWLEDGE BASE
        # =====================================================

        answer = (
            self.answer_from_knowledge_base(
                message
            )
        )

        self.add_conversation(
            session,
            "assistant",
            answer
        )

        return {

            "response":
                answer,

            "intent":
                "knowledge_query",

            "patient_type":
                session["patient_type"],

            "lead_temperature":
                None,

            "appointment_data":
                None
        }