# 🧠 NeuraCity – Intelligent, Human-Centered Smart City Platform

NeuraCity is a unified smart-city platform that enables citizens to report problems using **image + automatic GPS location**, while AI analyzes the city's emotional mood, traffic, noise, and infrastructure health to provide smarter, safer, calmer routes and support city officials with automated summaries, work orders, and insights.

All data is synthetic, all maps are 2D, and the entire system runs on **React + FastAPI + Supabase + Gemini**, fully free and open-source.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Supabase account (free tier)
- Google Gemini API key

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
python -m app.main
```

Backend runs at: http://localhost:8000

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with API URL
npm run dev
```

Frontend runs at: http://localhost:5173

### Database Setup

1. Create a new Supabase project
2. Run the SQL scripts in `database/migrations/` to create tables
3. Run the seed scripts in `database/seeds/` to populate initial data
4. Update `.env` with your Supabase credentials

## 📋 Project Structure

```
NeuraCity/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/       # API endpoints
│   │   ├── core/      # Configuration
│   │   ├── services/  # Business logic
│   │   └── utils/     # Utilities
│   └── tests/         # Backend tests
├── frontend/          # React frontend
│   └── src/
│       ├── pages/     # Page components
│       ├── components/# Reusable components
│       └── lib/       # API clients
├── database/          # Database scripts
│   ├── migrations/    # Schema migrations
│   └── seeds/         # Seed data
└── docs/              # Documentation

```

## ✨ Core Features

### 1. Citizen Issue Reporting
- Upload image evidence (required)
- Automatic GPS location capture (required)
- Category selection: accident, pothole, traffic_light, other
- AI-powered severity & urgency scoring

### 2. City Mood Analysis
- Synthetic social sentiment analysis
- Emotion mapping per area
- Mood visualization on 2D map

### 3. Smart Routing
- **Drive Route**: Avoids accidents and high-urgency issues
- **Eco Route**: Minimizes congestion and CO₂
- **Quiet Walk**: Prefers low-noise paths

### 4. AI-Powered Admin Support
- Emergency summaries for accidents (Gemini)
- Automated work order suggestions
- Contractor and material recommendations

## 🧰 Technology Stack

**Frontend**: React 18, Vite, TailwindCSS, React Router, Leaflet.js
**Backend**: FastAPI, Python 3.10+
**Database**: Supabase (PostgreSQL)
**AI**: Google Gemini API, HuggingFace Transformers
**Maps**: OpenStreetMap + Leaflet

## 📖 Documentation

- [Full Project Roadmap](roadmap.md)
- [Context Document](context-neuracity-2025-11-14.md)
- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)

## 🔒 Security & Privacy

- No automatic emergency calls
- Mandatory image + GPS for evidence
- Admin validation required for all actions
- Synthetic data only (no real personal data)

## 📄 License

MIT License - Open source and free to use

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines first.

---

Built with ❤️ for smarter, safer cities
