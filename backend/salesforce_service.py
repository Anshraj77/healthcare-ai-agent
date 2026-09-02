import os
from dotenv import load_dotenv

load_dotenv()


class SalesforceService:

    def __init__(self):
        self.enabled = os.getenv(
            "SALESFORCE_ENABLED",
            "false"
        ).lower() == "true"

        self.sf = None

        if self.enabled:
            try:
                from simple_salesforce import Salesforce

                self.sf = Salesforce(
                    username=os.getenv("SALESFORCE_USERNAME"),
                    password=os.getenv("SALESFORCE_PASSWORD"),
                    security_token=os.getenv(
                        "SALESFORCE_SECURITY_TOKEN"
                    ),
                    domain=os.getenv(
                        "SALESFORCE_DOMAIN",
                        "login"
                    ),
                )

                print("Salesforce connected successfully.")

            except Exception as error:
                print(
                    f"Salesforce connection failed: {error}"
                )
                self.sf = None

    def create_lead(
        self,
        name,
        email,
        phone,
        location=None,
        patient_type=None,
        lead_temperature="Warm",
    ):

        if not self.sf:

            print("Salesforce disabled - mock lead created.")

            return {
                "success": True,
                "mode": "mock",
                "lead_id": "MOCK_LEAD"
            }

        try:

            result = self.sf.Lead.create({

                "LastName": name or "Website Patient",

                "Company": "CareConnect AI",

                "Email": email,

                "Phone": phone,

                "Description":
                    f"Patient Type: {patient_type}\n"
                    f"Location: {location}\n"
                    f"Lead Temperature: "
                    f"{lead_temperature}"
            })

            return {
                "success": True,
                "mode": "salesforce",
                "lead_id": result["id"]
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error)
            }

    def create_task(
        self,
        lead_id,
        conversation,
        lead_temperature="Warm"
    ):

        if not self.sf:

            print("Salesforce disabled - mock task created.")

            return {
                "success": True,
                "mode": "mock",
                "task_id": "MOCK_TASK"
            }

        try:

            result = self.sf.Task.create({

                "WhoId": lead_id,

                "Subject":
                    f"CareConnect AI Conversation - "
                    f"{lead_temperature} Lead",

                "Status": "Not Started",

                "Priority":
                    "High"
                    if lead_temperature == "Hot"
                    else "Normal",

                "Description":
                    f"Lead Temperature: "
                    f"{lead_temperature}\n\n"
                    f"FULL CONVERSATION:\n"
                    f"{conversation}"
            })

            return {
                "success": True,
                "mode": "salesforce",
                "task_id": result["id"]
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error)
            }