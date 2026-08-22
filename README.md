# GlobeTrotter - AI Travel Planner

GlobeTrotter is a full-stack, AI-powered travel planning companion featuring interactive itinerary builders, dynamic local recommendations, a community-driven travel feed, and a role-based administrative dashboard. 

The application is tailored for the **Indian context**, featuring prices and budgets in **Indian Rupees (INR/₹)**, local destinations (Delhi, Munnar, Goa, Agra), and Indian travel profiles.

---

## 🚀 Features

### 1. Indian Context & Currency
- Denominated all budgets, costs, and revenues in Indian Rupees (`₹` / INR).
- Seeded default trips featuring local tours (e.g., Delhi Golden Triangle, Kerala Backwaters).

### 2. Custom Activity Planner (Unlocked)
- Replaced the hardcoded "Premium" popup blocking users from tailoring itineraries.
- Features a beautiful interactive modal allowing users to log custom activities (name, time, cost, category) for any day.
- New activities automatically persist in the database and instantly re-render timelines and spent budget calculations.

### 3. Dynamic Destination Recommendations & Images
- Swaps recommendation cards (descriptions, costs, and types) dynamically in the Trip Planner based on the chosen destination.
- Renders high-fidelity localized assets (e.g., Red Fort in Delhi, tea walks in Munnar, watersports in Goa) for both recommendation cards and community feed items.

### 4. Interactive Community Feed
- Load, create, and publish posts dynamically from/to the backend.
- Filter feed posts by destination (All, Delhi, Goa, Munnar, Amalfi, Kyoto) using interactive tab filters.

### 5. Role-Based Access Guard & Admin Panel
- **Security guards:** Added client-side auth guards. Users without the `"admin"` role are blocked from entering the administrative dashboard and redirected to `/my-journeys` with an alert.
- **Admin Dashboard:** Features real-time system metrics (Users, Active Trips, Posts, and Total Revenue in INR) and displays the user activity database directory.

### 6. Navigational Calendar Widget
- Instantly highlights active travel dates on a dropdown calendar directly from any page in the application.

---

## 🛠️ Project Architecture

- **Frontend:** HTML5, CSS3, TailwindCSS, Vanilla JS, and `mock-api.js` (proxies requests to fallback data if the FastAPI server is offline).
- **Backend:** FastAPI (Python), SQLModel/Pydantic, SQLite, Uvicorn, and `google-generativeai` SDK.

---

## ⚙️ Setup & Running Instructions

### 1. Backend Server Setup
From the `backend/` directory:

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create or verify `backend/.env` containing your Gemini API key:
   ```env
   GEMINI_API_KEY=YOUR_GCP_API_KEY
   ```
3. Run the FastAPI development server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### 2. Frontend Server Setup
From the `frontend/` directory:

#### Option A: Python server (Built-in)
Run the simple built-in routing script:
```bash
python server.py
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser.

#### Option B: Express server (Node.js)
```bash
npm install
npm start
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser.

---

## 🔑 Test Credentials

| Role | Email | Password | Access |
|---|---|---|---|
| **User** | `aarav@globetrotter.dev` | `password123` | Trip Planner, Itinerary Builder, Community |
| **Admin** | `admin@globetrotter.dev` | `adminpassword` | Full Dashboard, User List, Metrics |