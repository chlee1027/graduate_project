# Fitness AI Recommender - Project Guide

## 🚀 Project Overview
This project is a Reinforcement Learning-based fitness recommendation system. It uses a **Contextual Bandit (ε-greedy)** algorithm to suggest personalized workout plans based on user state and feedback.

## 🛠 Tech Stack
*   **Backend:** FastAPI (Python)
*   **Frontend:** React Native (Expo SDK 54)
*   **Database:** PostgreSQL (via Docker)
*   **Styling:** NativeWind (Tailwind CSS)
*   **State Management:** Zustand

## 🏃 Quick Start

### 1. Database (Docker)
Ensure Docker Desktop is running.
```powershell
docker-compose up -d
```

### 2. Backend (FastAPI)
```powershell
.\venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*   **Note:** `--host 0.0.0.0` is required for mobile device connectivity.

### 3. Frontend (Expo)
```powershell
cd frontend
npx expo start -c
```
*   Update `frontend/src/api/client.ts` with your PC's IPv4 address (Current: `192.168.45.48`).

## 📁 Directory Structure
*   `/app`: FastAPI backend logic, routers, and DB models.
*   `/frontend`: React Native (Expo) application.
*   `/docker-compose.yml`: Database container configuration.

## 🧠 Core Logic
1.  **Onboarding:** Collects user profile.
2.  **Recommend:** `Candidate Generator` filters plans, then `Bandit` selects the best action.
3.  **Log/Reward:** User records performance; system calculates reward and updates `BanditStat`.
