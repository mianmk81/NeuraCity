# NeuraCity Frontend

React + Vite frontend for the NeuraCity smart city platform.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API URL
```

3. Run development server:
```bash
npm run dev
```

The app will be available at http://localhost:5173

## Build for Production

```bash
npm run build
npm run preview  # Preview production build
```

## Project Structure

```
frontend/
├── src/
│   ├── pages/          # Page components
│   ├── components/     # Reusable components
│   ├── lib/            # API clients and utilities
│   ├── assets/         # Static assets
│   ├── App.jsx         # Main app component
│   └── main.jsx        # Entry point
├── public/             # Public static files
└── package.json        # Dependencies
```

## Key Features

- **Issue Reporting**: Image upload + GPS location capture
- **Smart Routing**: Drive, Eco, and Quiet Walking routes
- **Mood Map**: City emotional analytics visualization
- **Admin Panel**: Emergency queue and work orders
- **Interactive Maps**: Leaflet.js with OpenStreetMap

## Tech Stack

- React 18
- Vite
- TailwindCSS
- React Router
- Leaflet.js
- Axios
