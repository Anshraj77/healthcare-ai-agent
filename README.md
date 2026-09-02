# 🏥 CareConnect AI

An AI-powered healthcare clinic assistant built for the Tars assignment.

## What it does

- Answers common clinic questions using a lightweight knowledge base.
- Detects appointment intent.
- Conversationally collects appointment details.
- Identifies new vs existing patients.
- Scores lead quality as **Hot / Warm / Cold**.
- Stores the complete conversation as a Salesforce Task when Salesforce is configured.
- Creates a Salesforce Lead for the sales/follow-up team.
- Includes a polished Streamlit interface with functional quick actions.

## Architecture

```text
Streamlit Frontend
       |
       v
FastAPI Backend
       |
       +--> Intent Detection
       +--> Patient Type Detection
       +--> Clinic Knowledge Retrieval
       +--> Appointment Data Collection
       +--> Hot/Warm/Cold Lead Scoring
       |
       v
Salesforce Lead + Task
```

## Project structure

```text
CareConnect_AI_Project/
├── backend/
│   ├── __init__.py
│   ├── agent.py
│   ├── knowledge.py
│   ├── main.py
│   └── salesforce.py
├── frontend/
│   └── app.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Run locally

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env`.

Salesforce is optional. The project works in mock mode when:

```env
SALESFORCE_ENABLED=false
```

### 4. Start the backend

From the project root:

```powershell
python -m uvicorn backend.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

### 5. Start the frontend

Open a second terminal:

```powershell
streamlit run frontend/app.py
```

## Salesforce integration

Set these values in `.env`:

```env
SALESFORCE_ENABLED=true
SALESFORCE_USERNAME=your_username
SALESFORCE_PASSWORD=your_password
SALESFORCE_SECURITY_TOKEN=your_token
SALESFORCE_DOMAIN=login
```

When an appointment conversation is complete, the backend:

1. Creates a Salesforce Lead.
2. Adds the appointment context.
3. Creates a Salesforce Task linked to that Lead.
4. Stores the complete conversation in the Task description.
5. Labels the Task subject with Hot, Warm, or Cold lead temperature.

> Depending on the Salesforce org, a custom Lead Temperature field can also be added and mapped in `backend/salesforce.py`.

## Lead scoring

- **Hot**: Strong appointment intent plus enough contact/context signals.
- **Warm**: Appointment interest with partial qualification.
- **Cold**: General information seeker or limited contact context.

## Healthcare safety

CareConnect AI is designed for clinic information and appointment support. It does not diagnose conditions, prescribe treatment, or replace emergency medical care.

## Deployment

### Backend
Deploy the FastAPI backend to Render/Railway.

Start command:

```text
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### Frontend
Deploy Streamlit separately and set:

```toml
BACKEND_URL = "https://your-backend-url"
```

in Streamlit secrets, or change the backend URL configuration.
