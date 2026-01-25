from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import shutil
import os
import json
import logging
import io 
from learner import AILearner

# Import our new modular components
from detector import detect_file_type
from loader import DataLoader
from cleaner import DataCleaner
from sql_engine import SQLEngine
from gemini_agent import GeminiAnalyst
from exporter import ReportExporter
from rag_engine import RAGEngine
from logger import log_action
from security import SecurityManager 

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("API")

app = FastAPI(title="AI Data Analyst Agent")

# Initialize Components
try:
    security = SecurityManager() # Auto-init encryption
    loader = DataLoader(security_manager=security) # Pass security to loader
    cleaner = DataCleaner()
    sql_engine = SQLEngine()
    agent = GeminiAnalyst()
    exporter = ReportExporter()
    rag = RAGEngine(security_manager=security) # Pass security to RAG
    logger.info("All components initialized successfully in SECURE MODE.")
except Exception as e:
    logger.error(f"Critical Component Failure: {e}")
    raise e

UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Global state
CURRENT_DATAFRAME = None
CURRENT_FILENAME = ""

@app.get("/")
def read_root():
    return {"status": "Server is running (Encrypted)", "message": "Welcome to the AI Data Analyst API"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global CURRENT_DATAFRAME, CURRENT_FILENAME
    
    try:
        file_location = f"{UPLOAD_DIR}/{file.filename}"
        
        # 1. READ & ENCRYPT IMMEDIATELY
        content = await file.read()
        encrypted_content = security.encrypt_data(content)
        
        with open(file_location, "wb") as f:
            f.write(encrypted_content)
        
        CURRENT_FILENAME = file.filename
        logger.info(f"File uploaded and encrypted: {file.filename}")
        
        # 2. DETECT TYPE (Simple Extension fallback since magic needs bytes)
        # For full security, we'd decrypt a small chunk in memory for magic, but extension is safe enough for V1
        ext = file.filename.split('.')[-1].lower()
        if ext in ['csv', 'xlsx', 'json', 'parquet']:
            file_type = ext
        else:
            # Try magic as fallback by decrypting first 2kb in memory
            try:
                header = security.decrypt_data(encrypted_content)[:2048]
                # Re-use detector logic if adapted, or valid fallback
                file_type = detect_file_type(file_location) # This might fail on encrypted file, so we default to ext
            except:
                pass
            if not file_type:
                 raise HTTPException(status_code=400, detail="Could not detect file type")
        
        # 3. LOAD (Loader handles decryption in memory)
        df = loader.load_file(file_location, file_type)
        if df is None:
            raise HTTPException(status_code=400, detail="Failed to load file content")

        # 4. CLEAN
        df = cleaner.clean_data(df)
        CURRENT_DATAFRAME = df
        
        # 5. REGISTER SQL
        sql_engine.register_table("uploaded_data", df)
        
        # 6. ANALYZE (GEMINI)
        columns = df.columns
        sample = df.head(3).to_dicts()
        
        try:
            analysis_text = agent.analyze_schema(file.filename, columns, sample)
            # 7. STORE RAG (Encrypted internally by RAG Engine)
            rag.add_memory(f"File: {file.filename}. Analysis: {analysis_text}")
        except Exception as ai_e:
            logger.error(f"AI Analysis Failed: {ai_e}")
            analysis_text = json.dumps({
                "summary": "AI Analysis Unavailable (Model Error). Data loaded and secured.",
                "queries": ["SELECT * FROM uploaded_data LIMIT 10"],
                "viz_config": {"chart_type": "bar", "x_axis": columns[0] if columns else "", "y_axis": ""}
            })
        
        return {
            "filename": file.filename,
            "rows": df.shape[0],
            "columns": columns,
            "analysis": analysis_text
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Upload Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run_sql/")
async def run_sql(query: str = Form(...)):
    try:
        data, error = sql_engine.run_query(query)
        if error:
            return {"error": error}
        return {"data": data}
    except Exception as e:
        logger.error(f"SQL Error: {e}")
        return {"error": "Internal Server Error"}

@app.post("/export_report/")
async def export_report(
    summary: str = Form(...), 
    queries: str = Form(...), 
    format: str = Form("pptx")
):
    try:
        query_list = queries.split(";") 
        
        if format == "docx":
            path = exporter.generate_docx(CURRENT_FILENAME, summary, query_list, "")
            filename = f"{CURRENT_FILENAME}_report.docx"
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        else:
            path = exporter.generate_pptx(CURRENT_FILENAME, summary, query_list, "")
            filename = f"{CURRENT_FILENAME}_report.pptx"
            media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            
        return FileResponse(path, filename=filename, media_type=media_type)
    except Exception as e:
        logger.error(f"Export Error: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {e}")

@app.post("/query/")
async def query_agent(query: str = Form(...), context: str = Form(None)):
    try:
        # 1. Retrieve RAG Context
        rag_info = rag.retrieve(query)
        
        # 2. Combine Contexts
        final_context = ""
        if context:
            final_context += f"--- CURRENT DATASET METADATA ---\n{context}\n\n"
        
        if rag_info:
            final_context += f"--- RELEVANT PAST MEMORY ---\n{rag_info}"
        
        # 3. Ask Gemini
        response = agent.chat_with_data(query, final_context)
        
        # 4. Log
        log_action("user_query", {"query": query, "context": final_context}, response)
        return {"response": response}
    
    except Exception as e:
        logger.error(f"Chat Error: {e}")
        return {"response": "I'm having trouble connecting to my brain right now. Please try again."}

@app.post("/train/")
async def run_training():
    try:
        learner = AILearner()
        result = learner.run_learning_cycle()
        return {"status": "success", "message": result}
    except Exception as e:
        logger.error(f"Training Error: {e}")
        return {"status": "error", "message": str(e)}