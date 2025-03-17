from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from typing import List, Dict

from test_query_handler import UserQueryHandlerTest
from test_faiss_handler import FaissHandlerTest

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change "*" to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Define frontend directory
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../standalone_frontend'))

# Check if the directory exists
if not os.path.exists(FRONTEND_DIR):
    raise RuntimeError(f"❌ ERROR: Frontend directory not found at {FRONTEND_DIR}")

print(f"🔹 Serving frontend from: {FRONTEND_DIR}")

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Serve base.html at "/"
@app.get("/")
async def serve_chatbot():
    """Serve the chatbot frontend."""
    base_html_path = os.path.join(FRONTEND_DIR, "base.html")

    if not os.path.exists(base_html_path):
        print(f"❌ ERROR: base.html not found at {base_html_path}")
        return {"error": "base.html not found"}

    return FileResponse(base_html_path)

# Serve favicon.ico
@app.get("/favicon.ico")
async def serve_favicon():
    favicon_path = os.path.join(FRONTEND_DIR, "favicon.ico")
    if not os.path.exists(favicon_path):
        raise HTTPException(status_code=404, detail="Favicon not found")
    return FileResponse(favicon_path)

# Initialize query handlers
query_handler = UserQueryHandlerTest()
faiss_handler = FaissHandlerTest()

# Define request model with conversation history
class ChatContext(BaseModel):
    user_query: str
    conversation_history: List[Dict[str, str]] = []

# Chatbot API: Retrieve similar cases with context
@app.post("/search_cases")
async def search_cases(request: ChatContext):
    """
    FastAPI endpoint to retrieve similar cases with conversation context.
    """
    try:
        # Include conversation history in the query
        full_query = request.user_query
        if request.conversation_history:
            full_query = " ".join([msg["message"] for msg in request.conversation_history]) + " " + request.user_query

        # Generate query embedding and retrieve cases
        query_embedding = query_handler.generate_query_embedding(full_query)
        faiss_result = faiss_handler.retrieve_cases(query_embedding, top_n=5)

       # Format the results
        results = []
        for result in faiss_result:
            results.append(f'<a href="{result["url"]}" target="_blank">{result["title"]}</a>')

        return {
            "results": "<br><br>".join(results)
        }
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {
            "error": "An error occurred while processing your request.",
            "details": str(e)
        }

# Optional: Console-based chatbot interaction
def interactive_query_loop():
    while True:
        user_query = input("Enter your query (or type 'exit' to quit): ")

        if user_query.lower() == 'exit':
            print("Exiting the interactive query loop.")
            break

        top_n = 5
        query_embedding = query_handler.generate_query_embedding(user_query)
        faiss_result = faiss_handler.retrieve_cases(query_embedding, top_n)

        print(f"Results for your query '{user_query}':")
        print(faiss_result)

if __name__ == "__main__":
    import uvicorn
    from test_app.test_v1_app import app

    print("Starting FastAPI server...")
    # Start FastAPI server
    uvicorn.run("test_v1_app:app", host="0.0.0.0", port=8000, reload=True)