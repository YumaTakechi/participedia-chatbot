from sentence_transformers import SentenceTransformer

sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

def create_query_embedding(user_query):
    query_embedding = sbert_model.encode([user_query]).astype("float32")
    return query_embedding
    
