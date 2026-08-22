# Odoo-x-LDCE-Hackathon-
# GlobeTrotter ✈️

A multi-city travel planning and budget-tracking web application built for the hackathon. GlobeTrotter lets users create complex itineraries with nested cities/stops and activities, track categorical budget breakdowns, generate itineraries automatically using AI, and share read-only trips via unique share codes.

---

## 🛠️ Tech Stack

- **Backend Framework:** FastAPI (Python)
- **Database ORM:** SQLModel (SQLite engine)
- **AI Integration:** Google Gemini SDK (`gemini-2.5-flash`)
- **Validation:** Pydantic
- **Server:** Uvicorn

---

## 📁 Repository Structure

Odoo-x-LDCE-Hackathon-/
├── README.md
├── frontend/                 # empty (no app files yet)
└── backend/
    ├── main.py               # FastAPI app, CORS, routes, seed
    ├── models.py             # SQLModel tables + create/read schemas
    ├── database.py           # SQLite engine, sessions, create_db_and_tables
    ├── ai_service.py         # Gemini trip generation
    ├── requirements.txt
    └── globetrotter.db       # SQLite DB (created at runtime)