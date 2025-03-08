from fastapi import FastAPI
from pydantic import BaseModel
from test_query_handler import UserQueryHandlerTest
from test_faiss_handler import FaissHandlerTest

app = FastAPI()

query_handler = UserQueryHandlerTest()
faiss_handler = FaissHandlerTest()

class QueryRequest(BaseModel):
    user_query: str
    top_n: int = 3


"""Test"""
# user_query = "I want to learn about cases related to elections in Canada"
# top_n = 1
# query_embedding = query_handler.generate_query_embedding(user_query)
# faiss_result = faiss_handler.retrieve_cases(query_embedding, top_n)

# print(faiss_result)

@app.post("/search_cases")
async def search_cases(request: QueryRequest):
    """
    FastAPI endpoint to retrieve similar cases.
    """
    query_embedding = query_handler.generate_query_embedding(request.user_query)
    faiss_result = faiss_handler.retrieve_cases(query_embedding, request.top_n)
    
    return faiss_result