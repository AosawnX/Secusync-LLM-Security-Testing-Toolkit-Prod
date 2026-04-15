# SECUSYNC — LLM Security Testing Toolkit

An open-source vulnerability scanning toolkit for LLM-integrated applications. SECUSYNC identifies Prompt Injection, System Prompt Leakage, File Poisoning, and Sensitive Information Disclosure flaws using a targeted mutation engine and hybrid analysis (deterministic + semantic).

## Setup Instructions

This project requires **Docker** and **Docker Compose** to run the complete stack effortlessly.

### 1. Prerequisites
- Docker & Docker Compose
- Node.js (for local frontend development)
- Python 3.10+ (for local backend development)

### 2. Run with Docker 

1. Create a `.env` file in the root based on `.env.example`:
   ```bash
   cp .env.example .env
   ```
2. Start the services:
   ```bash
   docker-compose up --build
   ```
3. Access the application:
   - Frontend Dashboard: [http://localhost:5173](http://localhost:5173)
   - Backend API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Local Development (Without Docker)

#### Backend
1. Open a terminal in the `backend/` folder.
2. Setup Virtual Environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run migrations:
   ```bash
   alembic upgrade head
   ```
5. Start Uvicorn Server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

#### Frontend
1. Open a terminal in the `frontend/` folder.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite server:
   ```bash
   npm run dev
   ```

> This project is a Final Year Project developed at Bahria University, Islamabad. 
