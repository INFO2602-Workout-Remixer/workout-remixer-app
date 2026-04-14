import httpx
from typing import List, Dict, Any
from app.config import get_settings

class AIService:
    def __init__(self):
        self.api_key = "sk-59addf63a8bd464c92242421db666aa1"
        self.base_url = "https://ai-gen.sundaebytesett.com"
        self.model = "meta/llama-3.2-3b-instruct"
    
    async def get_exercise_replacement(self, exercise_name: str, muscle_group: str, equipment: str) -> str:
        prompt = f"""Suggest an alternative exercise to replace {exercise_name} that works the {muscle_group} muscles. 
The alternative should use {equipment} or bodyweight if possible. 
Return ONLY the name of the exercise, nothing else. Keep it to 1-3 words."""
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are a fitness expert suggesting alternative exercises."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 50
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    suggestion = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    return suggestion.strip()
                else:
                    return self._get_fallback_suggestion(exercise_name, muscle_group)
        except Exception as e:
            print(f"AI API error: {e}")
            return self._get_fallback_suggestion(exercise_name, muscle_group)
    
    def _get_fallback_suggestion(self, exercise_name: str, muscle_group: str) -> str:
        fallbacks = {
            "chest": ["Push Up", "Incline Press", "Chest Fly", "Dumbbell Press"],
            "back": ["Pull Up", "Lat Pulldown", "Seated Row", "Barbell Row"],
            "legs": ["Squat", "Lunge", "Leg Press", "Deadlift"],
            "shoulders": ["Overhead Press", "Lateral Raise", "Front Raise", "Face Pull"],
            "arms": ["Bicep Curl", "Tricep Pushdown", "Hammer Curl", "Skull Crusher"],
            "core": ["Plank", "Russian Twist", "Leg Raise", "Crunches"]
        }
        
        import random
        options = fallbacks.get(muscle_group.lower(), [exercise_name, "Push Up", "Squat", "Plank"])
        return random.choice([e for e in options if e.lower() != exercise_name.lower()])
    
    async def generate_workout_suggestion(self, goal: str, available_equipment: List[str]) -> str:
        prompt = f"""Suggest a 5-exercise workout routine for someone whose goal is {goal}. 
Available equipment: {', '.join(available_equipment)}. 
Return ONLY the exercise names separated by commas."""
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are a personal trainer creating workout plans."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 100
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as e:
            print(f"AI API error: {e}")
        
        return "Push Up, Squat, Pull Up, Lunge, Plank"