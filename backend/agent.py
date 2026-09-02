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

        print("Initializing CareConnect AI Agent...")

        self.rag = RAGSystem()

        self.salesforce = SalesforceService()

        self.sessions = {}

        self.client = None

        api_key = getattr(
            settings,
            "OPENAI_API_KEY",
            None
        )

        if api_key:

            self.client = OpenAI(
                api_key=api_key
            )

            print("OpenAI client initialized.")

        else:

            print(
                "OPENAI_API_KEY not configured. "
                "Knowledge-base fallback mode enabled."
            )

    # =========================================================
    # SESSION
    # =========================================================

    def get_session(self, session_id):

        if session_id not in self.sessions:

            self.sessions[session_id] = {

                "patient_type": None,

                "intent": None,

                "appointment_active": False,

                "appointment_data": {

                    "name": None,

                    "email": None,

                    "phone": None,

                    "location": None,

                    "date": None,

                    "reason": None
                },

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

        text = message.lower().strip()

        appointment_keywords = [

            "appointment",
            "book",
            "booking",
            "schedule",
            "consultation",
            "consult",
            "doctor appointment",
            "see doctor",
            "visit doctor",
            "meet doctor",
            "book doctor",
            "want to see"

        ]

        for keyword in appointment_keywords:

            if keyword in text:

                return "appointment"

        return "knowledge_query"

    # =========================================================
    # PATIENT TYPE
    # =========================================================

    def detect_patient_type(self, message):

        text = message.lower().strip()

        existing_keywords = [

            "existing patient",
            "already a patient",
            "i am an existing patient",
            "i'm an existing patient",
            "visited before",
            "i have visited before",
            "previous appointment",
            "old patient",
            "i was here before",
            "i have been here before",
            "reschedule",
            "cancel my appointment"

        ]

        new_keywords = [

            "new patient",
            "i am a new patient",
            "i'm a new patient",
            "first time",
            "first-time",
            "never visited",
            "never been here",
            "i am new",
            "i'm new",
            "visiting for the first time"

        ]

        for keyword in existing_keywords:

            if keyword in text:

                return "existing"

        for keyword in new_keywords:

            if keyword in text:

                return "new"

        return None

    # =========================================================
    # EMAIL
    # =========================================================

    def extract_email(self, message):

        pattern = (
            r"[A-Za-z0-9._%+-]+"
            r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
        )

        match = re.search(
            pattern,
            message
        )

        if match:

            return match.group(0)

        return None

    # =========================================================
    # PHONE
    # =========================================================

    def extract_phone(self, message):

        pattern = r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)"

        match = re.search(
            pattern,
            message
        )

        if match:

            return match.group(0).strip()

        # General fallback for international/other numbers

        fallback_pattern = (
            r"(?<!\d)"
            r"\+?\d[\d\s().-]{8,}"
            r"\d"
            r"(?!\d)"
        )

        fallback = re.search(
            fallback_pattern,
            message
        )

        if fallback:

            phone = fallback.group(0).strip()

            digits = re.sub(
                r"\D",
                "",
                phone
            )

            if len(digits) >= 10:

                return phone

        return None

    # =========================================================
    # LOCATION
    # =========================================================

    def extract_location(self, message):

        text = message.lower()

        locations = {

            "new delhi": "New Delhi",

            "delhi": "New Delhi",

            "mumbai": "Mumbai",

            "bombay": "Mumbai",

            "bangalore": "Bangalore",

            "bengaluru": "Bangalore",

            "hyderabad": "Hyderabad",

            "pune": "Pune",

            "chennai": "Chennai"
        }

        for key, value in locations.items():

            if key in text:

                return value

        return None

    # =========================================================
    # UPDATE APPOINTMENT DATA
    # =========================================================

    def update_appointment_data(
        self,
        session,
        message
    ):

        data = session["appointment_data"]

        email = self.extract_email(
            message
        )

        if email:

            data["email"] = email

        phone = self.extract_phone(
            message
        )

        if phone:

            data["phone"] = phone

        location = self.extract_location(
            message
        )

        if location:

            data["location"] = location

    # =========================================================
    # REQUIRED FIELD
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
                "Sure! May I have your full name?",

            "email":
                "Please provide your email address.",

            "phone":
                "Please provide your phone number.",

            "location":
                (
                    "Which clinic location would you prefer?"
                ),

            "date":
                "What is your preferred appointment date?",

            "reason":
                (
                    "Please briefly tell me the reason "
                    "for your visit."
                )
        }

        return questions.get(

            field,

            "Please provide the required information."
        )

    # =========================================================
    # CAPTURE FIELD
    # =========================================================

    def capture_current_field(
        self,
        session,
        message
    ):

        data = session["appointment_data"]

        missing_field = self.get_missing_field(
            data
        )

        if not missing_field:

            return

        clean_message = message.strip()

        # -----------------------------------------------------
        # NAME
        # -----------------------------------------------------

        if missing_field == "name":

            # Don't accidentally save "new patient"
            # as the patient's name.

            if self.detect_patient_type(
                message
            ):

                return

            if len(clean_message) >= 2:

                name = clean_message

                # Remove common prefixes

                name = re.sub(

                    r"^(my name is|i am|i'm|name is)\s+",

                    "",

                    name,

                    flags=re.IGNORECASE
                )

                data["name"] = name.strip()

        # -----------------------------------------------------
        # EMAIL
        # -----------------------------------------------------

        elif missing_field == "email":

            email = self.extract_email(
                message
            )

            if email:

                data["email"] = email

        # -----------------------------------------------------
        # PHONE
        # -----------------------------------------------------

        elif missing_field == "phone":

            phone = self.extract_phone(
                message
            )

            if phone:

                data["phone"] = phone

        # -----------------------------------------------------
        # LOCATION
        # -----------------------------------------------------

        elif missing_field == "location":

            location = self.extract_location(
                message
            )

            if location:

                data["location"] = location

        # -----------------------------------------------------
        # DATE
        # -----------------------------------------------------

        elif missing_field == "date":

            if len(clean_message) >= 3:

                data["date"] = clean_message

        # -----------------------------------------------------
        # REASON
        # -----------------------------------------------------

        elif missing_field == "reason":

            if len(clean_message) >= 3:

                data["reason"] = clean_message

    # =========================================================
    # LEAD TEMPERATURE
    # =========================================================

    def calculate_lead_temperature(
        self,
        session
    ):

        data = session["appointment_data"]

        conversation = (
            self.get_conversation_text(
                session
            ).lower()
        )

        score = 0

        # -----------------------------------------------------
        # HIGH-INTENT / URGENT WORDS
        # -----------------------------------------------------

        hot_keywords = [

            "urgent",

            "emergency",

            "as soon as possible",

            "today",

            "tomorrow",

            "immediately",

            "very soon",

            "need appointment",

            "want appointment",

            "book appointment",

            "book today"

        ]

        for keyword in hot_keywords:

            if keyword in conversation:

                score += 2

        # -----------------------------------------------------
        # INFORMATION COMPLETENESS
        # -----------------------------------------------------

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

        # -----------------------------------------------------
        # TEMPERATURE
        # -----------------------------------------------------

        if score >= 8:

            return "Hot"

        if score >= 4:

            return "Warm"

        return "Cold"

    # =========================================================
    # SALESFORCE
    # =========================================================

    def create_salesforce_lead(
        self,
        session
    ):

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

        lead_result = self.salesforce.create_lead(

            name=data.get("name"),

            email=data.get("email"),

            phone=data.get("phone"),

            location=data.get("location"),

            patient_type=patient_type,

            lead_temperature=lead_temperature
        )

        if not lead_result.get("success"):

            return {

                "success": False,

                "lead_temperature":
                    lead_temperature,

                "lead_result":
                    lead_result,

                "task_result":
                    None
            }

        # -----------------------------------------------------
        # LEAD ID
        # -----------------------------------------------------

        lead_id = lead_result.get(
            "lead_id"
        )

        # -----------------------------------------------------
        # FULL CONVERSATION
        # -----------------------------------------------------

        conversation = (
            self.get_conversation_text(
                session
            )
        )

        # -----------------------------------------------------
        # CREATE TASK
        # -----------------------------------------------------

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
                lead_result,

            "task_result":
                task_result
        }

    # =========================================================
    # KNOWLEDGE BASE
    # =========================================================

    def answer_from_knowledge_base(
        self,
        message
    ):

        results = self.rag.retrieve(
            message
        )

        if not results:

            return (
                "I couldn't find that information "
                "in our clinic knowledge base. "
                "Please contact the clinic directly "
                "for assistance."
            )

        context = "\n\n".join(

            result["text"]

            for result in results
        )

        # -----------------------------------------------------
        # NO OPENAI
        # -----------------------------------------------------

        if not self.client:

            return (
                "According to our clinic information:\n\n"
                + results[0]["text"]
            )

        # -----------------------------------------------------
        # OPENAI RESPONSE
        # -----------------------------------------------------

        prompt = f"""
You are CareConnect AI, a healthcare clinic
information and appointment assistant.

Use ONLY the clinic knowledge base below
to answer the patient's question.

Do not invent:
- doctors
- specialties
- clinic locations
- timings
- prices
- services
- appointment availability

If the requested information is not present
in the knowledge base, clearly say that you
do not have that information.

You may help with:
- clinic services
- available doctors
- medical specialties
- clinic locations
- clinic timings
- general appointment information

Do not diagnose medical conditions.

If the patient describes a medical emergency,
tell them to seek immediate emergency medical care.

CLINIC KNOWLEDGE BASE:

{context}

PATIENT QUESTION:

{message}

Give a concise, friendly answer.
"""

        try:

            model_name = getattr(

                settings,

                "OPENAI_MODEL",

                "gpt-4o-mini"
            )

            response = (
                self.client.chat.completions.create(

                    model=model_name,

                    messages=[

                        {
                            "role": "system",

                            "content":
                                (
                                    "You are CareConnect AI, "
                                    "a safe healthcare clinic "
                                    "assistant."
                                )
                        },

                        {
                            "role": "user",

                            "content": prompt
                        }
                    ],

                    temperature=0.2
                )
            )

            answer = (
                response
                .choices[0]
                .message
                .content
            )

            return answer.strip()

        except Exception as error:

            print(
                f"OpenAI Error: {error}"
            )

            return (
                "According to our clinic information:\n\n"
                + results[0]["text"]
            )

    # =========================================================
    # MAIN CHAT FUNCTION
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

        # -----------------------------------------------------
        # EMPTY MESSAGE
        # -----------------------------------------------------

        if not message:

            return {

                "response":
                    "Please enter a message.",

                "intent":
                    "knowledge_query",

                "patient_type":
                    session.get(
                        "patient_type"
                    ),

                "lead_temperature":
                    None,

                "appointment_data":
                    None
            }

        # -----------------------------------------------------
        # SAVE USER MESSAGE
        # -----------------------------------------------------

        self.add_conversation(

            session,

            "user",

            message
        )

        # -----------------------------------------------------
        # PATIENT TYPE DETECTION
        # -----------------------------------------------------

        detected_patient_type = (
            self.detect_patient_type(
                message
            )
        )

        if detected_patient_type:

            session["patient_type"] = (
                detected_patient_type
            )

        # -----------------------------------------------------
        # INTENT
        # -----------------------------------------------------

        detected_intent = (
            self.detect_intent(
                message
            )
        )

        # If appointment flow is already active,
        # keep appointment intent.

        if session["appointment_active"]:

            session["intent"] = "appointment"

        else:

            session["intent"] = detected_intent

        # =====================================================
        # APPOINTMENT FLOW ALREADY ACTIVE
        # =====================================================

        if session["appointment_active"]:

            # -------------------------------------------------
            # PATIENT TYPE NOT KNOWN
            # -------------------------------------------------

            if not session["patient_type"]:

                response_text = (

                    "I'd be happy to help with your "
                    "appointment. Before we continue, "
                    "are you a new patient visiting our "
                    "clinic for the first time, or are "
                    "you an existing patient?"
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

            # -------------------------------------------------
            # EXISTING PATIENT
            # -------------------------------------------------

            if (
                session["patient_type"]
                == "existing"
            ):

                session[
                    "appointment_active"
                ] = False

                response_text = (

                    "Thanks for letting me know. "
                    "Since you're an existing patient, "
                    "your request has been noted. "
                    "For existing-patient appointments, "
                    "rescheduling, or cancellations, "
                    "our clinic team will assist you "
                    "directly."
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
                        session[
                            "appointment_data"
                        ]
                }

            # -------------------------------------------------
            # NEW PATIENT
            # -------------------------------------------------

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

            # -------------------------------------------------
            # FIND MISSING INFORMATION
            # -------------------------------------------------

            missing_field = (
                self.get_missing_field(
                    data
                )
            )

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
                        session[
                            "patient_type"
                        ],

                    "lead_temperature":
                        self.calculate_lead_temperature(
                            session
                        ),

                    "appointment_data":
                        data
                }

            # -------------------------------------------------
            # ALL DETAILS COLLECTED
            # -------------------------------------------------

            salesforce_result = (
                self.create_salesforce_lead(
                    session
                )
            )

            session[
                "appointment_active"
            ] = False

            # -------------------------------------------------
            # SUCCESS
            # -------------------------------------------------

            if salesforce_result[
                "success"
            ]:

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

                task_created = (

                    task_result is not None

                    and

                    task_result.get(
                        "success",
                        False
                    )
                )

                response_text = (

                    "Thank you! Your appointment "
                    "request has been submitted "
                    "successfully. Our clinic team "
                    "will contact you soon."
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
                        session[
                            "patient_type"
                        ],

                    "lead_temperature":
                        lead_temperature,

                    "lead_id":
                        salesforce_result.get(
                            "lead_id"
                        ),

                    "task_created":
                        task_created,

                    "appointment_data":
                        data
                }

            # -------------------------------------------------
            # SALESFORCE FAILURE
            # -------------------------------------------------

            response_text = (

                "I collected your appointment "
                "details, but there was an issue "
                "submitting the request. Please try "
                "again or contact the clinic directly."
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
                    session[
                        "patient_type"
                    ],

                "lead_temperature":
                    salesforce_result.get(
                        "lead_temperature"
                    ),

                "appointment_data":
                    data
            }

        # =====================================================
        # START NEW APPOINTMENT FLOW
        # =====================================================

        if detected_intent == "appointment":

            session[
                "appointment_active"
            ] = True

            # -------------------------------------------------
            # ASK PATIENT TYPE
            # -------------------------------------------------

            if not session["patient_type"]:

                response_text = (

                    "I'd be happy to help you "
                    "request an appointment. "
                    "First, are you a new patient "
                    "visiting our clinic for the "
                    "first time, or are you an "
                    "existing patient?"
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

            # -------------------------------------------------
            # EXISTING PATIENT
            # -------------------------------------------------

            if (
                session["patient_type"]
                == "existing"
            ):

                session[
                    "appointment_active"
                ] = False

                response_text = (

                    "Thanks for letting me know "
                    "you're an existing patient. "
                    "Our clinic team can help you "
                    "with your appointment request, "
                    "rescheduling, or other existing-"
                    "patient needs."
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
                        session[
                            "appointment_data"
                        ]
                }

            # -------------------------------------------------
            # NEW PATIENT
            # -------------------------------------------------

            missing_field = (
                self.get_missing_field(
                    session[
                        "appointment_data"
                    ]
                )
            )

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
                    "new",

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
        # NORMAL KNOWLEDGE QUESTION
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
                session.get(
                    "patient_type"
                ),

            "lead_temperature":
                None,

            "appointment_data":
                None
        }