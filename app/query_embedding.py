from sentence_transformers import SentenceTransformer

def create_query_embedding(user_query):
    sbert_model = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = sbert_model.encode([user_query]).astype("float32").tolist()
    return query_embedding
    
