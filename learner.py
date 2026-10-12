import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

LOG_FILE = "agent_actions.jsonl"
INSTRUCTION_FILE = "data/learned_instructions.txt"

class AILearner:
    def __init__(self):
        self.candidate_models = ["gemini-2.5-pro", "gemini-3.1-pro-preview", "gemini-pro-latest", "gemini-3.8-flash"]
        self.model = genai.GenerativeModel(self.candidate_models[0])

    def run_learning_cycle(self):
        """
        Reads logs, analyzes performance, and updates the system prompt.
        """
        if not os.path.exists(LOG_FILE):
            return "No logs found. Interact with the agent first to generate training data."

        # 1. Read Logs (Limit to last 50 interactions to save tokens)
        logs = []
        with open(LOG_FILE, "r") as f:
            for line in f:
                try:
                    logs.append(json.loads(line))
                except:
                    continue
        
        if not logs:
            return "Logs are empty. No training data available."

        # 2. Prepare Context for "Meta-Learning"
        training_data = json.dumps(logs[-50:], indent=2)
        
        prompt = f"""
        You are an AI Optimization Engine. 
        I am providing you with logs of an AI Data Analyst Agent's past interactions.
        
        --- LOGS START ---
        {training_data}
        --- LOGS END ---

        YOUR TASK:
        1. Analyze the 'user_query' vs 'output'. 
        2. Identify successful patterns (e.g., "SQL queries for 'trends' work best when grouping by month").
        3. Identify any vague answers or errors.
        4. Generate a concise list of "Strategic Guidelines" that the Agent should follow to improve future performance.
        
        OUTPUT FORMAT:
        Just the list of guidelines in plain text. No intro/outro.
        Example:
        - Always format dates as YYYY-MM-DD in SQL.
        - When asking for "Sales", check for 'total_amount' or 'gross_revenue' columns.
        """

        # 3. Generate New Instructions with fallback
        new_guidelines = None
        last_error = None
        for model_name in self.candidate_models:
            try:
                m = genai.GenerativeModel(model_name)
                response = m.generate_content(prompt)
                new_guidelines = response.text
                break
            except Exception as e:
                last_error = e
                continue

        if not new_guidelines:
            return f"Training Failed: {str(last_error)}"

        try:
            # 4. Save to Persistent Memory
            os.makedirs("data", exist_ok=True)
            with open(INSTRUCTION_FILE, "w") as f:
                f.write(new_guidelines)
            
            return f"Training Complete! New Guidelines Learned:\n{new_guidelines}"
        except Exception as e:
            return f"Training Failed: {str(e)}"

if __name__ == "__main__":
    learner = AILearner()
    print(learner.run_learning_cycle())