from fastapi import FastAPI
from pydantic import BaseModel
import faiss
import pandas as pd
from faiss_search import faiss_search, format_faiss_results
from query_embedding import create_query_embedding


app = FastAPI()

class SearchRequest(BaseModel):
    user_query: str
    top_n: int

faiss_index = faiss.read_index("../case_index.faiss") 
cases_with_topics_df = pd.read_csv("../cases_with_topics.csv")

# TEST
# user_query = "I want to learn about cases related to elections in Canada"
# top_n = 1


# query_embedding = create_query_embedding(user_query)
# print(type(query_embedding))

# faiss_indices = faiss_search(query_embedding, top_n, faiss_index)
# print(type(faiss_indices))
# results = format_faiss_results(faiss_indices, cases_with_topics_df)

# print(type(results))

@app.get("/")
async def read_root():
    return {'Participedia Chatbot'}


@app.post("/search_cases")
async def search_cases(request: SearchRequest):
    query_embedding = create_query_embedding(request.user_query)
    faiss_indices = faiss_search(query_embedding, request.top_n, faiss_index)
    results = format_faiss_results(faiss_indices, cases_with_topics_df)
    # print(results)
    return results