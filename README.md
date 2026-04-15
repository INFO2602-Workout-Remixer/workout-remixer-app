# 💪 LiftLab - Workout Remixer App

## Group Members
| Name | Role | GitHub |
|------|------|--------|
| Deron | DevOps | @deron |
| Alex | Lead/UI Design | @alex |
| Aiden | Marketing | @aiden |

## Application Title
**LiftLab** - The AI-Powered Workout Remixer

## Features
- ✅ Exercise Library with 40+ exercises
- ✅ YouTube video tutorials for each exercise
- ✅ Create and manage workout routines
- ✅ AI-powered exercise remixer
- ✅ Active workout timer with rest intervals
- ✅ Community routines sharing
- ✅ Dashboard with progress charts
- ✅ AI fitness assistant chatbot

## Technologies Used
- **Backend:** FastAPI, Python, SQLModel
- **Frontend:** Jinja2, Bootstrap 5, JavaScript
- **Database:** PostgreSQL (Render), SQLite (local)
- **AI Integration:** LLM API for exercise recommendations
- **Deployment:** Render.com

## Live Application
🔗 https://liftlab-jy0x.onrender.com

## Test Credentials
- **Username:** bob
- **Password:** bobpass

## Setup Instructions
1. Clone repository: `git clone [URL]`
2. Create virtual environment: `python -m venv venv`
3. Activate: `.\venv\Scripts\Activate.ps1` (Windows)
4. Install: `pip install -e .`
5. Create `.env` file with `DATABASE_URI`, `SECRET_KEY`, `ENV`
6. Run: `uvicorn app.main:app --reload`
