from sentence_transformers import SentenceTransformer
import numpy as np

sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

class UserQueryHandlerTest:
    def __init__(self):
        self.sbert_model = sbert_model
    
    def generate_query_embedding(self, user_query: str) -> np.ndarray:
        """
        Generates query embeddings using SBERT.
        
        :param user_query: str
        :return: np.ndarray
        """

        query_embedding = self.sbert_model.encode(user_query).astype("float32").reshape(1, -1)
        return query_embedding
    