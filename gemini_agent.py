import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class GeminiModelManager:
    """
    Manages Gemini Flash models with graceful fallback if a model version is deprecated.
    """
    def __init__(self):
        self.candidate_models = ["gemini-2.5-flash", "gemini-3.8-flash", "gemini-flash-latest"]
        self.model_name = self.candidate_models[0]
        self.model = genai.GenerativeModel(self.model_name)
        logger.info(f"Initialized with {self.model_name}")

    def generate_content(self, prompt, config=None):
        """
        Executes generation using Gemini Flash with automatic fallback.
        """
        last_error = None
        models_to_try = [self.model_name] + [m for m in self.candidate_models if m != self.model_name]
        for candidate in models_to_try:
            try:
                logger.info(f"Generating content with {candidate}...")
                model = genai.GenerativeModel(candidate)
                response = model.generate_content(prompt, generation_config=config)
                self.model_name = candidate
                self.model = model
                return response
            except Exception as e:
                logger.warning(f"Generation failed with {candidate}: {e}")
                last_error = e
                continue
        logger.error(f"Error during generation across all models: {last_error}")
        raise last_error

class GeminiAnalyst:
    def __init__(self):
        self.manager = GeminiModelManager()

    def analyze_schema(self, file_name, columns, sample_data):
        """
        Generates summary, queries, and visualization recommendations using Gemini 2.5 Flash.
        """
        prompt = f"""
        You are an expert Data Analyst Agent.
        I have uploaded a file named '{file_name}'.
        
        Columns: {columns}
        Sample Data (first 3 rows): {sample_data}

        Please provide a response in valid JSON format with the following keys:
        1. "summary": A brief executive summary (max 3 sentences).
        2. "queries": A list of 3 DuckDB-compatible SQL queries.
        3. "viz_config": A dictionary containing:
            - "chart_type": One of ["bar", "line", "scatter", "pie", "histogram"]
            - "x_axis": The exact column name for the X-axis.
            - "y_axis": The exact column name for the Y-axis (or null if not applicable).
            - "title": A creative title for the chart.
        
        IMPORTANT: Return ONLY valid JSON. No markdown formatting.
        """
        response = self.manager.generate_content(
            prompt, 
            config={"response_mime_type": "application/json"}
        )
        return response.text

    def chat_with_data(self, query, context):
        """
        Chat functionality using Gemini 2.5 Flash.
        """
        learned_guidelines = ""
        try:
            if os.path.exists("data/learned_instructions.txt"):
                with open("data/learned_instructions.txt", "r") as f:
                    learned_guidelines = f"\n--- LEARNED GUIDELINES --- \n{f.read()}\n"
        except Exception:
            pass

        system_instruction = f"""
        You are a versatile AI Assistant and Senior Data Analyst.
        
        MODE 1: DATA ANALYSIS
        If the user asks about the dataset, use the context.
        
        MODE 2: GENERAL ASSISTANT
        If the user asks general questions, answer directly.
        
        {learned_guidelines}
        
        Be professional, concise, and helpful.
        """
        
        prompt = f"""
        {system_instruction}
        
        --- DATASET CONTEXT ---
        {context}
        -----------------------
        
        USER QUESTION: {query}
        """
        
        response = self.manager.generate_content(prompt)
        return response.text