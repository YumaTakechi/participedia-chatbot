from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import os
from typing import List, Dict
from pydantic import BaseModel
import faiss
import pandas as pd
from faiss_search import faiss_search, format_faiss_results
from query_embedding import create_query_embedding


app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #TODO: Change "*" to frontend domain in production
    allow_credentials=True,
    allow_methods=["GET", "POST"]
)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))

# Check if the directory exists
if not os.path.exists(FRONTEND_DIR):
    raise RuntimeError(f"ERROR: Frontend directory not found at {FRONTEND_DIR}")

print(f"Serving frontend from: {FRONTEND_DIR}")

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class SearchRequest(BaseModel):
    user_query: str
    conversation_history: List[Dict[str, str]] = []

faiss_index = faiss.read_index("./case_index.faiss") 
cases_with_topics_df = pd.read_csv("./cases_with_topics.csv")

@app.get("/")
async def serve_chatbot():
    """Serve the chatbot frontend."""
    base_html_path = os.path.join(FRONTEND_DIR, "base.html")

    if not os.path.exists(base_html_path):
        print(f"ERROR: base.html not found at {base_html_path}")
        return {"error": "base.html not found"}

    return FileResponse(base_html_path)

# Serve favicon.ico
@app.get("/favicon.ico")
async def serve_favicon():
    favicon_path = os.path.join(FRONTEND_DIR, "favicon.ico")
    if not os.path.exists(favicon_path):
        raise HTTPException(status_code=404, detail="Favicon not found")
    return FileResponse(favicon_path)

@app.post("/search_cases")
async def search_cases(request: SearchRequest):
    try:
        # Include conversation history in the query
        full_query = request.user_query
        if request.conversation_history:
            full_query = " ".join([msg["message"] for msg in request.conversation_history]) + " " + request.user_query

        query_embedding = create_query_embedding(request.user_query)
        faiss_indices = faiss_search(query_embedding, , faiss_index)
        faiss_results = format_faiss_results(faiss_indices, cases_with_topics_df)

        #TODO: put this formating to format_faiss_results
        results = []
        for result in faiss_results:
                results.append(f'<a href="{result["url"]}" target="_blank">{result["title"]}</a>')

        return {
                "results": "<br><br>".join(results)
            }

    except Exception as e:
        print(f"ERROR: {e}")
        return {
            "error": "An error occurred while processing your request.",
            "details": str(e)
        }