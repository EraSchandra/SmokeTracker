# 🚭 SmokeTracker AI

**SmokeTracker AI** is an AI-powered smoking habit tracker that helps users understand patterns in their logged smoking behavior through data visualization and personalized AI insights.

## 🎯 Problem

People may notice that they smoke more in certain situations but may not clearly understand **when, where, or under what circumstances** these patterns appear.

SmokeTracker AI turns simple habit logs into understandable behavioral patterns around **time, mood, stress, location, and triggers**.

## 💡 Solution

SmokeTracker AI allows users to record smoking events along with contextual information such as:

* Number of cigarettes
* Mood
* Stress level
* Location
* Reason/trigger
* Time of the event

The application visualizes the collected information and uses aggregated statistics with an LLM to generate concise, personalized observations.

## ✨ Key Features

### 📝 Smoking Log

Record smoking events with contextual information including mood, stress, location, reason, and time.

### 📊 Interactive Dashboard

View key statistics and visualizations of logged smoking behavior.

### ✏️ Edit & Delete Logs

Update or remove previously recorded smoking entries.

### 🧠 AI Insights

The AI analyzes aggregated behavioral statistics to identify patterns such as:

* Frequently logged time of day
* Common moods
* Stress-level patterns
* Common locations
* Frequently logged triggers

The generated insight is designed to distinguish **observed patterns from predictions** and can suggest simple, low-risk actions users may try in situations where a pattern appears.

### 🔐 Privacy-Aware Analysis

Instead of unnecessarily sending raw database records to the LLM, the backend first converts the logs into lightweight aggregated statistics before requesting an insight.

### ⚠️ Responsible AI

SmokeTracker AI does not provide medical diagnoses, medical claims, or medical advice.

> **Disclaimer:** AI Insights are observations based on the user's logged data and are not medical advice or a medical diagnosis.

## 🏗️ Architecture

```text
User
  ↓
Streamlit Frontend
  ↓
FastAPI Backend
  ↓
SQLite Database
  ↓
Aggregated Behavioral Statistics
  ↓
LatentStack / Gemini
  ↓
AI Pattern Analysis
  ↓
Personalized Insight
  ↓
Streamlit Dashboard
```

## 🛠️ Tech Stack

* **Python**
* **Streamlit** — interactive frontend and dashboard
* **FastAPI** — backend API
* **SQLite** — local data storage
* **SQLAlchemy** — database interaction
* **Plotly** — data visualization
* **Gemini 3.1 Pro** — AI-powered pattern analysis
* **LatentStack** — LLM runtime access

## 🚀 Running Locally

### 1. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 2. Configure environment variables

Create a local `.env` file with the required LLM configuration.

**Never commit `.env` or API credentials to GitHub.**

### 3. Start the backend

```bash
py -m uvicorn backend.main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

### 4. Start the frontend

Open another terminal and run:

```bash
streamlit run frontend/app.py
```

The application will open in your browser.

## 📁 Project Structure

```text
SmokeTracker/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── config.py
│   ├── models/
│   ├── schemas/
│   └── routes/
├── frontend/
│   └── app.py
├── tests/
│   └── test_api.py
├── .gitignore
└── README.md
```

## 🧪 Testing

API tests are included in the `tests/` directory to help verify the backend functionality.

## 🌱 Future Improvements

Possible future improvements include:

* More detailed trigger categorization
* Longer-term behavioral trend analysis
* Additional visualization options
* More personalized pattern-based suggestions
* Expanded tracking and reporting features

## 🏆 BuildSprint 2026

SmokeTracker AI was built during **LatentForce BuildSprint 2026**.

The project demonstrates how lightweight behavioral analytics and AI-powered pattern analysis can transform simple habit logs into understandable, personalized insights.

### Responsible Use

SmokeTracker AI is designed as a **self-awareness and habit-tracking tool**. Its AI-generated insights reflect only the patterns present in the user's logged data and should not be interpreted as medical advice, diagnosis, or prediction.
