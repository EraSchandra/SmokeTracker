from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.schemas.smoking_log import SmokingLogsCreate
from backend.models.smoking_log import SmokingLog
from backend.database import get_db
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

router = APIRouter()

@router.get("/logs/insights")
def get_insights(db: Session = Depends(get_db)):
    logs = db.query(SmokingLog).all()
    
    if len(logs) < 2:
        return {"insight": "Not enough data yet. Log a few more entries to see your personalized AI insights!"}

    # Aggregate data
    total_cigs = 0
    mood_counts = {}
    valid_stress_sum = 0
    valid_stress_count = 0
    locations = {}
    time_of_day_counts = {"Morning": 0, "Afternoon": 0, "Evening": 0, "Night": 0}
    triggers = {}
    
    for log in logs:
        total_cigs += log.cigarettes
        
        mood = log.mood
        mood_counts[mood] = mood_counts.get(mood, 0) + 1
        
        if 1 <= log.stress_level <= 10:
            valid_stress_sum += log.stress_level
            valid_stress_count += 1
            
        loc = log.location.strip().lower() if log.location else "unknown"
        if loc:
            locations[loc] = locations.get(loc, 0) + 1

        reason = log.reason.strip().lower() if log.reason else "none"
        if reason and reason != "none":
            triggers[reason] = triggers.get(reason, 0) + 1
            
        if log.smoked_at:
            hour = log.smoked_at.hour
            if 5 <= hour < 12:
                time_of_day_counts["Morning"] += 1
            elif 12 <= hour < 17:
                time_of_day_counts["Afternoon"] += 1
            elif 17 <= hour < 22:
                time_of_day_counts["Evening"] += 1
            else:
                time_of_day_counts["Night"] += 1

    avg_stress = round(valid_stress_sum / valid_stress_count, 1) if valid_stress_count > 0 else 0
    
    # Keep only the top 3 triggers to avoid overwhelming the prompt if they enter paragraphs of text
    top_triggers = dict(sorted(triggers.items(), key=lambda item: item[1], reverse=True)[:3])

    summary_data = {
        "total_entries": len(logs),
        "total_cigarettes": total_cigs,
        "average_stress_out_of_10": avg_stress,
        "mood_frequencies": mood_counts,
        "common_locations": locations,
        "time_of_day_frequencies": time_of_day_counts,
        "common_triggers_reasons": top_triggers
    }

    api_key = os.getenv("LATENTSTACK_API_KEY")
    if not api_key:
        return {"insight": "AI Insights are currently unavailable (missing configuration)."}

    try:
        client = OpenAI(
            base_url="https://latentstack.dev/v1",
            api_key=api_key
        )

        prompt = f"""You are an empathetic, analytical habit-tracker assistant. 
Review the following aggregated JSON data representing a user's smoking logs.

Produce a concise, behavioral insight (4-6 sentences maximum) structured as follows:
1. Pattern observed: Clearly state the strongest pattern found in the logged data (e.g., time of day, mood, location). If data is too small to establish a strong pattern, explicitly state that this is a tentative observation.
2. Context: Explain when, where, or under what stress level/mood it tends to occur based on the data.
3. Contrast (if applicable): Mention a calm or lower-stress pattern if enough data exists to support it.
4. Practical suggestion: Give 1-2 simple, non-medical, low-risk strategies the user could try in the identified situation, and suggest logging future results to see if the pattern changes.

CRITICAL RULES:
- Only make claims explicitly supported by the JSON data provided.
- Do NOT make any medical diagnoses, medical claims, or give medical advice.
- Do NOT make unsupported causal claims (e.g., do not say "stress causes smoking"; say "smoking was frequently logged during periods of high stress").
- Clearly frame your response as an observation of their logged data, not a prediction.
- Keep the tone neutral, supportive, and non-judgmental.
- Do not use markdown headers; write as a cohesive paragraph.

Data:
{json.dumps(summary_data, indent=2)}
"""

        response = client.chat.completions.create(
            model="gemini/gemini-3.1-pro",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4000
        )
        
        insight_text = response.choices[0].message.content.strip()
        return {"insight": insight_text}

    except Exception as e:
        return {"insight": "We couldn't generate an insight right now. Please try again later."}

@router.post("/logs")
def create_log(log:SmokingLogsCreate, db: Session = Depends(get_db)):
    db_log= SmokingLog(
        cigarettes=log.cigarettes,
        mood=log.mood,
        stress_level= log.stress_level,
        location=log.location,
        reason= log.reason,
        smoked_at=log.smoked_at
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return{
        "message":"Smoking log recieved successfully",
        "data":db_log
    }

@router.get("/logs")
def get_logs(db: Session = Depends(get_db)):
    logs = db.query(SmokingLog).all()
    return logs

@router.put("/logs/{log_id}")
def update_log(log_id: int, update_log: SmokingLogsCreate, db: Session = Depends(get_db)):
    log=db.query(SmokingLog).filter(SmokingLog.id == log_id).first()
    if log is None:
        return{"message":"Log not found"}
    
    log.cigarettes=update_log.cigarettes
    log.mood= update_log.mood
    log.stress_level = update_log.stress_level
    log.location= update_log.location
    log.reason=update_log.reason
    log.smoked_at = update_log.smoked_at
    
    db.commit()
    db.refresh(log)

    return{
        "message":"Log updated sucessfully","data":log
    }

@router.delete("/logs/{log_id}")
def delete_log(log_id: int, db: Session = Depends(get_db)):
    log=db.query(SmokingLog).filter(SmokingLog.id == log_id).first()
    if log is None:
        return{"Message":"Log not found"}
    
    db.delete(log)
    db.commit()
    
    return{
        "message":"Log Deleted sucessfully","data":log
    }