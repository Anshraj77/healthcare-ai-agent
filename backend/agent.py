import re
from openai import OpenAI

from backend.config import settings
from backend.rag import RAGSystem
from backend.salesforce_service import SalesforceService


class HealthcareAgent:

    def __init__(self):

        self.rag = RAGSystem()

        self.salesforce = SalesforceService()

        self.sessions = {}

        self.client = None

        if settings.OPENAI_API_KEY:

            self.client = OpenAI(
                api_key=settings.OPENAI_API_KEY
            )

    # -----------------------------------------
    # SESSION
    # -----------------------------------------

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

                "appointment_active": False
            }

        return self.sessions[session_id]

    # -----------------------------------------
    # INTENT DETECTION
    # -----------------------------------------

    def detect_intent(self, message):

        message = message.lower()

        appointment_keywords = [

            "appointment",
            "book",
            "booking",
            "schedule",
            "consultation",
            "visit doctor",
            "see doctor"
        ]

        for keyword in appointment_keywords:

            if keyword in message:

                return "appointment"

        return "knowledge_query"

    # -----------------------------------------
    # PATIENT TYPE DETECTION
    # -----------------------------------------

    def detect_patient_type(self, message):

        message = message.lower()

        existing_keywords = [

            "existing patient",
            "already a patient",
            "visited before",
            "my previous appointment",
            "my last appointment",
            "i have visited",
            "reschedule",
            "cancel my appointment"
        ]

        new_keywords = [

            "new patient",
            "first time",
            "never visited",
            "haven't visited",
            "i want to know about your clinic"
        ]

        for keyword in existing_keywords:

            if keyword in message:

                return "existing"

        for keyword in new_keywords:

            if keyword in message:

                return "new"

        return None

    # -----------------------------------------
    # EXTRACT EMAIL
    # -----------------------------------------

    def extract_email(self, message):

        pattern = r'[\w\.-]+@[\w\.-]+\.\w+'

        match = re.search(
            pattern,
            message
        )

        if match:

            return match.group()

        return None

    # -----------------------------------------
    # EXTRACT PHONE
    # -----------------------------------------

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

    # -----------------------------------------
    # EXTRACT LOCATION
    # -----------------------------------------

    def extract_location(self, message):

        locations = [

            "new delhi",
            "mumbai",
            "bangalore"
        ]

        message_lower = message.lower()

        for location in locations:

            if location in message_lower:

                return location.title()

        return None

    # -----------------------------------------
    # UPDATE APPOINTMENT DATA
    # -----------------------------------------

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

    # -----------------------------------------
    # FIND MISSING FIELD
    # -----------------------------------------

    def get_missing_field(
        self,
        data
    ):

        for field, value in data.items():

            if not value:

                return field

        return None

    # -----------------------------------------
    # FIELD QUESTIONS
    # -----------------------------------------

    def ask_for_field(
        self,
        field
    ):

        questions = {

            "name":
                "Sure! Please provide your full name.",

            "email":
                "Please provide your email address.",

            "phone":
                "Please provide your phone number.",

            "location":
                "Which clinic location would you prefer: New Delhi, Mumbai, or Bangalore?",

            "date":
                "What is your preferred appointment date?",

            "reason":
                "Please briefly tell me the reason for your visit."
        }

        return questions.get(
            field,
            "Please provide the required information."
        )

    # -----------------------------------------
    # EXTRACT CURRENT FIELD
    # -----------------------------------------

    def capture_current_field(
        self,
        session,
        message
    ):

        data = session["appointment_data"]

        missing = self.get_missing_field(data)

        if missing is None:

            return

        if missing == "name":

            # Basic validation
            if len(message.strip()) >= 2:
                data["name"] = message.strip()

        elif missing == "email":

            email = self.extract_email(message)

            if email:
                data["email"] = email

        elif missing == "phone":

            phone = self.extract_phone(message)

            if phone:
                data["phone"] = phone

        elif missing == "location":

            location = self.extract_location(message)

            if location:
                data["location"] = location

        elif missing == "date":

            if len(message.strip()) >= 3:
                data["date"] = message.strip()

        elif missing == "reason":

            if len(message.strip()) >= 3:
                data["reason"] = message.strip()

    # -----------------------------------------
    # RAG RESPONSE
    # -----------------------------------------

    def answer_from_knowledge_base(
        self,
        message
    ):

        results = self.rag.retrieve(
            message
        )

        context = "\n\n".join(
            [result["text"] for result in results]
        )

        # If API key is unavailable,
        # return retrieved information

        if not self.client:

            return (
                "Based on our clinic information:\n\n"
                + results[0]["text"]
            )

        prompt = f"""
You are CareConnect Healthcare's helpful AI assistant.

Answer ONLY using the provided clinic knowledge base.

If the answer is not available in the knowledge base,
say that you do not have that information and suggest
contacting the clinic.

Knowledge Base:

{context}

Patient Question:

{message}

Give a helpful, concise answer.
"""

        try:

            response = self.client.chat.completions.create(

                model="gpt-4o-mini",

                messages=[
                    {
                        "role": "system",
                        "content":
                        "You are a helpful healthcare clinic assistant."
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
                "I found this information in our clinic "
                "knowledge base:\n\n"
                + results[0]["text"]
            )

    # -----------------------------------------
    # MAIN CHAT FUNCTION
    # -----------------------------------------

    def chat(
        self,
        session_id,
        message
    ):

        session = self.get_session(
            session_id
        )

        # Detect patient type

        detected_patient_type = (
            self.detect_patient_type(message)
        )

        if detected_patient_type:

            session["patient_type"] = (
                detected_patient_type
            )

        # -------------------------------------
        # APPOINTMENT FLOW ALREADY ACTIVE
        # -------------------------------------

        if session["appointment_active"]:

            self.capture_current_field(
                session,
                message
            )

            data = session[
                "appointment_data"
            ]

            missing_field = (
                self.get_missing_field(data)
            )

            if missing_field:

                return {

                    "response":
                        self.ask_for_field(
                            missing_field
                        ),

                    "intent":
                        "appointment",

                    "patient_type":
                        session["patient_type"],

                    "appointment_data":
                        data
                }

            # ---------------------------------
            # EXISTING PATIENT
            # ---------------------------------

            if session["patient_type"] == "existing":

                session[
                    "appointment_active"
                ] = False

                return {

                    "response": (
                        "Thank you. Since you are an existing "
                        "patient, your request has been noted. "
                        "For appointment modifications or "
                        "existing patient support, our clinic "
                        "team will assist you directly."
                    ),

                    "intent":
                        "existing_patient_support",

                    "patient_type":
                        "existing",

                    "appointment_data":
                        data
                }

            # ---------------------------------
            # NEW PATIENT
            # ---------------------------------

            result = self.salesforce.create_lead(
                data
            )

            session[
                "appointment_active"
            ] = False

            if result["success"]:

                return {

                    "response": (
                        "Thank you! Your appointment request "
                        "has been submitted successfully. "
                        "Our clinic team will contact you soon."
                    ),

                    "intent":
                        "appointment",

                    "patient_type":
                        session["patient_type"]
                        or "new",

                    "appointment_data":
                        data
                }

            return {

                "response": (
                    "I collected your details, but there was "
                    "an issue submitting the request. "
                    "Please try again later."
                ),

                "intent":
                    "appointment",

                "patient_type":
                    session["patient_type"],

                "appointment_data":
                    data
            }

        # -------------------------------------
        # DETECT INTENT
        # -------------------------------------

        intent = self.detect_intent(
            message
        )

        session["intent"] = intent

        # -------------------------------------
        # APPOINTMENT START
        # -------------------------------------

        if intent == "appointment":

            session[
                "appointment_active"
            ] = True

            if not session["patient_type"]:

                return {

                    "response": (
                        "I'd be happy to help with your "
                        "appointment. Before we continue, "
                        "are you a new patient visiting our "
                        "clinic for the first time, or are "
                        "you already an existing patient?"
                    ),

                    "intent":
                        "appointment",

                    "patient_type": None,

                    "appointment_data":
                        session["appointment_data"]
                }

            missing = self.get_missing_field(
                session["appointment_data"]
            )

            return {

                "response":
                    self.ask_for_field(
                        missing
                    ),

                "intent":
                    "appointment",

                "patient_type":
                    session["patient_type"],

                "appointment_data":
                    session["appointment_data"]
            }

        # -------------------------------------
        # ASK PATIENT TYPE IF APPOINTMENT
        # -------------------------------------

        if (
            session["appointment_active"]
            and not session["patient_type"]
        ):

            return {

                "response": (
                    "Are you a new patient or an existing patient?"
                ),

                "intent":
                    "appointment",

                "patient_type": None,

                "appointment_data":
                    session["appointment_data"]
            }

        # -------------------------------------
        # KNOWLEDGE BASE
        # -------------------------------------

        answer = self.answer_from_knowledge_base(
            message
        )

        return {

            "response": answer,

            "intent": "knowledge_query",

            "patient_type":
                session["patient_type"],

            "appointment_data": None
        }