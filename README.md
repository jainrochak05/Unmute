# Unmute - Emotional Wellness Flask MVP

## Setup

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Create `.env` from `.env.example` and fill values.

## Run

```bash
python emotional_wellness_app.py
```

App runs at: http://127.0.0.1:5000

## Features
- Authentication (register/login/logout)
- Mood tracking
- Journal entries
- Anonymous stories
- Daily prompt
- AI chat (Gemini)
- Dashboard metrics
- Profile
- Resources

## Notes
- Requires MongoDB Atlas URI.
- Requires Gemini API key.
- Chat gracefully returns friendly message if Gemini is not configured.
