import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    SALESFORCE_ENABLED = (
        os.getenv("SALESFORCE_ENABLED", "false").lower() == "true"
    )

    SALESFORCE_USERNAME = os.getenv("SALESFORCE_USERNAME", "")
    SALESFORCE_PASSWORD = os.getenv("SALESFORCE_PASSWORD", "")
    SALESFORCE_SECURITY_TOKEN = os.getenv(
        "SALESFORCE_SECURITY_TOKEN", ""
    )


settings = Settings()